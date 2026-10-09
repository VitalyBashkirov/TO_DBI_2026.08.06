# DS_131 — Отчёт: устранение invalid escape sequence

## Итог

14 invalid escape sequence устранены в 6 файлах. Все строки с
Windows-путями (`\AI_IN`, `\AI_OUT`, `\DS_STANDARD`, `F:\TO_DBI`)
переведены в raw-string. ast.parse warnings: 0.

## Изменения

| Файл | Строки | Правка |
|------|--------|--------|
| SRC\fixer\code_fixer.py | 2403 | `"""` -> `r"""` |
| SRC\ai_exchange.py | 674, 683 | `'\|'`->`r'\|'`; `"""`->`r"""` |
| SRC\gui_app.py | 1238, 1289, 5320, 5407, 5409, 5417, 5531 | `"""`->`r"""`, `f"`->`rf"`, `"`->`r"` |
| tools\ai_local_worker.py | 865, 866 | `help='` -> `help=r'` |
| tools\check_standard.py | 2 | `"""` -> `r"""` |
| tools\explain_log.py | 2 | `"""` -> `r"""` |

## Побочный инцидент

На однострочных docstring gui_app.py L1238, L1289, L5531
`.Replace('"""', 'r"""')` заменил ОБА `"""` — открывающее и закрывающее.
Получилось `r"""...AI_OUT.r"""`. Семантическая порча: docstring содержал
`.r` в конце. Обнаружено при проверке размера (gui_app.py +10 B вместо +8 B).
Исправлено повторным блоком: `.Replace('.r"""', '."""')`.
Итоговый размер gui_app.py = 347 146 (+7 B — ровно 7 букв `r`).

## Проверки

- ast.parse warnings: **0** (было 14).
- py_compile × 6: exit=0.
- import gui_app, check_standard, explain_log: OK.
- ai_local_worker.py --check: OK.
- pytest: 65 passed.
- BOM: все 6 — False.

## Урок N

`.Replace` в PowerShell (и в Python) заменяет ВСЕ вхождения подстроки.
При правке docstring `"""..."""` на одной строке — `.Replace('"""', 'r"""')`
меняет И открывающую, И закрывающую кавычку. Нужно либо ограничить
контекст (`.Replace('    """', '    r"""')` — с отступом), либо
использовать `.Substring`/индексы, либо явно править только первое
вхождение.

## Бэкапы

`*.bak_ds131` для 6 файлов (ignored, `*.bak_*`).