# DS_120 — Отчёт: замена 12 messagebox.showinfo на _show_copyable_dialog

## Итог

12 messagebox.showinfo в gui_app.py заменены на self._show_copyable_dialog
(кастомный диалог с кнопкой «Копировать»). Добавлено централизованное
подавление диалога в автономном режиме. py_compile exit=0, import OK,
pytest exit=0, BOM=False.

## Причина

messagebox не поддерживает копирование текста — для сообщений
с путями (каталоги AI_IN/AI_OUT, filepath, task_file.name) это
неудобно пользователю. Кастомный _show_copyable_dialog (DS_114)
уже существует и решает проблему.

## Изменения

1. 12 замен messagebox.showinfo -> self._show_copyable_dialog
   на строках 1399, 4137, 4199, 4575, 4817, 5154, 5226, 5245, 5269,
   5336, 5414, 5539 (номера до правки).
2. Добавлено подавление в _show_copyable_dialog: проверка
   getattr(self, '_ai_cycle_running', False) — если автономный цикл,
   тихо логировать и не показывать диалог.

## Побочные эффекты

- Размер: 347146 -> 347481 (+335 B).
- Строк: 5918 -> 5923 (+5 — блок подавления).
- Номера строк после 3659 сдвинулись на +5.

## Проверки

- py_compile: exit=0.
- import gui_app: OK.
- _show_copyable_dialog: 17 вхождений.
- messagebox.showinfo: 0 вхождений.
- pytest: LASTEXITCODE=0.
- BOM: False.

## Урок

Массовая замена messagebox.showinfo на кастомный метод затрагивает
автономный режим: подавление через monkey-patch tkinter.messagebox
(L5794-5800) НЕ покрывает пользовательские диалоги. Нужна
дополнительная проверка флага (_ai_cycle_running) в самом методе.

## Бэкап

SRC\gui_app.py.bak_ds120 (ignored).
