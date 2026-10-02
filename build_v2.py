"""Корпус v2: v1 + агентский indirect (InjecAgent enhanced, BIPIA), hard negatives
(LLMail fp), разнообразие (neuralchemy, sentinel, slabs, jayavibhav), benign (dolly).

Правила: val/test v1 заморожены; новые данные только в train_v2; дедупликация
против v1 train/val/test и всех eval-наборов; новые eval-файлы из чужих test-сплитов.
"""
import json, random, re, ast
import pandas as pd

random.seed(42)
def norm(t): return re.sub(r"\s+", " ", str(t)).strip()
def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]
def dump(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

# --- защищенные от утечки множества (val/test v1 + все eval) ---
protected = set()
for f in ["data/val.jsonl", "data/test.jsonl", "data/eval_overtrigger_notinject.jsonl",
          "data/eval_agentic_indirect.jsonl", "data/eval_hometurf_gandalf.jsonl",
          "data/eval_hometurf_mosscap.jsonl"]:
    protected |= {norm(r["text"]) for r in jl(f)}
seen = {norm(r["text"]) for r in jl("data/train.jsonl")}
print(f"protected: {len(protected)}, v1 train: {len(seen)}")

leaks = [0]
def add(rows, source, stats):
    out = []
    for r in rows:
        t = norm(r["text"])
        if not t or len(t) < 8: continue
        if t in seen: continue
        if t in protected:
            leaks[0] += 1
            continue
        seen.add(t)
        r["text"] = t
        r["source"] = source
        r.setdefault("language", "en")
        r.setdefault("intent", None)
        out.append(r)
    stats[source] = len(out)
    return out

new_rows, stats = [], {}

# 1. InjecAgent enhanced: пара атака/чистый из одного кейса
for kind, fn in [("dh", "test_cases_dh_enhanced.json"), ("ds", "test_cases_ds_enhanced.json")]:
    cases = json.load(open(f"raw/gh-InjecAgent/data/{fn}"))
    atk, clean = [], []
    for c in cases:
        head = f"User task: {c['User Instruction']}\n\n[Tool: {c['User Tool']} output]\n"
        if c.get("Tool Response"):
            atk.append({"text": head + str(c["Tool Response"]), "label": 1, "category": "indirect_injection"})
        if c.get("Tool Response Template"):
            clean.append({"text": head + str(c["Tool Response Template"]), "label": 0, "category": "benign"})
    new_rows += add(atk, f"injecagent/enhanced_{kind}", stats)
    new_rows += add(clean, f"injecagent/clean_{kind}", stats)

# 2. BIPIA: чистые контексты + внедрение attack-строк (методология статьи)
attacks = []
for f in ["text_attack_train.json", "text_attack_test.json", "code_attack_train.json", "code_attack_test.json"]:
    d = json.load(open(f"raw/gh-BIPIA/benchmark/{f}"))
    for cat, items in d.items():
        attacks += [str(i) for i in items]
print("BIPIA attack strings:", len(attacks))
bipia_clean, bipia_atk = [], []
for dom in ["email", "table", "code"]:
    for split in ["train", "test"]:
        for line in open(f"raw/gh-BIPIA/benchmark/{dom}/{split}.jsonl"):
            r = json.loads(line)
            ctx, q = norm(r["context"]), norm(r.get("question", ""))
            bipia_clean.append({"text": f"{ctx}\n{q}", "label": 0, "category": "benign"})
            a = random.choice(attacks)
            pos = random.choice(["start", "middle", "end"])
            if pos == "start": t = f"{a}\n{ctx}\n{q}"
            elif pos == "end": t = f"{ctx}\n{a}\n{q}"
            else:
                mid = len(ctx) // 2
                t = f"{ctx[:mid]}\n{a}\n{ctx[mid:]}\n{q}"
            bipia_atk.append({"text": t, "label": 1, "category": "indirect_injection"})
new_rows += add(bipia_clean, "bipia/clean", stats)
new_rows += add(bipia_atk, "bipia/attacked", stats)

# 3. LLMail fp_tests - benign письма-ловушки
fp = json.load(open("raw/gh-LLMail-Inject-Challenge/src/agent/data/fp_tests.json"))
new_rows += add([{"text": e, "label": 0, "category": "benign"} for e in fp["emails"]], "llmail/fp", stats)

# 4. neuralchemy core (train+val -> train; test -> eval)
cat_map = {"direct_injection": "direct_injection", "jailbreak": "jailbreak",
           "encoding": "direct_injection", "token_smuggling": "direct_injection",
           "system_manipulation": "direct_injection", "persona_replacement": "direct_injection",
           "adversarial": "direct_injection", "training_extraction": "direct_injection",
           "rag_poisoning": "indirect_injection", "agent_manipulation": "indirect_injection",
           "benign": "benign", "edge_case": "benign"}
def nc_rows(split):
    df = pd.read_parquet(f"raw/neuralchemy/core/{split}-00000-of-00001.parquet")
    return [{"text": t, "label": int(l), "category": cat_map.get(c, "direct_injection" if l else "benign")}
            for t, l, c in zip(df.text, df.label, df.category)]
new_rows += add(nc_rows("train") + nc_rows("validation"), "neuralchemy/core", stats)
dump([{**r, "source": "neuralchemy/core-test"} for r in nc_rows("test")], "data/eval_neuralchemy.jsonl")

# 5. sentinel (вердикт из assistant JSON; train+val сэмпл -> train, test -> eval)
def sentinel_rows(split):
    df = pd.read_parquet(f"raw/sentinel/data/{split}-00000-of-00001.parquet")
    out = []
    for _, r in df.iterrows():
        try:
            v = json.loads(str(r.assistant))
            lab = 1 if v.get("threat_detected") else 0
        except Exception:
            continue
        out.append({"text": str(r.user), "label": lab, "category": "direct_injection" if lab else "benign"})
    return out
sent = sentinel_rows("train") + sentinel_rows("validation")
sa = [r for r in sent if r["label"] == 1]; sb = [r for r in sent if r["label"] == 0]
random.shuffle(sa); random.shuffle(sb)
new_rows += add(sa[:6000] + sb[:6000], "sentinel/unicode", stats)
dump([{**r, "source": "sentinel/test"} for r in sentinel_rows("test")], "data/eval_sentinel.jsonl")

# 6. slabs (короткие чистые бинарные)
sl = pd.concat([pd.read_csv(f"raw/slabs/data/{s}.csv") for s in ["train", "validation", "test"]])
new_rows += add([{"text": t, "label": int(l), "category": "direct_injection" if l else "benign"}
                 for t, l in zip(sl.text, sl.label)], "slabs", stats)

# 7. jayavibhav: сэмпл (129K атак шаблонных - дозированно)
jv = pd.read_parquet("raw/jayavibhav/data/train-00000-of-00001.parquet")
ja = jv[jv.label == 1].sample(8000, random_state=42); jb = jv[jv.label == 0].sample(4000, random_state=42)
new_rows += add([{"text": t, "label": 1, "category": "jailbreak"} for t in ja.text], "jayavibhav/attacks", stats)
new_rows += add([{"text": t, "label": 0, "category": "benign"} for t in jb.text], "jayavibhav/benign", stats)

# 8. dolly benign (реальные пользовательские инструкции)
dl = pd.read_json("raw/dolly/databricks-dolly-15k.jsonl", lines=True).sample(3000, random_state=42)
new_rows += add([{"text": f"{i}\n{c}" if str(c).strip() else str(i), "label": 0, "category": "benign"}
                 for i, c in zip(dl.instruction, dl.context)], "dolly/benign", stats)

# --- сборка train_v2 ---
v1 = jl("data/train.jsonl")
train_v2 = v1 + new_rows
random.shuffle(train_v2)
dump(train_v2, "data/train_v2.jsonl")

print(f"\nutechek в eval отсечено: {leaks[0]}")
print(json.dumps(stats, indent=1))
tot_a = sum(1 for r in train_v2 if r["label"] == 1); tot_b = len(train_v2) - tot_a
print(f"train_v2: {len(train_v2)} строк (было {len(v1)}, +{len(new_rows)}); атак {tot_a}, benign {tot_b}")
cats = {}
for r in train_v2: cats[r["category"]] = cats.get(r["category"], 0) + 1
print("категории:", cats)
