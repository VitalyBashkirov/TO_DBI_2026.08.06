# DS_134 — Ручной smoke GUI: фиксы К4, К3 после К2, сброс прогресса

## 1. Задача

Чат 28. Ручной smoke-тест живого GUI (`SRC\gui_app.py`, АРМ «Адаптация под DBI»).
Ветка feature/dockerization на 3db4cc4 (DS_133). Ollama available.

Три бага, обнаруженные вручную:

1. К4 «4. Из Ai» не видна в GUI (скрыта legacy-списком UI_HIDE_DEFAULT_V1).
2. К3 «3. В Ai» не активируется после завершения К2.
3. Прогресс-бар не сбрасывается после К2 (застревает 0% / 100%).

Задание требовало тестов test_k4_visible и test_k3_after_fix в стиле
if __name__ == '__main__' (не pytest — правило N12).

## 2. Что сделано

### 2.1. К4 «4. Из Ai» — сделана видимой (выполнено)

- L94-95: UI_HIDE_DEFAULT_V1 сокращён с 5 до 4 ключей — убран btn_from_ai.
- L80: btn_from_ai убран из UI_HIDEABLE_ELEMENTS.
- L76-77, L91: комментарии про К4.

### 2.2. К3 «3. В Ai» — активация после К2 (выполнено через DS_135-2f)

Первая попытка (правка 2 из задания DS_134, L4199 — замена legacy
self._update_buttons_state на self._update_main_buttons) НЕ СРАБОТАЛА.

Причина: _update_main_buttons вызывалась ДО _finish_abortable_operation,
когда scan_running=True. Функция делает ранний выход при scan_running=True
(L1332-1333) → пересчёт не выполнялся.

Решение (DS_135-2f):
- Удалено из _run_fix (L4239-4240): self.root.after(0, self._update_main_buttons).
- Добавлено в _finish_abortable_operation (после scan_running = False):
  self._update_main_buttons().

Результат: К3 корректно активируется после завершения К2.

### 2.3. Прогресс-бар — НЕ закрыт (перенесён в DS_137)

Правка 3 из задания (сброс прогресса перед _show_copyable_dialog, L4222)
НЕ СРАБОТАЛА.

Причина: _run_archive в отдельном потоке устанавливает 100% после
_finish_abortable_operation (который сбрасывает в 0%). Архив возвращает 100%.

Решение отложено в DS_137: сбросить прогресс в _run_archive finally либо
в callback после архива.

### 2.4. Дополнительно (сверх задания)

- Tooltip дерева рубрикаторов: AttributeError _tree_tooltip_text.
  Фикс: L243 — self._tree_tooltip = None, self._tree_tooltip_text = None
  в __init__.

- Guard в _update_main_buttons (DS_135-2g): L1332-1335 — проверка
  hasattr(self, 'source_dir_var') and hasattr(self, 'result_dir_var').
  Причина: 3 теста (test_ds089a, test_ds108) вызывают
  _finish_abortable_operation через new без init → AttributeError.
  Правило N14 / Урок CC.

## 3. Файлы и правки

SRC\gui_app.py:
- L76-77, L80, L91, L94-95 — К4 (UI_HIDE_DEFAULT_V1, UI_HIDEABLE_ELEMENTS).
- L243 — инициализация _tree_tooltip / _tree_tooltip_text.
- L1332-1335 — guard hasattr в _update_main_buttons.
- _run_fix → _finish_abortable_operation — перенос вызова
  _update_main_buttons (DS_135-2f).

## 4. Тесты

По заданию требовались:
- test_k4_visible — после инициализации GUI
  self.btn_from_ai.winfo_ismapped() возвращает True.
- test_k3_after_fix — при has_plp=True и ai_in_empty=True после
  _update_main_buttons() btn_to_ai имеет state !disabled и style
  WorkflowActive.TButton.

