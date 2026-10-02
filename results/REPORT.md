# Матрица сравнения гардов

Метрики: acc / recall / FPR (порог 0.5), kind - точность типа атаки. n - валидных ответов.

## core

| set | jeff+guard(merged) | jeff+guard(adapter) | jeff+our-lora(adapter) | jeff+our-lora(merged) | kev-0.8b |
|-|-|-|-|-|-|
| test | a 0.85 r 0.66 f 0.044, kind 0.38 (8102) | a 0.85 r 0.66 f 0.043, kind 0.38 (8100) | a 0.99 r 0.99 f 0.007, kind 0.95 (8099) | a 0.99 r 0.98 f 0.007, kind 0.95 (8102) | a 0.68 r 0.62 f 0.289, kind 0.21 (8121) |

## lang

| set | jeff+guard(merged) | jeff+guard(adapter) | jeff+our-lora(adapter) | jeff+our-lora(merged) | kev-0.8b |
|-|-|-|-|-|-|
| eval_ru | a 0.68 r 0.51 f 0.000, kind 0.32 (269) | a 0.69 r 0.52 f 0.000, kind 0.32 (269) | a 0.97 r 0.98 f 0.032, kind 0.89 (268) | a 0.97 r 0.98 f 0.032, kind 0.89 (268) | a 0.70 r 0.64 f 0.191, kind 0.18 (269) |
| eval_zh | a 0.82 r 0.75 f 0.062, kind 0.49 (87) | a 0.82 r 0.75 f 0.062, kind 0.49 (87) | a 0.98 r 0.96 f 0.000, kind 0.89 (87) | a 0.98 r 0.96 f 0.000, kind 0.89 (87) | a 0.78 r 0.82 f 0.281, kind 0.22 (87) |
| eval_de | a 0.68 r 0.62 f 0.143, kind 0.43 (82) | a 0.68 r 0.62 f 0.143, kind 0.43 (82) | a 1.00 r 1.00 f 0.000, kind 0.92 (82) | a 1.00 r 1.00 f 0.000, kind 0.92 (82) | a 0.68 r 0.70 f 0.381, kind 0.21 (82) |
| eval_fr | a 0.67 r 0.47 f 0.027, kind 0.25 (96) | a 0.67 r 0.47 f 0.027, kind 0.24 (96) | a 0.96 r 0.97 f 0.054, kind 0.90 (96) | a 0.96 r 0.97 f 0.054, kind 0.90 (96) | a 0.72 r 0.76 f 0.351, kind 0.29 (96) |
| eval_es | a 0.71 r 0.56 f 0.030, kind 0.34 (92) | a 0.71 r 0.56 f 0.030, kind 0.34 (92) | a 0.98 r 0.97 f 0.000, kind 0.86 (92) | a 0.98 r 0.97 f 0.000, kind 0.86 (92) | a 0.75 r 0.75 f 0.242, kind 0.22 (92) |
| eval_ja | a 0.63 r 0.42 f 0.000, kind 0.33 (87) | a 0.63 r 0.42 f 0.000, kind 0.33 (87) | a 0.99 r 0.98 f 0.000, kind 0.89 (87) | a 0.99 r 0.98 f 0.000, kind 0.91 (87) | a 0.63 r 0.58 f 0.281, kind 0.25 (87) |

## special

| set | jeff+guard(merged) | jeff+guard(adapter) | jeff+our-lora(adapter) | jeff+our-lora(merged) | kev-0.8b |
|-|-|-|-|-|-|
| eval_agentic_indirect | a 0.35 r 0.35 f 0.000, kind 0.05 (158) | a 0.35 r 0.35 f 0.000, kind 0.05 (158) | a 1.00 r 1.00 f 0.000, kind 1.00 (158) | a 1.00 r 1.00 f 0.000, kind 1.00 (158) | a 0.87 r 0.87 f 0.000, kind 0.22 (158) |
| eval_overtrigger_notinject | a 0.81 r 0.00 f 0.186 (338) | a 0.82 r 0.00 f 0.180 (338) | a 0.77 r 0.00 f 0.234 (338) | a 0.77 r 0.00 f 0.231 (338) | a 0.82 r 0.00 f 0.180 (339) |
| eval_neuralchemy | a 0.88 r 0.83 f 0.039, kind 0.67 (939) | a 0.88 r 0.83 f 0.041, kind 0.68 (939) | a 0.96 r 0.97 f 0.046, kind 0.90 (940) | a 0.96 r 0.97 f 0.046, kind 0.90 (940) | a 0.82 r 0.78 f 0.115, kind 0.33 (942) |
| eval_sentinel | a 0.76 r 0.68 f 0.000, kind 0.55 (5150) | a 0.76 r 0.69 f 0.000, kind 0.56 (5148) | a 0.98 r 0.97 f 0.000, kind 0.95 (5147) | a 0.98 r 0.97 f 0.000, kind 0.95 (5150) | a 0.71 r 0.62 f 0.005, kind 0.36 (5161) |
| eval_hometurf_gandalf | a 1.00 r 1.00 f 0.000, kind 1.00 (886) | a 1.00 r 1.00 f 0.000, kind 1.00 (886) | a 1.00 r 1.00 f 0.000, kind 1.00 (886) | a 1.00 r 1.00 f 0.000, kind 1.00 (884) | a 0.67 r 0.67 f 0.000, kind 0.28 (888) |
| eval_hometurf_mosscap | a 0.79 r 0.79 f 0.000, kind 0.74 (998) | a 0.79 r 0.79 f 0.000, kind 0.74 (998) | a 0.59 r 0.59 f 0.000, kind 0.56 (998) | a 0.59 r 0.59 f 0.000, kind 0.56 (996) | a 0.49 r 0.49 f 0.000, kind 0.06 (1000) |
