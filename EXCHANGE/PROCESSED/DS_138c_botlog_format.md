# DS_138c — Формат записей в bot.log + Урок JJ (§6.6.8)

## Контекст

После DS_138b обнаружено: строка DS_138b в bot.log записана без
квадратных скобок и времени, тогда как существующий формат —
"[YYYY-MM-DD HH:MM] DS_XXX: текст". Стиль выбивается из журнала.

## Действие

1. Исправить строку DS_138b в EXCHANGE\bot.log к формату:
   "[2026-10-09 16:41] DS_138b: обновление DS_STANDARD.md §6.6.1-6.6.7 ...".
2. Добавить §6.6.8 в DS_STANDARD.md: Урок JJ — перед append в bot.log
   читать последние 2-3 строки и копировать формат.

## Ожидание

- bot.log: строка DS_138b в формате [YYYY-MM-DD HH:MM].
- DS_STANDARD.md: §6.6.8 добавлен; заголовков §6.6.x — 8.
- BOM=False для обоих.
- pytest 77 passed; DS_133 18/18.

## Ссылки

- Отчёт: EXCHANGE\OUTBOX\DS_138c_botlog_format_report.md
- Логи: PS\ds138c_botlog_fix.log, PS\ds138c_artifacts.log