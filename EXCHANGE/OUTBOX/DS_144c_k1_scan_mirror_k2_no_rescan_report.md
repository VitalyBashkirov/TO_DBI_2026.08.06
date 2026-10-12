# DS_144c — K1=скан+зеркало; K2 без повторного скана

**Дата:** 2026-10-12
**Автор DS:** DeepSeek
**Пользователь:** Vitaly
**Ветка:** feature/dockerization
**Базовый коммит:** 71f98f5 (DS_144b)

## Цель

1. K1 (`_run_scan`): после сканирования выполнить зеркало ИК→КР (тот же `_copy_files_to_result`, что в K2).
2. K2 (`_run_fix`): убрать повторный `scanner.scan_directory`, использовать `scanner` из K1.
3. Прогресс-бар K1: добавить шаг копирования.

## Решения (согласованы с Vitaly)

| Вопрос | Решение |
|--------|---------|
| В1: `edited_files` в K1 | always `only_edited=False`, `edited_files=None` (K1 = полное зеркало) |
| В2: K2 без K1 | fail-fast: лог + диалог + `return` |
| В3: прогресс K1 | 90→98 (копирование); при `aborted` — 100 + «K1 прерван: <причина>» + return |
| K2-копирование | K2a — убрать (K1 делает зеркало) |
| Вставка зеркала в K1 | после `_progress_update(50)` |
| `_progress_update(50)` | оставить как есть |

## Изменения в SRC\gui_app.py

### K1 (`_run_scan`)

После `self._progress_update(50)` вставлен блок:

~~~python
# DS_144c: зеркало ИК -> КР (только если скан не прерван).
if not self.scan_aborted:
    self.root.after(0, lambda: self.log(
        "\n[ЗЕРКАЛО] Копирование ИК -> КР...", 'info'))
    self._progress_update(90)
    _copy_res = self._copy_files_to_result(
        source_dir=Path(config['paths']['source_dir']),
        result_dir=Path(config['paths']['results_dir']),
        pattern=self.file_pattern_var.get(),
        preserve_structure=self.preserve_structure_var.get(),
        only_edited=False,
        edited_files=None,
    )
    if _copy_res.get('aborted'):
        _abort_msg = _copy_res['aborted']
        self._progress_update(100)
        self.root.after(0, lambda m=_abort_msg: self.log(
            f"[!] K1 прерван: {m}", 'error'))
        self.root.after(0,
            lambda m=_abort_msg: self._show_copyable_dialog(
                "Ошибка", m, kind="error"))
        return
    self._progress_update(98)
    self.root.after(0, lambda c=_copy_res: self.log(
        f"  Скопировано: {c['copied']}, пропущено: {c['skipped']}, "
        f"ошибок: {c['errors']}", 'info'))
~~~
### K2 (`_run_fix`)

**A — создание сканера:** удалено `from analyzer.scanner import PLPlusScanner ... fix_flags=self._current_header_flags())`; добавлено:

~~~python
# DS_144c: K2 без повторного скана — используем scanner из K1.
_k1 = getattr(self, 'scan_results', None) or {}
scanner = _k1.get('scanner')
if scanner is None:
    _msg = "Сначала выполните сканирование (K1)."
    self.log(f"[!] {_msg}", 'error')
    self.root.after(0, lambda m=_msg: self._show_copyable_dialog(
        "Ошибка", m, kind="error"))
    return
scan_results = _k1.get('stats') or {}
~~~

**B — убрать scan_directory:** удалено `scan_results = scanner.scan_directory(log_callback=scan_log)`.

**C — убрать копирование в K2:** удалён весь блок `# DS_144b: копирование файлов...` до `self._progress_update(40)`.

**D — упростить final_results_dir:**

~~~python
# DS_144c K2a: зеркало уже сделано в K1 -> работаем поверх result_dir.
final_results_dir = result_dir
~~~

## Тесты

Создан `SRC\tests\test_ds144c_k1_k2_pytest.py` (8 тестов):

