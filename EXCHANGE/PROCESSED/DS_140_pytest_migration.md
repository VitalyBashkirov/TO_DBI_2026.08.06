# DS_140 — pytest-миграция legacy-тестов

**Дата постановки:** 2026-10-10
**Дата закрытия:** 2026-10-11
**Автор:** DeepSeek
**Пользователь:** Vitaly

## Цель

Перевести два legacy-теста с самописного «runner» на pytest
(Вариант 2 — полный перенос):

- `SRC/tests/test_ds133_buttons_state.py` — 18 проверок (активация main-кнопок).
- `SRC/tests/test_ds086_ui_hide.py` — 15 проверок (скрытие элементов GUI).

Результат: все проверки живут в pytest-стиле (`def test_*`), собираются
`pytest SRC\tests\`, legacy-скрипты архивируются.

## План (5 шагов)

| Шаг | Действие |
|-----|----------|
| 0 | Превью `test_ds133_buttons_state.py` + разведка `gui_app.py`. |
| 1 | Создать `SRC/tests/conftest.py` + мигрировать `test_ds133`. |
| 2 | Проверить: pytest 95 passed. |
| 3 | Мигрировать `test_ds086`. |
| 4 | Проверить: pytest 110 passed. |
| 5 | Задание + отчёт + bot.log + коммит. |

## Открытые решения (приняты)

| Решение | Выбор |
|---------|-------|
| scope fixture `app` | **function** |
| Создавать `conftest.py` | **да** |
| Legacy-стиль | **убрать полностью** |
| Изоляция AI_IN / AI_OUT | **monkeypatch методов** (`_ai_in_request_files` / `_ai_out_files`) |
| Архитектура тестов | **2a: 18/15 отдельных `def test_*`** |
| Legacy после миграции | **оставить как `.py.txt`** |

## Риски

- Tkinter fixtures (один root, destroy между тестами).
- `after()`-таймеры (`_poll_ai_out` → TclError после destroy).
- `settings.json` backup/restore (DS_086).
- `winfo_manager` после `update_idletasks` (DS_086).
- `--capture=no` в pytest.ini → `print` из legacy виден.

## Критерий готовности

- pytest зелёный: **110 passed** (77 + 18 + 15).
- Legacy → `.py.txt` (git mv, история сохранена).
- Отчёт в `EXCHANGE\OUTBOX`.