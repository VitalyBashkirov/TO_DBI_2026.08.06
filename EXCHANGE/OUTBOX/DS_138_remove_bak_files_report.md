# DS_138 — Удаление 26 `.bak_` в SRC. Отчёт

**Дата:** 2026-10-09
**Чат:** 30
**Автор DS:** DeepSeek
**Пользователь:** Vitaly
**Тип:** Гигиена (low risk)
**Статус:** ✅ Выполнен

## Причина

В `SRC\` накопились 26 файлов `.bak_*` от правок DS_134…DS_137 и более ранних
серий. Файлы не попадают в git (ignored по `*.bak_*`), но захламляют рабочее
дерево и затрудняют навигацию.

## Действие

Рекурсивное удаление всех `*.bak_*` в `SRC\` через один PS-блок
(`Remove-Item -LiteralPath ... -Force` с проверкой ошибок на каждом файле).

## Файлы (26)

gui_app.py.bak_blockB1/B2/C1/C2/C3/F/G/G2 (8)
gui_app.py.bak_ds134/ds134b/ds135/ds135mark/ds135_2d (5)
gui_app.py.bak_ds136/ds136B/ds136fix/ds136fix2 (4)
gui_app.py.bak_ds137 (1)
gui_app.py.bak_finish/return/tooltip (3)
settings.json.bak_ds134 (1)
analyzer/scanner.py.bak_ds135/ds135mark (2)
fixer/code_fixer.py.bak_ds135_2 (1)
tests/test_ds133_buttons_state.py.bak_ds136a (1)

**Итого:** 26 файлов, ≈ 7.5 МБ.

## Результат

| Параметр | Ожидание | Факт |
|----------|----------|------|
| Найдено ДО | 26 | 26 |
| Удалено | 26 | 26 |
| Ошибок удаления | 0 | 0 |
| Найдено ПОСЛЕ | 0 | 0 |
| git status | clean, sync | `## feature/dockerization...origin/feature/dockerization` |
| pytest | 77 passed | exit=0 |
| DS_133 script | 18/18 PASSED | 18/18 PASSED |

## Проверки

- `ast.parse` не требуется (Python-код не менялся).
- pytest — 77 passed.
- DS_133 script — 18/18 PASSED.
- git status — clean, синхронизирован с origin.

## Откат

Не требуется. Содержимое .bak_ устарело; актуальные версии — в git-истории
(коммиты DS_134…DS_137).

## Артефакты

- Задание: EXCHANGE\PROCESSED\DS_138_remove_bak_files.md
- Отчёт: EXCHANGE\OUTBOX\DS_138_remove_bak_files_report.md
- Лог выполнения: PS\ds138_remove_bak.log

## Уроки

Без новых. Подтверждён **Урок FF** (черновик): `Start-Transcript` в PS 5.1
не перехватывает stdout внешних процессов (python.exe, git.exe). Для попадания
в транскрипт нужен `2>&1 | Out-Host`. Расширяет Урок V (правило 62).
Оформление в DS_STANDARD.md §6.6 — отдельным DS (DS_138b, отложено).