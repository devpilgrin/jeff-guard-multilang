"""Слияние Jeff-Qwen3.5-0.8B v1.2 + guard LoRA в единый чекпоинт.

Ручной merge на уровне safetensors: W' = W + (alpha/r) * B @ A.
Не требует transformers (архитектура Gated DeltaNet слишком свежая).
"""
import json, shutil, os
import torch
from safetensors.torch import load_file, save_file

BASE = "raw/jeff-base"
ADAPT = "raw/jeff-guard"
OUT = os.path.expanduser("~/workspace/jeff-guard-merged")
os.makedirs(OUT, exist_ok=True)

cfg = json.load(open(f"{ADAPT}/adapter_config.json"))
r, alpha = cfg["r"], cfg["lora_alpha"]
scale = alpha / r
print(f"LoRA r={r} alpha={alpha} scale={scale}")

base = load_file(f"{BASE}/model.safetensors")
adapt = load_file(f"{ADAPT}/adapter_model.safetensors")
print(f"base tensors: {len(base)}, adapter tensors: {len(adapt)}")

# Группировка lora_A/lora_B по целевому весу
pairs = {}
for k in adapt:
    stem = k.replace("base_model.model.", "").rsplit(".lora_", 1)
    if len(stem) != 2:
        print("неожиданный ключ:", k)
        continue
    tgt, ab = stem
    pairs.setdefault(tgt, {})[ab] = k

merged, deltas = dict(base), []
missing = []
for tgt, ab in pairs.items():
    wkey = tgt + ".weight"
    if wkey not in base:
        missing.append(wkey)
        continue
    A = adapt[ab["A.weight"]].to(torch.float32)
    B = adapt[ab["B.weight"]].to(torch.float32)
    delta = (B @ A) * scale
    W = base[wkey]
    assert W.shape == delta.shape, f"shape mismatch {wkey}: {W.shape} vs {delta.shape}"
    deltas.append((wkey, delta.norm().item(), W.norm().item()))
    merged[wkey] = (W.to(torch.float32) + delta).to(W.dtype)

print(f"слито модулей: {len(deltas)}, не найдено в базе: {len(missing)}")
for m in missing:
    print("  MISSING:", m)

# Сводка по масштабу правок
deltas.sort(key=lambda x: -x[1] / max(x[2], 1e-9))
print("топ-5 по относительной правке (|delta|/|W|):")
for k, dn, wn in deltas[:5]:
    print(f"  {dn/wn:8.4%}  {k}")
print("мин-5:")
for k, dn, wn in deltas[-5:]:
    print(f"  {dn/wn:8.4%}  {k}")

save_file(merged, f"{OUT}/model.safetensors", metadata={"format": "pt"})

# Базовые конфиги + головa и калибровка от guard
for f in ["config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja", "processor_config.json"]:
    shutil.copy(f"{BASE}/{f}", f"{OUT}/{f}")
for f in ["readout.safetensors", "decision_config.json", "calibration.jsonl"]:
    shutil.copy(f"{ADAPT}/{f}", f"{OUT}/{f}")

total = os.path.getsize(f"{OUT}/model.safetensors") / 1e9
print(f"готово: {OUT}/model.safetensors ({total:.2f} ГБ) + readout + конфиги")
