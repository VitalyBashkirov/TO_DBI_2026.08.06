# DS_142 — §6.6.10–§6.6.17 в DS_STANDARD.md

**Дата постановки:** 2026-10-11
**Дата закрытия:** 2026-10-11
**Автор:** DeepSeek
**Пользователь:** Vitaly

## Цель

Зафиксировать 7 уроков чата 31 (DS_140) в DS_STANDARD.md как
новые подразделы §6.6.10–§6.6.17. Расширяет блок §6.6.1–§6.6.9.

## Планируемые подразделы

| § | Урок | Заголовок |
|---|------|-----------|
| 6.6.10 | LLL | Активный транскрипт блокирует N7-очистку |
| 6.6.11 | MMM | Tkinter after() в pytest → TclError |
| 6.6.12 | NNN | Кириллица в PS-путях |
| 6.6.13 | OOO | trace_add('write') — side-effects |
| 6.6.14 | PPP | pytest.ini --capture=no и print |
| 6.6.15 | QQQ | Get-Content в PS 5.1 не UTF-8 |
| 6.6.16 | RRR/SSS | $ErrorActionPreference между блоками |
| 6.6.17 | TTT | here-string + вложенные backticks в PS 5.1 |

## Метод записи

DS_STANDARD.md — большой .md с Markdown-разметкой. Прямая вставка
через PS here-string **ломается** на backticks (Урок TTT).

**Решение**: писать через Python-скрипт `ds142_append.py` в `PS\`.
Python не боится ни backticks, ни кириллицы.

## Критерий готовности

- §6.6.10–§6.6.17 добавлены, BOM=False.
- Задание + отчёт в EXCHANGE.
- bot.log обновлён.
- Коммит сделан.