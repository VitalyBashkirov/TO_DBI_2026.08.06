# DS_136 — Активация К2 после К1: PATCH_OUT + критерий source_has_plp

## 1. Задача

Чат 28. Продолжение DS_134 (три бага GUI: К4 / К3 / прогресс).
В процессе ручного smoke обнаружено: К2 «2. Исправить код» не активируется
после К1. Замкнутый круг:

- критерий DS_133 требует *.plp в result,
- result создаётся только в К2,
- К2 не активна → result не создаётся.

Решение (вариант A + X):
- A: при К1 создавать пустой PATCH_OUT (прогноз результата).
- X: критерий К2 = source_ok AND source_has_plp
  (в source есть файлы по шаблону).

Ветка feature/dockerization, Ollama available, GUI SRC\gui_app.py.

## 2. Симптомы (исходные)

- После К1 (диалог «Сканирование завершено» → ОК):
  - PATCH_OUT не создан;
  - К2 остаётся тонкой (disabled);
  - индикатор КР: «будет создан» (не обновляется на «доступен»).
- Пользователь не может запустить К2 без ручного создания result.

## 3. Причины (исходные)

1. start_scan (L3266-3291) НЕ создавал result — только читал source.
   Result создавался в start_fix (L3832-3836).
2. _update_main_buttons (L1330-1331): k2_normal = has_plp, где
   has_plp = result_ok AND _result_dir_has_pattern_files().
   Пустой result → False.

## 4. Что сделано

### 4.1. Правка A — создание PATCH_OUT в start_scan (выполнено)

В start_scan, после проверки source_dir.exists(), вставлено:

    auto_result = self._auto_fill_result_dir(source_dir)
    if auto_result and not auto_result.exists():
        try:
            auto_result.mkdir(parents=True, exist_ok=True)
            self.result_dir_var.set(str(auto_result))
            self.log(f"Создан пустой каталог результатов (прогноз): {auto_result}", 'info')
        except Exception as e:
            self.log(f"Не удалось создать каталог результатов: {e}", 'warning')

Фактическое расположение (подтверждено в чате 29):
- L3313 — вызов _auto_fill_result_dir(source_dir).
- L3318 — self.log("Создан пустой каталог результатов (прогноз): ...").

_auto_fill_result_dir сам вызывает result_dir_var.set() → сработает trace
L2097 → _update_dir_indicators() → индикатор обновится на «доступен».

### 4.2. Правка B1 — функция _source_dir_has_pattern_files (выполнено)

Функция добавлена после L1290 (после _result_dir_has_pattern_files).

ФАКТИЧЕСКАЯ реализация (см. отступление Q1):

    def _source_dir_has_pattern_files(self) -> bool:
        """DS_136: есть ли файлы по Шаблону в исходном каталоге."""
        source = self.source_dir_var.get().strip()
        pattern = self.file_pattern_var.get().strip()
        if not source or not pattern:
            return False
        try:
            p = Path(source)
            if not p.exists() or not p.is_dir():
                return False
            gen = p.rglob(pattern if '*' not in pattern else pattern.replace('**/', '').replace('**', '*'))
            return any(True for f in gen if not is_temporary_filename(f.name))
        except Exception:
            return False

Отличие от задания: в задании предлагалось glob + scan_recursive_var;
фактически — rglob всегда + фильтр is_temporary_filename (DS_135-2d).

### 4.3. Правка B2 — _update_main_buttons (выполнено)

Фактическая строка L1352-1353:

    source_has_plp = source_ok and self._source_dir_has_pattern_files()
    k2_normal = source_has_plp and result_ok

Отличие от задания: в задании k2_normal = source_has_plp;
фактически добавлен AND result_ok (логичнее — result должен существовать).

### 4.4. Правка B3 — вызов тултипов (выполнено)

L1374-1378:

    self._update_main_buttons_tooltips(
        k1_normal=k1_normal, k2_normal=k2_normal, k3_normal=k3_normal,
        source_ok=source_ok, pattern_ok=pattern_ok, rule_ok=rule_ok,
        result_ok=result_ok, has_plp=has_plp, ai_in_empty=ai_in_empty,
        source_has_plp=source_has_plp)

### 4.5. Правка B4 — сигнатура тултипов (выполнено)

L1384-1387:

    def _update_main_buttons_tooltips(self, k1_normal, k2_normal, k3_normal,
                                        source_ok, pattern_ok, rule_ok,
                                        result_ok, has_plp, ai_in_empty,
                                        source_has_plp=False):

### 4.6. Правка B5 — тултип К2 (выполнено)

