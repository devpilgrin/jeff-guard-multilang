#!/usr/bin/env bash
# Обучение guard-LoRA (r16, alpha 32 - конфиг эталонного mstrasser-guard)
# на нашем корпусе, по нативному рецепту firelex/jeff.
# Предусловия: prepare_train.py --kit отработал, чекпоинт Jeff v1.2 на диске.
# Запуск из ~/workspace/jeff-guard-multilang.
set -euo pipefail
cd ~/workspace/jeff-repo
export PATH="$HOME/.local/bin:$PATH"

DATA=~/workspace/jeff-guard-multilang/.temp/train_jeff/split
BASE=~/workspace/jeff-guard-multilang/.temp/raw/jeff-base   # Jeff-Qwen3.5-0.8B v1.2 + readout
RUN="guard-v3-$(date +%Y%m%d)"
export JEFF_EVENTS=~/workspace/jeff-guard-multilang/.temp/checkpoints/$RUN-events.jsonl
mkdir -p ~/workspace/jeff-guard-multilang/.temp/checkpoints

uv run --no-default-groups --extra lora --extra cuda jeff-train \
  --train "$DATA/train.jsonl" \
  --development "$DATA/development.jsonl" \
  --temperature "$DATA/calibration.jsonl" \
  --run "$RUN" \
  --output ~/workspace/jeff-guard-multilang/.temp/checkpoints \
  --initial-checkpoint "$BASE" \
  --base-model Qwen/Qwen3.5-0.8B \
  --revision 2fc06364715b967f1860aea9cf38778875588b17 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0 \
  --epochs 1 \
  --batch-size 32 \
  --effective-batch-size 256 \
  --lr 1e-4 \
  --patience 3

# После: адаптер в ~/workspace/jeff-guard-multilang/.temp/checkpoints/$RUN/
# Слияние в единый чекпоинт: merge_guard.py (поправить пути ADAPT/OUT).
