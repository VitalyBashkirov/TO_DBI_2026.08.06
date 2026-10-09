# DS_139 — Починка test_ds086_ui_hide.py после DS_134

## Контекст

Чат 30. Тест test_ds086_ui_hide.py (DS_086, 2026-10-05) сломан
после DS_134: кнопка btn_from_ai убрана из UI_HIDEABLE_ELEMENTS
(стала видимой по умолчанию). Baseline — 13/15 PASSED:
  FAIL #7: меню «Вид»: 6 checkbutton (факт: 5)
  FAIL #10: toggle changelog_frame → from_ai ожидался скрытым (факт: pack)

## Действие

Правки в SRC\tests\test_ds086_ui_hide.py (5 точек):
- #7: n_check == 6 → n_check == 5 (DS_134 убрал btn_from_ai).
- #10: переключено с changelog_frame/btn_from_ai на btn_show_sql/changelog_frame.
- #3: обновлено описание (5 элементов без btn_from_ai).
- #13: обновлено описание (4 → 5 ключей).
- docstring модуля: актуализирован список hideable-элементов.

## Ожидание

- test_ds086_ui_hide.py: 15/15 PASSED.
- pytest: 77 passed.
- DS_133 script: 18/18 PASSED.
- BOM: False.

## Артефакты

- Отчёт: EXCHANGE\OUTBOX\DS_139_test_ds086_fix_report.md
- Логи: PS\ds139_preview.log, ds139_preview2.log, ds139_ui_hideable.log,
  ds139_baseline.log, ds139_patch.log, ds139_patch_10.log,
  ds139_after.log, ds139_git.log
- Бэкапы: test_ds086_ui_hide.py.bak_ds139, .bak_ds139b