Фактически (по результатам диагностики чата 29):
- test_k4_visible — НЕ РЕАЛИЗОВАН как отдельный тест. winfo_ismapped
  в SRC\tests\ встречается только в test_ds088a_fix.py (для
  conf_low_entry/conf_high_entry). В test_ds133_buttons_state.py
  winfo_ismapped отсутствует.
- test_k3_after_fix — НЕ РЕАЛИЗОВАН. К3 покрыт косвенно: #9 (disabled
  при AI_REQUEST в AI_IN), #10 (normal при *.plp + пустом AI_IN) —
  но это не проверка активации после отработки К2 (не тестирует
  _finish_abortable_operation).

Косвенное покрытие К4 в test_ds133_buttons_state.py:
- #11 (К4 disabled при пустом AI_OUT).
- #12 (К4 normal при AI_RESPONSE в AI_OUT).
Это state-проверки, не видимость.

## 5. Проверка (§5)

Историческая хронология:
- На момент DS_134 (до чата 28): pytest 65 passed.
- После чата 28 (DS_135/136 + test_ds135_temporary.py): pytest 77 passed, exit=0.
- После DS_136a (обновление test_ds133_buttons_state.py под К2 DS_136):
  pytest 77 passed, exit=0; скрипт test_ds133_buttons_state.py 18/18 PASSED,
  exit=0.

ast.parse gui_app.py — 0 warnings.

BOM-check: gui_app.py, test_ds133_buttons_state.py — UTF-8 без BOM.

Ручной smoke (Vitaly, чат 28):
- К4 «4. Из Ai» видна (тонкая, disabled при пустом AI_OUT).
- К1 → К2 → после «ОК»: К3 «3. В Ai» стала жирной (normal).
- Прогресс-бар — НЕ сбросился (баг перенесён в DS_137).

## 6. Артефакты

- Коммит: 6f5efb0 — "DS_134+135+136: GUI-фиксы (K4/K3), временные метки,
  критерий K2, статистика".
- Push: 3db4cc4..6f5efb0 в origin/feature/dockerization, выполнен.
- Задание: EXCHANGE\PROCESSED\DS_134_gui_smoke_fixes.md
  (перемещение из INBOX в PROCESSED выполнено в чате 29).
- Отчёт: этот файл.

## 7. Отступления от задания

Q1. test_k4_visible — не реализован как отдельный тест. К4 покрыта
    косвенно (#11, #12).

Q2. test_k3_after_fix — не реализован. К3 покрыт #9, #10, но без проверки
    активации после _finish_abortable_operation.

Q3. test_ds086_ui_hide.py #10 — сломан после DS_134. Проверяет
    is_hidden(app, 'btn_from_ai'), а после DS_134 кнопка видима.
    Файл — legacy (N12): pytest --collect-only возвращает exit=5,
    0 collected. На pytest 77 passed не влияет, но при ручном
    запуске падает. Требует обновления или удаления — DS_137/138.

Q4. Прогресс 100% после архивации — не закрыт, перенесён в DS_137.

Q5. Правка 2 из задания (замена legacy _update_buttons_state на
    _update_main_buttons в _run_fix) переработана в DS_135-2f
    (перенос в _finish_abortable_operation). Причина — гонка
    с scan_running=True.

Q6. Guard hasattr в _update_main_buttons (L1332-1335) добавлен
    сверх задания — требование N14 (тесты через new).

Q7. Tooltip дерева рубрикаторов — фикс сверх задания.

## 8. Открытые вопросы

1. Прогресс 100% после архивации → DS_137.

2. test_ds086_ui_hide.py #10 — обновить или удалить (устарел после DS_134).
   Решить в DS_137 или отдельном DS.

3. pytest-миграция test_ds133_buttons_state.py и test_ds086_ui_hide.py
   (правило N12): скрипты в стиле if __name__ == '__main__' не собираются
   pytest. Миграция — отдельная задача.

4. test_k4_visible и test_k3_after_fix — реализовать в pytest-стиле.
   Возможно, в рамках пункта 3.

5. settings.json не в git (Урок CC) — правки UI_HIDE локальны.
   Учесть при воспроизведении на другой машине.