# DS_141b — Урок JJJ в DS_STANDARD.md §6.6.9

## Контекст

В ходе DS_141 (Шаг 3) выявлен новый урок: оператор -like в PowerShell
трактует [ ], * и ? как wildcard-метасимволы, не как обычные символы.
Анкор с [sys.executable, ...] упал на WildcardPatternException.

## Действие

Append §6.6.9 в DS_STANDARD.md — описание Урока JJJ и правила:
для проверки подстроки использовать .Contains(), не -like.

## Ожидание

- DS_STANDARD.md: 41278 → 43444 B (+2166), строк 823 → 863.
- Заголовков §6.6.x — 9 (было 8).
- BOM=False.

## Артефакты

- Отчёт: EXCHANGE\OUTBOX\DS_141b_like_wildcard_report.md
- Логи: PS\ds141b_preview.log, ds141b_append.log, ds141b_git.log
- Бэкап: DS_STANDARD.md.bak_ds141b