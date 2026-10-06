# DS_089a — Прерывание / Продолжение (UI + mid-file abort)

Дата: 30.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация | Приоритет: высокий
Зависит от: DS_088b, DS_089_DIAG | Блокирует: DS_089b
См.: DS_STANDARD.md (§2, §3, §5)

---

## 1. Цель

Реализовать единый механизм **прерывания / продолжения** для трёх операций:

A. **Кнопка «Прервать» / «Продолжить»** — переключение надписи по клику, обратно.

B. **Mid-file abort в scanner** — проверка `abort_callback()` внутри
   `scan_file` (**строка 1256** — начало построчного цикла).

C. **`abort_callback` в `code_fixer.py`** — добавить в `__init__` (530)
   + проверка в `fix_directory` (1669).

D. **`rule_based_fixer`** — `Popen` + мониторинг + `terminate()`
   (вместо `subprocess.run`).

E. **Логирование** в ЖВ + `bot.log` с временными метками.

F. **Прогноз времени** до прерывания — в ЖВ.

**НЕ МЕНЯТЬ:** логику `send_to_ai`, `receive_from_ai`, `ai_local_worker`,
пороги confidence, layout, `fix_file` (атомарен).

**AI-цикл — НЕ возобновляется** (при «Прервать» → «Продолжить» → новый цикл
с пометкой в ЖВ). Resume — в DS_089b (скан / фикс).

**ВАЖНО — фактический workspace:**
- `SRC\analyzer\scanner.py` (2634 стр.) — НЕ `SRC\scanner.py`.
- `SRC\fixer\code_fixer.py` (2605 стр.).

**Уже реализовано (НЕ дублировать):**
- `abort_callback` в `PLPlusScanner.__init__` (479, 485).
- Проверка между файлами в `scan_directory` (1680).
- Передача из `gui_app.py:3267–3270` (скан).

**Не реализовано:**
- Mid-file abort в `scan_file`.
- `abort_callback` в `PLPlusFixer`.
- Передача в `gui_app.py:3786` (фикс).

---

## 2. Что делать

### 2.1. Разведка (уточнить перед правкой)

| Что | Где | Статус |
|-----|-----|--------|
| `scan_aborted` | `gui_app.py:287` | ✅ есть |
| `_abort_requested()` | `gui_app.py:1704–1706` | ✅ есть |
| `on_abort_click` | `gui_app.py:1682–1702` | ✅ есть |
| `_start_abortable_operation` | `gui_app.py:1715` | ✅ есть |
| `_finish_abortable_operation` | `gui_app.py:1730` | ✅ есть |
| `btn_abort` | `gui_app.py` | ✅ есть |
| `scan_file` | `SRC\analyzer\scanner.py:1221` | ✅ |
| Построчный цикл | `scanner.py:1256` | ✅ |
| Цикл по паттернам | `scanner.py:1269` | ✅ |
| Цикл по match | `scanner.py:1287` | ✅ |
| `scan_directory` — проверка | `scanner.py:1680` | ✅ есть |
| `PLPlusFixer.__init__` | `SRC\fixer\code_fixer.py:530` | ❌ нет `abort_callback` |
| `fix_directory` | `code_fixer.py:1600` | ✅ |
| Цикл по файлам | `code_fixer.py:1669` | ✅ |
| `fix_file` | `code_fixer.py:1495` | ✅ атомарен |
| `rule_based_fixer` вызов | `gui_app.py` | `subprocess.run` |
| ЖВ (`log_text`) | `gui_app.py` | ✅ |

**РАЗВИЛКА-СТОП:**
- Если `scan_file` (1256) **не цикл** `for` — СТОП.
- Если `rule_based_fixer` **не имеет** stdout — СТОП.

### 2.2. Кнопка «Прервать» / «Продолжить» (часть A)

**Текущее:** `on_abort_click` (1682–1702) — guard, `scan_aborted=True`,
`btn_abort` в `disabled`.

**Новое:**
- **Надпись** `btn_abort`: «Прервать» ↔ «Продолжить».
- **По клику** «Прервать» → `scan_aborted = True`, надпись → «Продолжить».
- **По клику** «Продолжить» → `scan_aborted = False`, надпись → «Прервать».
- **Кнопка активна только во время операции** (`normal`/`disabled`).

**Логика:**

