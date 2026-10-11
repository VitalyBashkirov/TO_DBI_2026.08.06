# DS_144 — Периодический пересчёт КР + K2 = result_ok AND has_plp

## Шапка

- **DS:** DS_144
- **Автор:** DeepSeek
- **Пользователь:** Vitaly
- **Дата:** 11.10.2026
- **Ветка:** feature/dockerization
- **База:** 92c25ea
- **Предшественники:** DS_143 (галка «Только Ai» = K3)

## §1. Цель

1. **Периодически (раз в 10 сек) пересчитывать индикаторы КР** —
   «доступен» / «будет создан», цвета полей, доступность кнопок
   K1–K3 и галки «Только Ai».
2. **K2 «Исправить код»** — активна **только** если в КР (включая
   подкаталоги) есть файлы по маске из поля «Шаблон».

## §2. Объём работ

### 2.1. gui_app.py

| # | Место | Действие |
|---|-------|----------|
| 1 | _update_main_buttons (1356) | k2_normal = result_ok and has_plp |
| 2 | _update_main_buttons_tooltips (1411-1417) | блок К2 переписан |
| 3 | Новый метод _poll_result_dir | таймер 10 сек |
| 4 | __init__ (после 1178) | запуск _poll_result_dir |

### 2.2. SRC/tests/test_ds133_buttons_state_pytest.py

| # | Тест | Действие |
|---|------|----------|
| 1 | test_08b_k2_disabled_result_no_plp | переписан (ИК с файлом, КР пуст) |
| 2 | test_08c_k2_tooltip_result_no_plp | переписан (то же) |

## §3. Детали

### 3.1. Таймер _poll_result_dir

    def _poll_result_dir(self):
        '''DS_144: таймер (10 сек) — пересчёт индикаторов КР и кнопок.'''
        try:
            if not self.root.winfo_exists():
                return
            self._update_dir_indicators()
        except Exception:
            return
        try:
            self.root.after(10000, self._poll_result_dir)
        except Exception:
            pass

Вызывает _update_dir_indicators (2630), который уже выполняет:

- update_field_colors — цвет полей (зелёный/жёлтый/красный);
- update_status_indicators — метки «доступен»/«будет создан»;
- _update_main_buttons — пересчёт K1/K2/K3 + галки.

Ничего нового — просто периодический вызов существующего метода.

### 3.2. K2 = result_ok AND has_plp

Было:

    k2_normal = source_has_plp and result_ok

Стало:

    k2_normal = result_ok and has_plp

Где:

- result_ok — КР указан + существует + доступен для записи;
- has_plp — result_ok AND _result_dir_has_pattern_files().

Новая семантика: K2 «Исправить код» — фиксит файлы в КР (не в ИК).

### 3.3. Тултип K2

Было:

    if not source_ok: ...
    elif not source_has_plp: ...
    elif not result_ok: ...
    else: ...

Стало:

    if not result_ok: "Каталог результатов не создан. Запустите <1.Сканировать>"
    elif not has_plp: "В каталоге результатов нет файлов по шаблону."
    else: "Автоматически исправить файлы в каталоге результатов."

## §4. Результаты

### 4.1. Тесты

    pytest SRC/tests/ -q
    118 passed in ~26s

- 110 — старые (без регресса);
- +8 — DS_143 (test_ds143_ai_only_pytest.py);
- ±0 — DS_144 (тесты 08b/08c переписаны, не добавлены).

test_ds133_buttons_state_pytest.py: 18 passed (включая обновлённые
08b/08c).

### 4.2. Smoke

Сценарий 1 — КР не существует:

- индикатор «будет создан» (жёлтый);
- K2 — серая;
- тултип K2 — «Каталог результатов не создан. Запустите
  <1.Сканировать>».

Сценарий 2 — КР существует, файлы по шаблону есть:

- индикатор «доступен» (зелёный);
- K2 — активна;
- тултип K2 — «Автоматически исправить файлы в каталоге результатов».

Сценарий 3 — КР существует, файлов нет:

- K2 — серая;
- тултип K2 — «В каталоге результатов нет файлов по шаблону».

## §5. Файлы

- SRC/gui_app.py — правки D.3, D.4.
- SRC/tests/test_ds133_buttons_state_pytest.py — правки D.4b.
- tools/_archive/gui_app.py.bak_ds144_after_d4 — бэкап.

## §6. Итог

DS_144 закрыт. Периодический пересчёт КР работает. K2 привязана
к файлам в КР. Тесты зелёные.
