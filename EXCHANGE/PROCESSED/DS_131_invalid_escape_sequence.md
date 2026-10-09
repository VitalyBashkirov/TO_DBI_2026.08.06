# DS_131 — Устранение invalid escape sequence в 6 файлах

## Контекст

- Проект: TO_DBI. Ветка: feature/dockerization.
- База: f8c1c20 (DS_130).
- Цель: устранить DeprecationWarning/SyntaxWarning "invalid escape sequence"
  в строковых литералах (не raw) — там, где Windows-пути содержат `\X`.
- Приоритет: НИЗКИЙ (косметика, но при `-W error` — блокер).

## Диагноз

`ast.parse` выявил 14 hits в 6 файлах:

| Файл | Строка | Escape |
|------|--------|--------|
| SRC\fixer\code_fixer.py | 2417 (в docstring L2403-2422) | `\T` от `F:\TO_DBI` |
| SRC\ai_exchange.py | 674 | `\|` |
| SRC\ai_exchange.py | 683 | `\O` от `\OUTBOX` |
| SRC\gui_app.py | 1238, 1289, 5320, 5407, 5409, 5417, 5531 | `\A` от `\AI_IN`/`\AI_OUT` |
| tools\ai_local_worker.py | 865, 866 | `\A` от `\AI_IN`/`\AI_OUT` |
| tools\check_standard.py | 4 (в docstring L2-9) | `\D` от `\DS_STANDARD` |
| tools\explain_log.py | 4 (в docstring L2-8) | `\ ` и `\b` |

## Что сделано

Все строки с `\X` переведены в raw-string (`r"..."`, `r"""..."""`, `rf"..."`,
`help=r'...'`). Содержимое НЕ изменено — только добавлена буква `r`.

- code_fixer.py L2403: `"""` -> `r"""`
- ai_exchange.py L674: `'\|'` -> `r'\|'`; L683: `"""` -> `r"""`
- gui_app.py: 1238,1289,5320,5531: `"""` -> `r"""`; 5407: `f"` -> `rf"`;
  5409,5417: `"` -> `r"`
- ai_local_worker.py L865,866: `help='` -> `help=r'`
- check_standard.py L2: `"""` -> `r"""`
- explain_log.py L2: `"""` -> `r"""`

## Инцидент (закрыт)

`.Replace('"""', 'r"""')` на однострочных docstring (L1238, L1289, L5531
в gui_app.py) заменил ОБА вхождения — открывающее И закрывающее:
`r"""...AI_OUT.r"""`. Исправлено `.Replace('.r"""', '."""')`.

## Проверки

- ast.parse warnings: 0 (было 14).
- py_compile × 6: exit=0.
- import gui_app: OK.
- import check_standard, import explain_log: OK.
- ai_local_worker.py --check: OK (ollama available).
- pytest: 65 passed.
- BOM: все 6 — False.

## Бэкапы (ignored)

- SRC\fixer\code_fixer.py.bak_ds131
- SRC\ai_exchange.py.bak_ds131
- SRC\gui_app.py.bak_ds131
- tools\ai_local_worker.py.bak_ds131
- tools\check_standard.py.bak_ds131
- tools\explain_log.py.bak_ds131