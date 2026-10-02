# 01. Датасет

Корпус для обучения и оценки детектора промпт-инъекций. Версия v3 (02.10.2026):
**103 146 строк** обучающих + 8 122 val + 8 121 test + 14 eval-наборов.

## Схема записи (JSONL)

```json
{"text": "...", "label": 1, "category": "direct_injection",
 "intent": null, "source": "spml/chatbot-prompt-injection", "language": "en"}
```

- `label`: 0 = benign, 1 = атака
- `category`: `benign` | `direct_injection` | `indirect_injection` | `jailbreak`
- `source`: датасет-происхождение (для переводов - суффикс `/ru`, `/zh`...)
- `language`: en/ru/zh/de/fr/es/ja/ko/pt/it/ar/hi/tr

## Состав train (v2 + переводы)

Ядро v2 (82 791 строка) - ShieldLM (11 источников: SPML, xTRam1/safe-guard,
deepset, yanismiraoui, Harelix, InjecAgent base, TrustAIRLab in-the-wild,
jackhhao, JBB-Behaviors, chatbot-instruction-prompts) плюс расширения:

| Источник | Строк | Что дает |
|-|-|-|
| InjecAgent enhanced (UIUC) | 1 054 + clean | агентский indirect: пары атака/чистый из одного кейса |
| BIPIA (Microsoft) | 1 200 + 1 200 | indirect в email/таблицах/коде (методология статьи) |
| LLMail-Inject fp_tests | 160 | benign-письма-ловушки (hard negatives) |
| neuralchemy core | 5 168 | 29 категорий: encoding, token_smuggling, rag_poisoning |
| sentinel (Chgdz) | 6 359 | Unicode/обфускация |
| S-Labs | 15 124 | короткие бинарные |
| jayavibhav | 11 656 | шаблонные jailbreak (доза из 261K) |
| dolly-15k | 2 943 | реальные пользовательские инструкции (benign) |

Переведенная часть (20 355 строк, ornith-1.5-35b локально, инструкция
в user-реплике - сборка игнорирует system-роль):

- **ru: 12 040** (7 606 атак / 4 434 benign)
- multi 8 315: zh 1 700, fr 1 085, es 1 065, ja 907, de 825, ko 695, pt 646,
  ar 468, hi 370, tr 294, it 260
- переведена стратифицированная смесь (34% benign) - защита от ложного
  правила "не-английский = атака"; ~11.5% строк потеряно на отказах
  переводчика (зафиксировано в `.temp/dead_archive`)

Категории в train: direct 27 318+ / jailbreak 8 784+ / indirect 3 052+ /
benign 43 637+ (с переводами пропорции сохранены).

## Eval-наборы

| Набор | Строк | Назначение |
|-|-|-|
| test.jsonl | 8 121 | финальная оценка EN (заморожен с v1) |
| val.jsonl | 8 122 | валидация (заморожена) |
| eval_ru/zh/de/fr/es/ja | ~90-270 каждый | языковые срезы (перевод test) |
| eval_agentic_indirect | 158 | InjecAgent base - приоритетный сценарий |
| eval_overtrigger_notinject | 339 | hard negatives - FPR на стоп-словах |
| eval_neuralchemy | 942 | 29 категорий атак |
| eval_sentinel | 5 161 | обфускация/Unicode |
| eval_hometurf_gandalf/mosscap | 888+1 000 | "домашние" наборы эталонного guard |

## Гигиена

- Глобальная exact-дедупликация по нормализованному тексту на каждой сборке;
  187 потенциальных утечек в eval отсечено при v2; 5 строк утечки
  train↔test найдено в самом ShieldLM и устранено.
- Split для обучения - jeff-kit по family=источнику (leave-one-source-out).
- **Известный остаточный риск:** near-дубли (85% 5-gram) между train и
  внутренними партициями kit (~4K пар, ~0.4%) - обнаружены jeff-kit
  leak-check; метрики на test.jsonl потенциально верхняя оценка.
  См. `.temp/train_jeff/leaks.json` и docs/03-results.md.
- Отвергнутые источники: DAXAAI v8 (шумные метки), XSTest/qualifire (gated),
  hackaprompt (соревновательный формат), LLMail levels (нет почтовой разметки).

## Лицензии источников

ShieldLM и входящие (SPML CC-BY-4.0, xTRam1 Apache-2.0, deepset Apache-2.0,
TrustAIRLab CC-BY-NC-SA-4.0 ⚠ исследовательское использование, InjecAgent MIT,
jackhhao MIT, JBB MIT), neuralchemy Apache-2.0, S-Labs MIT, dolly CC-BY-SA-3.0,
NotInject MIT, BIPIA MIT, LLMail-Inject MIT, Gandalf MIT.
Перед коммерческим использованием проверить CC-BY-NC-SA (TrustAIRLab) и
share-alike (dolly) компоненты.
