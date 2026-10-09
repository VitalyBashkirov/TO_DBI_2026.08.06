# DS_139 — Починка test_ds086_ui_hide.py. Отчёт

**Дата:** 2026-10-09
**Чат:** 30
**Автор DS:** DeepSeek
**Пользователь:** Vitaly
**Тип:** Правка теста
**Статус:** ✅ Выполнен

## Причина

После DS_134 (коммит 6f5efb0) кнопка btn_from_ai убрана из
UI_HIDEABLE_ELEMENTS — стала видимой по умолчанию (workflow DS_133).
Тест test_ds086_ui_hide.py этого не знал.

## Baseline (до правок)

13/15 PASSED:
- FAIL #7: checkbutton=5 (ожидалось 6).
- FAIL #10: from_ai='pack' (ожидалось скрытие).

## Действие

5 правок в SRC\tests\test_ds086_ui_hide.py через PS-блоки .Replace
(без Python в консоли — Урок DD):

1. #7 описание: «6 checkbutton» → «5 checkbutton (DS_134: btn_from_ai убран)».
2. #7 условие: n_check == 6 → n_check == 5.
3. #10 (переключено): btn_show_sql + changelog_frame (оба в HIDE_KEYS).
4. #3 описание: «btn_show_sql / btn_send_koda / btn_from_ai / changelog_frame»
   → «5 элементов реестра (без btn_from_ai — видим по DS_134)».
5. #13 описание: «4 ключа» → «5 ключей».
6. docstring: список hideable-элементов актуализирован.

## Результат

| Параметр | Было | Стало |
|----------|------|-------|
| test_ds086_ui_hide.py | 13/15 | **15/15 PASSED** |
| pytest | 77 passed | **77 passed** |
| DS_133 script | 18/18 | **18/18 PASSED** |
| Размер теста | 9965 B | 10307 B |
| BOM | False | False |

## Проверки

- ast.parse OK.
- Все 15 тестов PASSED.
- pytest exit=0.
- DS_133 exit=0.

## Инцидент

Первая правка #10 (многострочный .Replace) не сработала —
несовпадение переводов строк. Исправлено построчной заменой
(блок 157..164 → новый). Файл не пострадал, ast.parse OK.

## Артефакты

- Задание: EXCHANGE\PROCESSED\DS_139_test_ds086_fix.md
- Отчёт: EXCHANGE\OUTBOX\DS_139_test_ds086_fix_report.md
- Логи: PS\ds139_*.log (8 файлов)
- Бэкапы: test_ds086_ui_hide.py.bak_ds139, .bak_ds139b

## Уроки

- Урок DD подтверждён (Python в PS-консоли → ParserError).
- Урок II (не полагаться на пустые строки в .md) —
  распространяется на .py: многострочный .Replace ненадёжен,
  построчная замена по индексам надёжнее.
- Baseline перед правкой (Шаг 1) — правильный подход,
  позволил точно локализовать 2 падения.

## bot.log

Запись добавлена.