1. `test_ds144c_k1_calls_copy_with_full_mirror` — K1 вызывает `_copy_files_to_result(only_edited=False, edited_files=None)`.
2. `test_ds144c_k1_aborted_progress_100` — K1 при `aborted` → прогресс 100.
3. `test_ds144c_k1_scan_aborted_no_copy` — K1 при `scan_aborted=True` копирование не вызывает.
4. `test_ds144c_k2_no_scan_results_failfast` — K2 без `scan_results` → fail-fast.
5. `test_ds144c_k2_no_scanner_failfast` — K2 без `scanner` → fail-fast.
6. `test_ds144c_k2_no_rescan` — K2 не вызывает `scan_directory`.
7. `test_ds144c_k2_no_copy` — K2 не вызывает `_copy_files_to_result`.
8. `test_ds144c_k2_final_dir_is_result_dir` — `final_results_dir == result_dir`.

## Результаты

| Проверка | Результат |
|----------|-----------|
| ast.parse | OK |
| pytest 8 тестов | 8 passed |
| pytest полный регресс | 144 passed (136 + 8) |
| Размер gui_app.py | 356907 → 356566 B (−341 B) |
| Строк gui_app.py | 6240 → 6237 (−3) |

## Артефакты

- Бэкап: `tools\_archive\gui_app.py.bak_ds144c`
- Тест: `SRC\tests\test_ds144c_k1_k2_pytest.py` (9890 B)
- Отчёт: `EXCHANGE\OUTBOX\DS_144c_k1_scan_mirror_k2_no_rescan_report.md`

## Открытые долги

- **DS_144c2:** звук при `aborted` в K1 (сейчас играет звук успеха в `finally`, т.к. `scan_aborted=False` при `_copy_res['aborted']`).
- **N7 v7:** очистка `PS\` в **каждом** PS-блоке (уточнение к N7 v6, в `DS_STANDARD.md` §6.6.23).
## Дополнение: DS_144c2 — звук при aborted в K1

**Дата:** 2026-10-12
**Мотивация:** при `_copy_res['aborted']` в K1 (после правки DS_144c) играл звук успеха — потому что `self.scan_aborted` остаётся `False` (скан-то прошёл, прервали только копирование). Логически K1 — прерван.

**Решение (Вариант B, согласован с Vitaly):** отдельный флаг `self._k1_copy_aborted`.

### Изменения в SRC\gui_app.py

**Правка 1 — K1, ветка `aborted`:**

~~~python
if _copy_res.get('aborted'):
    _abort_msg = _copy_res['aborted']
    # DS_144c2: пометить, что K1 прерван по aborted (для звука в finally).
    self._k1_copy_aborted = True
    self._progress_update(100)
    ...
    return
~~~

**Правка 2 — K1, `finally` (уточнённый anchor — только K1):**

~~~python
self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
# DS_088b §2.2: звук завершения (scan_aborted ещё не сброшен).
# DS_144c2: при aborted копирования в K1 — тоже звук ошибки.
_sound_ok = (not self.scan_aborted) and (
    not getattr(self, '_k1_copy_aborted', False))
~~~

**Правка 3 — K1, начало метода (сброс флага):**

~~~python
# DS_088b §2.2: замер длительности для звука завершения.
_op_start = time.time()
# DS_144c2: сброс флага «K1 прерван по aborted» при новом запуске.
self._k1_copy_aborted = False
~~~

### Тест

Добавлен `test_ds144c2_k1_aborted_flag_set`:
- При `_copy_res['aborted']` — флаг `_k1_copy_aborted=True`.
- Звук завершения — `False` (звук ошибки).

### Результаты

| Проверка | Результат |
|----------|-----------|
| ast.parse | OK |
| pytest 9 тестов | 9 passed |
| pytest полный регресс | 145 passed (136 + 8 + 1) |
| Размер gui_app.py | 356566 → 357058 B (+492) |
| Строк gui_app.py | 6237 → 6243 (+6) |

### Артефакт

- Бэкап: `tools\_archive\gui_app.py.bak_ds144c2` (356566 B)