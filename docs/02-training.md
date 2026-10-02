# 02. Обучение

Рецепт воспроизводит метод авторов Jeff (firelex/jeff, форк AutoJev):
доменная LoRA поверх decision-модели Jeff + fitted temperature.

## Конфигурация

| Параметр | Значение |
|-|-|
| База | Jeff-Qwen3.5-0.8B **v1.2** (Qwen3.5-0.8B, гибрид Gated DeltaNet + attention) |
| Метод | LoRA (PEFT), r=16, alpha=32, dropout=0 |
| Target modules | все проекции: q/k/v/o, in_proj_qkv, in_proj_z, out_proj (DeltaNet), MLP gate/up/down |
| Обучаемых параметров | 10 484 736 (~1.3% от 0.8B) |
| Readout | decision head от базы, дообучается вместе с адаптером |
| Данные | 164 946 jeff-записей (2 на строку корпуса: noul attack + choice kind) |
| Split | jeff-kit по family=источнику (leave-one-source-out); dev 8%, calibration 10% |
| Оптимизатор | AdamW, lr 1e-4, weight decay 0.01, effective batch 256 |
| Эпохи | 1 (645 шагов), checkpoint selection по development loss |
| Выбранный шаг | **320 / 645** |
| Калибровка | fitted temperature на calibration-фолде (штатно в jeff-train) |
| Железо | RTX 4090 48 ГБ, ~7.1 ч (с замедлением: reference-ядро causal_conv1d; с пакетом `causal-conv1d` ожидается в разы быстрее) |

Run ID: `guard-v3-20261002`. Полный provenance (хэши данных, артефакта,
коммита кода) - в `.temp/checkpoints/guard-v3-20261002-events.jsonl`.

## Вопросы (формулировки часть модели)

State: `{application, source, text}`. application = "An orchestration system
that reads incoming user tasks and assigns them to specialised AI agents.";
source = "user message" | "tool result" (для indirect). Вопросы `attack`
(noul) и `kind` (choice, 5 классов) - дословно в `compare_guards.py` /
`model/decision_config.json`; калибровка подогнана под эти формулировки.

## Воспроизведение

```bash
# 1. корпус (если пересобирать): build_dataset.py, build_v2.py (источники с HF/GitHub)
# 2. переводы: translate_ru.py train, translate_multi.py train (LM Studio, OpenAI API)
# 3. конвертация + проверки
.venv/bin/python prepare_train.py --kit     # jeff-формат, check-rows, split, leak-check
# 4. обучение
bash train_guard_lora.sh                    # run -> checkpoints/<run>/selected
# 5. слияние (опционально, для единого чекпоинта)
.venv/bin/python merge_ours.py              # -> ~/workspace/jeff-ours-merged
```

Зависимости тренера: репозиторий firelex/jeff, `uv sync --no-default-groups
--extra lora --extra cuda`. Обязательные env: `JEFF_EVENTS` (журнал событий),
сверка `--base-model Qwen/Qwen3.5-0.8B --revision 2fc063...` с чекпоинтом.

## Известные огрехи процесса (для v4)

1. Leak-check нашел ~4K near-дублей train↔внутренние партиции kit
   (одни и те же атаки из разных датасетов): development-фолд слегка
   оптимистичен, чекпоинт мог быть выбран не оптимально.
2. Hard negatives (NotInject-стиль) почти отсутствуют в train -
   причина FPR 0.23 на eval_overtrigger_notinject.
3. Mosscap не входил в корпус - recall 0.59 на "домашнем" наборе эталона.
4. `causal-conv1d` не был установлен - ~2-4x потеря скорости на DeltaNet-слоях.
