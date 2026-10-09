# DS_137. Прогресс 100% после архивации результата

## СТАТУС ЗАДАНИЯ

ВОССТАНОВЛЕНО ПО ФАКТУ в чате 29.
Задание выделено из отложенных задач чата 28 (см. DS_134_gui_smoke_fixes.md,
пункт «Прогресс-бар не сбрасывается после К2», перенесено в DS_137).
Выполнено в чате 29.

## Контекст

Чат 29. Основная тема — прогресс-бар не сбрасывается после архивации.
Ветка feature/dockerization. Живой GUI SRC\gui_app.py.

## Симптом

После К2 «2. Исправить код» с включённой опцией «Архивировать результат»:

1. Прогресс доходит до 100% в момент архивации.
2. Диалог «Исправление завершено» → ОК.
3. Диалог «Архивация завершена» → ОК.
4. Прогресс-бар остаётся 100%, надпись «100%».

Ожидание: после закрытия диалогов прогресс-бар = 0%, надпись «0%».

## Причина

Гонка потоков между _run_fix (main thread) и _run_archive (отдельный поток).

_run_fix (L4248-4296):
- L4254-4257: если should_archive → thread = Thread(target=_run_archive); thread.start().
- L4270-4271: after(0, progress.config(0)) + after(0, progress_label.config("0%")).
- L4273-4279: after(0, _show_copyable_dialog("Исправление завершено", ...)).
- L4287-4296 (finally): after(0, _finish_abortable_operation).

_finish_abortable_operation (L1929-1959):
- L1953: self._reset_progress() → progress.config(0) + progress_label("0%").

_run_archive (L4298-4341):
- L4302: self._progress_update(95) → after(0, progress.config(95)).
- L4328: self._progress_update(100) → after(0, progress.config(100)).
- L4334: after(0, log("Архив создан")).
- L4335-4337: after(0, _show_copyable_dialog("Архивация завершена", ...)).

Итог гонки: _progress_update(100) из _run_archive (L4328) выполняется
ПОСЛЕ сброса в _finish_abortable_operation (L1953). _run_archive —
последний в цепочке, НЕ сбрасывает прогресс. Прогресс остаётся 100%.

## Решение (вариант 3 — двойной сброс)

В _run_archive добавить два сброса:

1. Явный сброс ПЕРЕД диалогом «Архивация завершена»:
   - После _progress_update(100) (L4328).
   - Перед after(0, log("Архив создан")) (L4334).
   - Это гарантирует 0% к моменту показа диалога.

2. Гарантированный сброс в finally:
   - Сработает в т.ч. при исключении в блоке try.
   - Дубль безопасен (идемпотентно).

## Правки в SRC\gui_app.py

### Правка 1 (_run_archive, ~L4334)

Вставлено ПЕРЕД строкой `self.root.after(0, lambda: self.log(f"\nАрхив создан: ...`:

    # DS_137: сброс прогресса до диалога «Архивация завершена»
    self.root.after(0, self._reset_progress)

### Правка 2 (_run_archive, ~L4345)

Добавлено ПОСЛЕ блока except:

    finally:
        # DS_137: гарантированный сброс прогресса (в т.ч. при исключении)
        self.root.after(0, self._reset_progress)

Блок try/except/finally — единый; finally привязан к try в начале функции.

## Тесты

- pytest SRC\tests\ -q → 77 passed, exit=0.
- python SRC\tests\test_ds133_buttons_state.py → 18/18 PASSED, exit=0.
- ast.parse gui_app.py → OK.

Ручной smoke (Vitaly):
- К2 с архивацией → диалоги «Исправление завершено», «Архивация завершена».
- После закрытия обоих: прогресс-бар = 0%, надпись «0%», статус «Готово».
- Подтверждено скриншотом.

## §5 Проверка

1. python -m pytest SRC\tests\ -q → 77 passed, exit=0.
2. python SRC\tests\test_ds133_buttons_state.py → 18/18 PASSED, exit=0.
3. ast.parse gui_app.py → OK.
4. Ручной smoke → прогресс 0% после архивации.
5. BOM-check: gui_app.py — UTF-8 без BOM.

## Ограничения

- Не трогать _finish_abortable_operation (сброс L1953 остаётся —
  покрывает ветку should_archive=False).
- Не трогать _progress_update (общий механизм).
- Не менять порядок в _run_fix (L4248-4296).

## Артефакты

- Отчёт: EXCHANGE\OUTBOX\DS_137_archive_progress_reset_report.md.
- Задание: этот файл (восстановлено).
- Бэкап: SRC\gui_app.py.bak_ds137.
- bot.log — обновить (правило 29: до коммита).