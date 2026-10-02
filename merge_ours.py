"""Слияние Jeff v1.2 + наша guard-LoRA (checkpoints/selected) в единый чекпоинт.
Standalone-копия merge_guard.py с путями под наш адаптер и правкой decision_config."""
import json, shutil, os
import torch
from safetensors.torch import load_file, save_file

BASE = ".temp/raw/jeff-base"
ADAPT = "model"
OUT = os.path.expanduser("~/workspace/jeff-ours-merged")
os.makedirs(OUT, exist_ok=True)

cfg = json.load(open(f"{ADAPT}/adapter_config.json"))
r, alpha = cfg["r"], cfg["lora_alpha"]
scale = alpha / r
print(f"LoRA r={r} alpha={alpha} scale={scale}")

base = load_file(f"{BASE}/model.safetensors")
adapt = load_file(f"{ADAPT}/adapter_model.safetensors")
print(f"base tensors: {len(base)}, adapter tensors: {len(adapt)}")

pairs = {}
for k in adapt:
    stem = k.replace("base_model.model.", "").rsplit(".lora_", 1)
    if len(stem) != 2:
        continue
    tgt, ab = stem
    pairs.setdefault(tgt, {})[ab] = k

merged, missing, n = dict(base), [], 0
for tgt, ab in pairs.items():
    wkey = tgt + ".weight"
    if wkey not in base:
        missing.append(wkey)
        continue
    A = adapt[ab["A.weight"]].to(torch.float32)
    B = adapt[ab["B.weight"]].to(torch.float32)
    W = base[wkey]
    merged[wkey] = (W.to(torch.float32) + (B @ A) * scale).to(W.dtype)
    n += 1
print(f"слито: {n}, не найдено: {len(missing)}")

save_file(merged, f"{OUT}/model.safetensors", metadata={"format": "pt"})
for f in ["config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja", "processor_config.json"]:
    shutil.copy(f"{BASE}/{f}", f"{OUT}/{f}")
for f in ["readout.safetensors", "decision_config.json"]:
    shutil.copy(f"{ADAPT}/{f}", f"{OUT}/{f}")

cfgp = f"{OUT}/decision_config.json"
d = json.load(open(cfgp))
d.pop("adapter", None)
d.pop("initial_artifact", None)
d.setdefault("provenance", {})["merged_from"] = "Jeff v1.2 + guard-v3-20261002 LoRA (safetensors merge)"
json.dump(d, open(cfgp, "w"), indent=2)
print("готово:", OUT)
