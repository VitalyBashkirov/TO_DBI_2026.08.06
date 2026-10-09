# DS_136. Активация К2 после К1: создание PATCH_OUT + критерий source_has_plp

## Контекст

Чат 28. Продолжение DS_134 (три бага GUI: К4/К3/прогресс). В процессе ручного
smoke обнаружено: К2 «2. Исправить код» не активируется после К1, потому что
критерий DS_133 требует *.plp в result, а result создаётся только в К2.
Замкнутый круг: К2 не активна → К2 нельзя нажать → result не создаётся.

Решение (вариант A + X):
- A: при К1 создавать пустой PATCH_OUT (прогноз результата).
- X: критерий К2 = source_ok AND source_has_plp (в source есть файлы по шаблону).

Ветка feature/dockerization, Ollama available, GUI SRC\gui_app.py.

## Симптомы

- После К1 (диалог «Сканирование завершено» → ОК):
  - PATCH_OUT не создан (ожидаемо по DS_133, но ломает workflow).
  - К2 остаётся тонкой (disabled).
  - Индикатор КР: «будет создан» (не обновляется на «доступен»).
- Пользователь не может запустить К2 без ручного создания result.

## Причины

1. `start_scan` (L3266-3291) НЕ создаёт result — только читает source.
   Result создаётся в `start_fix` (L3832-3836).
2. `_update_main_buttons` (L1330-1331): `k2_normal = has_plp`, где
   `has_plp = result_ok AND _result_dir_has_pattern_files()`. Пустой result → False.

## Правки

### Правка A (УЖЕ ПРИМЕНЕНА) — создание PATCH_OUT в start_scan

В `start_scan`, после проверки `source_dir.exists()` (L3280), вставлено:

    # DS_136: создать пустой PATCH_OUT (прогноз результата) сразу при К1
    auto_result = self._auto_fill_result_dir(source_dir)
    if auto_result and not auto_result.exists():
        try:
            auto_result.mkdir(parents=True, exist_ok=True)
            self.result_dir_var.set(str(auto_result))
            self.log(f"Создан пустой каталог результатов (прогноз): {auto_result}", 'info')
        except Exception as e:
            self.log(f"Не удалось создать каталог результатов: {e}", 'warning')

`_auto_fill_result_dir` сам вызывает `result_dir_var.set()` → сработает trace
L2097 → `_update_dir_indicators()` → индикатор обновится на «доступен».

### Правка B1 — новая функция _source_dir_has_pattern_files

Вставить после L1290 (после `_result_dir_has_pattern_files`):

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
            if '**' in pattern:
                gen = p.glob(pattern)
            elif self.scan_recursive_var.get():
                gen = p.rglob(pattern)
            else:
                gen = p.glob(pattern)
            return any(True for _ in gen)
        except Exception:
            return False

### Правка B2 — _update_main_buttons (L1330-1331)

Было:
    has_plp = result_ok and self._result_dir_has_pattern_files()
    k2_normal = has_plp

Стало:
    has_plp = result_ok and self._result_dir_has_pattern_files()
    source_has_plp = source_ok and self._source_dir_has_pattern_files()
    k2_normal = source_has_plp

### Правка B3 — вызов тултипов (L1352-1355)

Было:
    self._update_main_buttons_tooltips(
        k1_normal=k1_normal, k2_normal=k2_normal, k3_normal=k3_normal,
        source_ok=source_ok, pattern_ok=pattern_ok, rule_ok=rule_ok,
        result_ok=result_ok, has_plp=has_plp, ai_in_empty=ai_in_empty)

Стало (добавлен source_has_plp):
    self._update_main_buttons_tooltips(
        k1_normal=k1_normal, k2_normal=k2_normal, k3_normal=k3_normal,
        source_ok=source_ok, pattern_ok=pattern_ok, rule_ok=rule_ok,
        result_ok=result_ok, has_plp=has_plp, ai_in_empty=ai_in_empty,
        source_has_plp=source_has_plp)

### Правка B4 — сигнатура тултипов (L1361-1363)

Было:
    def _update_main_buttons_tooltips(self, k1_normal, k2_normal, k3_normal,
                                        source_ok, pattern_ok, rule_ok,
                                        result_ok, has_plp, ai_in_empty):

Стало (добавлен source_has_plp с дефолтом):
    def _update_main_buttons_tooltips(self, k1_normal, k2_normal, k3_normal,
                                        source_ok, pattern_ok, rule_ok,
                                        result_ok, has_plp, ai_in_empty,
                                        source_has_plp=False):

### Правка B5 — тултип К2 (L1376-1382)

Было:
    if not result_ok:
        k2_tip = "Каталог результатов недоступен или недоступен на запись."
    elif not has_plp:
        k2_tip = "В каталоге результатов нет файлов по шаблону."
    else:
        k2_tip = "Автоматически исправить найденные проблемы."

Стало:
    if not source_ok:
        k2_tip = "Укажите существующий исходный каталог."
    elif not source_has_plp:
        k2_tip = "В исходном каталоге нет файлов по шаблону."
    else:
        k2_tip = "Автоматически исправить найденные проблемы."

Тултип К3 (L1391-1400) НЕ трогаем — он привязан к has_plp в result, что
правильно (К3 активируется после К2).

## Тесты (SRC\tests\test_ds133_buttons_state.py)

Добавить:

1. test_k2_normal_when_source_has_plp — source с *.plp, result пуст →
   btn_fix.state(['!disabled']), style 'WorkflowActive.TButton'.
2. test_k2_disabled_when_source_empty — source без *.plp → btn_fix disabled,
   style 'WorkflowNormal.TButton'.

## §5 Проверка

1. python -m pytest SRC\tests\ -q → ожидается 65 passed, exit=0.
2. python SRC\tests\test_ds133_buttons_state.py → ожидается 18/18, exit=0.
3. ast.parse gui_app.py → OK.
4. Ручной smoke (Vitaly):
   - Перезапустить GUI.
   - К1 на каталоге с *.plp → PATCH_OUT создан, индикатор «доступен»,
     К2 жирная.
   - К2 → диалог «Исправление завершено» → ОК.
   - К3 «3. В Ai» жирная. Прогресс 0%. К1/К2 жирные.
5. BOM-check: gui_app.py, test_ds133_buttons_state.py — UTF-8 без BOM.

## Ограничения

- Правка A уже применена (см. выше).
- Правка B1-B5 — новые.
- Тултип К3 не менять.
- settings.json — не трогать в этом DS.

## Артефакты

- Отчёт: EXCHANGE\OUTBOX\DS_136_gui_patchout_k2_activation_report.md.
- Задание: EXCHANGE\PROCESSED\DS_136_gui_patchout_k2_activation.md.
- bot.log — обновить (правило 29: до коммита).