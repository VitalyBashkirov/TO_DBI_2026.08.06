# DS_141b — Урок JJJ в §6.6.9. Отчёт

**Дата:** 2026-10-10
**Чат:** 30
**Автор DS:** DeepSeek
**Пользователь:** Vitaly
**Тип:** Документация
**Статус:** ✅ Выполнен

## Причина

В ходе DS_141 (Шаг 3) обнаружено: оператор -like в PowerShell трактует
символы [ ], * и ? как wildcard-метасимволы. Анкор с [sys.executable, ...]
(типичный Python-список) упал с WildcardPatternException.

Это привело к fail-fast в Шаге 3 — файл НЕ пострадал, но инцидент
стоит зафиксировать.

## Действие

Append §6.6.9 в DS_STANDARD.md — Урок JJJ:
- Симптом: WildcardPatternException на -like с [ ].
- Решение: использовать .Contains() для проверки подстроки.
- Правило: -like только для намеренной wildcard-семантики.
- Расширяет Урок N (49) и Урок DD (70).

## Результат

| Параметр | Было | Стало |
|----------|------|-------|
| DS_STANDARD.md | 41278 B / 823 строки | 43444 B / 863 строки |
| §6.6.x заголовков | 8 | 9 |
| BOM | False | False |

## Артефакты

- Задание: EXCHANGE\PROCESSED\DS_141b_like_wildcard.md
- Отчёт: EXCHANGE\OUTBOX\DS_141b_like_wildcard_report.md
- Логи: PS\ds141b_preview.log, ds141b_append.log, ds141b_git.log
- Бэкап: DS_STANDARD.md.bak_ds141b

## bot.log

Короткая запись добавлена.