L1400-1408:

    if not source_ok:
        k2_tip = "Укажите существующий исходный каталог."
    elif not source_has_plp:
        k2_tip = "В исходном каталоге нет файлов по шаблону."
    elif not result_ok:
        k2_tip = "Каталог результатов не создан. Запустите <1.Сканировать>"
    else:
        k2_tip = "Автоматически исправить найденные проблемы."

Тултип К3 не трогали — он привязан к has_plp в result, что правильно.

## 5. Тесты

### 5.1. По заданию

Требовалось добавить два теста:
- test_k2_normal_when_source_has_plp.
- test_k2_disabled_when_source_empty.

### 5.2. Фактическое состояние

Файл SRC\tests\test_ds133_buttons_state.py — legacy-стиль
(if __name__ == '__main__'), не собирается pytest (правило N12).

После DS_136 критерий К2 изменился, а тест #8 остался на СТАРОЙ формуле
(К2 = result_ok AND has_plp) — падал: «К2 disabled при наличии *.plp в result».
Это НЕ регресс логики, а устаревший тест.

Диагноз (чат 29, «Вариант A»): тест устарел, логика корректна. Потери
return в функциях-сёстрах нет (Урок AA не подтверждён).

### 5.3. DS_136a — обновление теста (выполнено в чате 29)

Правки в test_ds133_buttons_state.py:
- L6 шапка: «К2 = result_ok AND has_plp» → «К2 = source_has_plp AND result_ok (DS_136)».
- Тест #8: положить *.plp и в source, и в result → К2 normal.
- Новый #8b: result с *.plp, source без *.plp → К2 disabled (DS_136-специфика).
- Новый #8c: тултип К2 при source без *.plp → «В исходном каталоге
  нет файлов по шаблону.»

Бэкап: SRC\tests\test_ds133_buttons_state.py.bak_ds136a.

## 6. Проверка (§5)

1. python -m pytest SRC\tests\ -q → 77 passed, exit=0.
2. python SRC\tests\test_ds133_buttons_state.py → 18/18 PASSED, exit=0
   (16 исходных + #8 обновлён + #8b, #8c новые).
3. ast.parse gui_app.py → без ошибок.
4. Ручной smoke (Vitaly): К1 на каталоге с *.plp → PATCH_OUT создан,
   индикатор «доступен», К2 жирная; К2 → диалог «Исправление завершено»
   → ОК; К3 жирная.
5. BOM-check: gui_app.py, test_ds133_buttons_state.py — UTF-8 без BOM.

## 7. Артефакты

- Коммит: 6f5efb0 — "DS_134+135+136: GUI-фиксы (K4/K3), временные метки,
  критерий K2, статистика".
- Push: 3db4cc4..6f5efb0 в origin/feature/dockerization, выполнен.
- Задание: EXCHANGE\PROCESSED\DS_136_gui_patchout_k2_activation.md
  (перемещение из INBOX в PROCESSED в чате 29).
- Отчёт: этот файл.
- Правка теста: DS_136a (в чате 29, вне коммита 6f5efb0).

## 8. Отступления от задания

Q1. Правка B1: фактическая реализация использует rglob всегда, без
    scan_recursive_var. Это результат DS_135-2d (рекурсивный поиск
    согласован с _result_dir_has_pattern_files). Отступление
    задокументировано.

Q2. Правка B2: k2_normal = source_has_plp AND result_ok (в задании —
    source_has_plp). Добавлено AND result_ok — логичнее, result должен
    существовать до К2.

Q3. Тест #8 устарел после DS_136 → закрыт через DS_136a (в чате 29).

Q4. Методологический вывод (правило N12): pytest 77 passed не покрывает
    DS_133 script, потому что файл в legacy-стиле. Регресс pytest
    «зелёный», а скрипт «красный» — ровно тот случай, ради которого N12
    вводилось. Правка теста — DS_136a.

Q5. settings.json не в git (Урок CC) — правки UI_HIDE локальны,
    не сохранятся в репо.

## 9. Открытые вопросы

1. Прогресс 100% после архивации → DS_137 (основная тема чата 29).

2. test_ds133_buttons_state.py — миграция в pytest-стиль (N12).
   Отдельная задача.

3. test_ds086_ui_hide.py — legacy, pytest не собирает, #10 сломан
   после DS_134 (см. отчёт DS_134 §7 Q3).

4. DS_136a не закоммичен на момент написания отчёта (правка теста
   + .bak_ds136a). Войдёт в коммит чата 29.

5. deep_scanner.py — фильтр временных (см. отчёт DS_135 §7 Q1).