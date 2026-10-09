# DS_120 — Замена 12 messagebox.showinfo на _show_copyable_dialog

## Контекст

- Проект: TO_DBI. Ветка: feature/dockerization.
- База: 5f0cb26 (DS_131).
- Цель: заменить 12 messagebox.showinfo в gui_app.py на
  self._show_copyable_dialog — кастомный диалог с кнопкой «Копировать».
- Причина: messagebox не поддерживает копирование текста (путей к файлам).
- Приоритет: НИЗКИЙ/СРЕДНИЙ.

## Что сделано

12 замен messagebox.showinfo -> self._show_copyable_dialog:

| Строка (до) | Строка (после +5) | Содержимое |
|-------------|-------------------|------------|
| L1399 | L1399 | «Очистка завершена» |
| L4137 | L4142 | «Исправление завершено» (lambda) |
| L4199 | L4204 | «Архивация завершена» (lambda) |
| L4575 | L4580 | «Генерация завершена» (lambda) |
| L4817 | L4822 | «Нет проблем» |
| L5154 | L5159 | «Успех: Журнал сохранен» |
| L5226 | L5231 | «Успех: Задание отправлено в Koda» |
| L5245 | L5250 | «Информация: Нет ответов в OUTBOX» |
| L5269 | L5274 | «Успех: Ответ получен из» |
| L5336 | L5341 | «Нет проблем» |
| L5414 | L5419 | «AI-запрос сформирован» (многострочный) |
| L5539 | L5544 | «Нет ответов» |

## Подавление в автономном режиме

Добавлено в _show_copyable_dialog (L3661-L3664 после docstring).
Проверка: if getattr(self, '_ai_cycle_running', False) — тихо логировать и выйти.

Причина: _run_ai_cycle (L5794-5800) подавляет messagebox.* monkey-patch'ем.
После замены showinfo на _show_copyable_dialog диалог БЫ появлялся
в автономном режиме и ломал цикл. Теперь подавляется централизованно.

## Проверки

- py_compile gui_app.py: exit=0.
- import gui_app: OK, exit=0.
- _show_copyable_dialog: 17 вхождений (1 def + 16 вызовов).
- messagebox.showinfo: 0.
- messagebox остались: askyesno 2, showerror 18, showwarning 6 (нативные).
- pytest: LASTEXITCODE=0.
- BOM: False.
- gui_app.py: 5918 -> 5923 строк, 347146 -> 347481 B.

## Бэкап

SRC\gui_app.py.bak_ds120 (ignored, *.bak_*).
