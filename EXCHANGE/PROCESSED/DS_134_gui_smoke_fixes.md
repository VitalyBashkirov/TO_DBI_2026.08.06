# DS_134. Ручной smoke GUI: фиксы К4, К3 после К2, сброс прогресса

## Контекст

Чат 28. Ручной smoke-тест живого GUI (`SRC\gui_app.py`, АРМ «Адаптация под DBI»).
Ветка feature/dockerization на `3db4cc4` (DS_133). Ollama доступна
(`--check` → available, model=qwen2.5-coder:7b).

## Симптомы (обнаружены вручную)

1. **К4 «4. Из Ai» не видна в GUI.** Кнопка создаётся (L991), подпись верная,
   `pack` корректный, но скрыта legacy-списком `UI_HIDE_DEFAULT_V1` (L95).
2. **К3 «3. В Ai» не активируется после завершения К2.** К2 отрабатывает,
   диалог «Исправление завершено» закрыт «ОК», но К3 остаётся disabled.
3. **Прогресс-бар не сбрасывается после К2.** Индикатор застревает (0% / 100%).

## Причины (подтверждены probe)

- **К4:** L95 `UI_HIDE_DEFAULT_V1 = ('btn_show_sql', 'btn_send_koda', 'btn_from_ai', 'changelog_frame')` —
  `btn_from_ai` в списке скрытых. Legacy DS_054, не учтён в DS_133.
- **К3:** финализатор `_run_fix` L4199 вызывает legacy `self._update_buttons_state`,
  а не новый `self._update_main_buttons` (DS_133). Пересчёт по артефактам не
  выполняется, К3 остаётся в состоянии после `start_fix` (L3845-3846).
- **Прогресс:** сброс (`progress.config(value=0)`, `progress_label.config(text="0%")`)
  есть только в начале `start_fix` (L3852-3853). После завершения сброса нет.
  Дополнительно: `_show_copyable_dialog` (L4222) модальный, `after(0,...)` из
  L4179-4245 исполняются только после его закрытия — сброс должен стоять
  ДО вызова диалога.

## Правки в SRC\gui_app.py

### Правка 1 (L95) — показать К4

Было:
    UI_HIDE_DEFAULT_V1 = ('btn_show_sql', 'btn_send_koda', 'btn_from_ai', 'changelog_frame')

Стало:
    UI_HIDE_DEFAULT_V1 = ('btn_show_sql', 'btn_send_koda', 'changelog_frame')

Правило N10: использовать .Replace на строке, не присваивание целиком.

### Правка 2 (L4199) — активация К3 после К2

Было:
    4198:  # Обновить состояние кнопок после исправления
    4199:  self.root.after(0, self._update_buttons_state)

Стало:
    4198:  # DS_133/DS_134: пересчёт кнопок 1/2/3 по артефактам на диске
    4199:  self.root.after(0, self._update_main_buttons)

### Правка 3 (перед L4222) — сброс прогресса

Вставить ПЕРЕД вызовом `_show_copyable_dialog` (L4222):

    # DS_134: сброс прогресс-бара до показа модального диалога
    self.root.after(0, lambda: self.progress.config(value=0))
    self.root.after(0, lambda: self.progress_label.config(text="0%"))

## Тесты (SRC\tests\test_ds133_buttons_state.py)

Добавить два теста (в стиле файла, `if __name__ == '__main__'`):

1. **test_k4_visible** — после инициализации GUI `self.btn_from_ai.winfo_ismapped()`
   возвращает True (кнопка не скрыта). Проверяет правку 1.
2. **test_k3_after_fix** — при `has_plp=True` и `ai_in_empty=True` после вызова
   `_update_main_buttons()` `btn_to_ai` имеет state `!disabled` и style
   `WorkflowActive.TButton`. Проверяет правку 2.

## §5 Проверка (обязательна)

1. `python -m pytest SRC\tests\ -q` → ожидается 65 passed, exit=0.
2. `python SRC\tests\test_ds133_buttons_state.py` → ожидается 18/18 PASSED, exit=0
   (16 старых + 2 новых).
3. `ast.parse` на `gui_app.py` → без ошибок.
4. Ручной smoke (Vitaly):
   - перезапустить `python SRC\gui_app.py`;
   - убедиться, что К4 «4. Из Ai» видна (тонкая, disabled — при пустом AI_OUT);
   - выполнить К2 «Исправить код» на тестовом каталоге с `*.plp`;
   - после «ОК» в диалоге: К3 «3. В Ai» стала жирной (normal);
   - прогресс-бар сбросился в 0%.
5. BOM-check: `gui_app.py`, `test_ds133_buttons_state.py` — UTF-8 без BOM.

## Ограничения

- Не трогать legacy `_update_buttons_state` — он используется в других ветках.
- Не трогать прочие элементы `UI_HIDE_DEFAULT_V1`.
- Не коммитить bot.log отдельно — только вместе с DS_134.

## Артефакты

- Отчёт: `EXCHANGE\OUTBOX\DS_134_gui_smoke_fixes_report.md`.
- Задание: `EXCHANGE\PROCESSED\DS_134_gui_smoke_fixes.md`.
- bot.log — обновить (правило 29: ДО коммита).