```python
def on_abort_click(self):
    if not self.scan_running:
        return
    if not self.scan_aborted:
        # ПРЕРЫВАТЬ
        self.scan_aborted = True
        self._progress_frozen = True
        self.btn_abort.config(text="Продолжить")
        self._log_to_journal("[HH:MM:SS] Операция прервана пользователем")
        log.info("Операция прервана пользователем")
    else:
        # ПРОДОЛЖИТЬ
        self.scan_aborted = False
        self._progress_frozen = False
        self.btn_abort.config(text="Прервать")
        self._log_to_journal("[HH:MM:SS] Операция продолжена")
        log.info("Операция продолжена")
2.3. Mid-file abort в scanner (часть B)
Точка A (1256) — начало построчного цикла:

python
def scan_file(self, file_path, log_callback=None):
    # ... подготовка ...
    for line_num, line in enumerate(self.lines, 1):
        if self.abort_callback and self.abort_callback():
            # прерывание между строками
            return partial_issues  # issues, собранные до этой строки
        # ... обработка строки (1269, 1287) ...
Результат: scan_file возвращает частичный результат.
scan_directory (1680) прерывает цикл по файлам.

Точку B (1269) — не добавлять (per KODA: минимальное влияние на
производительность, чистое состояние).

2.4. abort_callback в code_fixer.py (часть C)
Шаг 1. PLPlusFixer.__init__ (530) — добавить параметр:

python
def __init__(self, config, iteration, clean_output=None,
             abort_callback=None, ...):
    # ...
    self.abort_callback = abort_callback
Шаг 2. fix_directory — цикл по файлам (1669):

python
for idx, (file_path_str, issues) in enumerate(...):
    if self.abort_callback and self.abort_callback():
        break  # прерывание между файлами
    # ... обработка файла ...
Внутри файла — НЕ трогать. fix_file (1495) атомарен (Stage1 + Stage2).

Шаг 3. gui_app.py:3786 — передать abort_callback:

python
fixer = PLPlusFixer(config, iteration, clean_output=...,
                    abort_callback=self._abort_requested)
2.5. rule_based_fixer — Popen (часть D)
Сейчас: subprocess.run([...], timeout=600).

Заменить на:

python
proc = subprocess.Popen(
    [sys.executable, "tools/rule_based_fixer.py", ...],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
self._monitor_worker(proc)  # общий метод из DS_088a
_monitor_worker (DS_088a) — проверяет self._abort_requested() после
каждой строки stdout. При True → proc.terminate() + proc.wait().

2.6. Логирование (часть E)
В ЖВ:

Прерывание: [HH:MM:SS] Операция прервана пользователем.

Продолжение: [HH:MM:SS] Операция продолжена.

Досрочное завершение: [HH:MM:SS] Операция завершена досрочно.

В bot.log: те же метки (log.info).

2.7. Прогноз времени (часть F)
При нажатии «Прервать»:

python
# Скан:
avg_time = elapsed / files_done
remaining = total_files - files_done
eta_sec = avg_time * remaining
# AI:
eta_sec = 30  # грубо
Формат в ЖВ:

text
[HH:MM:SS] Мягкое прерывание запрошено.
[HH:MM:SS] Текущий файл будет дочитан, затем операция остановится.
[HH:MM:SS] Прогноз: прерывание через ~N сек (осталось M файлов).
2.8. AI-цикл — не возобновляется (часть G)
При «Прервать» в AI-цикле:

scan_aborted = True → _run_ai_cycle прерывается (проверка после
строки stdout / итерации ожидания).

proc.terminate() для воркера.

При «Продолжить»: новый цикл (не resume).

Пометка в ЖВ:

text
[HH:MM:SS] Операция не возобновляется. Новый цикл — по кнопке «3. В Ai».
3. Тесты
#	Тест	Ожидание
1	Надпись «Прервать» при старте	при scan_running=True
2	Клик «Прервать»	scan_aborted=True, надпись «Продолжить»
3	Клик «Продолжить»	scan_aborted=False, надпись «Прервать»
4	Кнопка disabled вне операции	при scan_running=False
5	Mid-file abort (scanner 1256)	прерывание внутри scan_file
6	code_fixer.py — abort_callback в __init__	параметр добавлен
7	fix_directory (1669) — проверка	прерывание между файлами
8	gui_app.py:3786 — передача	abort_callback=self._abort_requested
9	rule_based_fixer — Popen	мониторинг + terminate()
10	Логирование ЖВ	«прервана» / «продолжена» / «досрочно»
11	Логирование bot.log	те же метки
12	Прогноз в ЖВ	«~N сек»
13	AI-цикл — не возобновляется	пометка в ЖВ
14	Регресс DS_086/087/088a/088a_fix/088b	PASSED
4. Ограничения
Правка: SRC\gui_app.py, SRC\analyzer\scanner.py (только проверка
в scan_file:1256), SRC\fixer\code_fixer.py (только __init__:530 +
fix_directory:1669).

НЕ МЕНЯТЬ: tools\ai_local_worker.py, tools\rule_based_fixer.py
(только вызов из GUI), SRC\ai_exchange.py, SRC\rule_engine.py.

НЕ МЕНЯТЬ: fix_file (1495) — атомарен.

Логи: EXCHANGE\bot.log + ЖВ. temp\ — можно.

GIT — НЕ КОММИТИТЬ.

5. Отчёт (OUTBOX\DS_089a_report.md)
5.1. Разведка — подтверждение строк.
5.2. Кнопка — надпись, флаг, disabled/normal.
5.3. Mid-file abort — что добавлено (1256).
5.4. code_fixer.py — __init__ (530), fix_directory (1669),
gui_app.py:3786.
5.5. rule_based_fixer — Popen + мониторинг.
5.6. Логирование — формат.
5.7. Прогноз — формат.
5.8. AI-цикл — пометка.
5.9. Тесты 1–14 — PASSED/FAILED.
5.10. Расхождения / стоп.

6. Артефакты
SRC\gui_app.py (правка)

SRC\analyzer\scanner.py (правка — проверка в scan_file:1256)

SRC\fixer\code_fixer.py (правка — __init__, fix_directory)

EXCHANGE\OUTBOX\DS_089a_report.md

(опционально) SRC\tests\test_ds089a.py