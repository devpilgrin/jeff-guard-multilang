import pandas as pd, json, os, re

os.makedirs("data", exist_ok=True)

def norm(t):
    return re.sub(r"\s+", " ", str(t)).strip()

frames = {}
for split in ["train", "validation", "test"]:
    frames[split] = pd.read_parquet(f"raw/shieldlm/data/{split}-00000-of-00001.parquet")

sets = {s: set(frames[s].text.map(norm)) for s in frames}
print("overlap train/val:", len(sets["train"] & sets["validation"]))
print("overlap train/test:", len(sets["train"] & sets["test"]))
print("overlap val/test:", len(sets["validation"] & sets["test"]))

stats = {}
for split, df in frames.items():
    df = df.copy()
    df["_n"] = df.text.map(norm)
    before = len(df)
    df = df.drop_duplicates("_n")
    out = df.rename(columns={"label_binary": "label"})[["text", "label", "label_category", "label_intent", "source", "language"]]
    out = out.rename(columns={"label_category": "category", "label_intent": "intent"})
    path = f"data/{'val' if split == 'validation' else split}.jsonl"
    out.to_json(path, orient="records", lines=True, force_ascii=False)
    stats[path] = {
        "rows": len(out), "dropped_dups": before - len(out),
        "attack": int(out.label.sum()), "benign": int((out.label == 0).sum()),
        "categories": out.category.value_counts().to_dict(),
    }

ni = pd.concat([pd.read_parquet(f"raw/notinject/data/{s}-00000-of-00001.parquet") for s in ["train", "validation", "test"]])
ni_out = pd.DataFrame({"text": ni.prompt.map(norm), "label": 0, "category": "benign_hard_negative",
                       "intent": None, "source": "leolee99/NotInject", "language": "multi"})
ni_out.to_json("data/eval_overtrigger_notinject.jsonl", orient="records", lines=True, force_ascii=False)
stats["data/eval_overtrigger_notinject.jsonl"] = {"rows": len(ni_out), "benign": len(ni_out)}

te = pd.read_json("data/test.jsonl", lines=True)
ag = te[te.category == "indirect_injection"]
ag.to_json("data/eval_agentic_indirect.jsonl", orient="records", lines=True, force_ascii=False)
stats["data/eval_agentic_indirect.jsonl"] = {"rows": len(ag), "attack": int(ag.label.sum())}

print(json.dumps(stats, ensure_ascii=False, indent=1))
lens = pd.read_json("data/train.jsonl", lines=True).text.str.len()
print("train text chars: mean", int(lens.mean()), "p95", int(lens.quantile(.95)), "p99", int(lens.quantile(.99)), "max", lens.max())
