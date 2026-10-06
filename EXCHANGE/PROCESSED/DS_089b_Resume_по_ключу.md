# DS_089b — Resume по ключу (скан / фикс)

Дата: 02.10.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация | Приоритет: высокий
Зависит от: DS_089a (принят), DS_089_DIAG | Блокирует: DS_090
См.: DS_STANDARD.md (§2, §3, §5)

---

## 1. Цель

Реализовать **возобновление** прерванных операций:

A. **Сохранение состояния** при прерывании: ключи обработанных issues
   (для скана) + список обработанных файлов (для фикса).

B. **Resume scanner** — пересканировать + фильтр по ключам
   `(file_path, line_number, issue_type, description, match_fragment)`.

C. **Resume code_fixer** — пропуск обработанных файлов (идемпотентен, F6).

D. **Логирование** resume в ЖВ + `bot.log`.

**НЕ МЕНЯТЬ:** логику `send_to_ai`, `receive_from_ai`, `ai_local_worker`,
пороги confidence, layout.

**AI-цикл — НЕ возобновляется** (при «Продолжить» → новый цикл
с пометкой в ЖВ). Resume — только для скана / фикса.

---

## 1a. Уже реализовано в workspace (НЕ дублировать)

**DS_089a (принят):**
- `self._stop_event = threading.Event()` (`gui_app.py:294`).
- `_stop_event.set()` (1695) / `.clear()` (1718).
- `stop_event` в `PLPlusScanner` (480) + `PLPlusFixer` (531).
- Проверки `stop_event.is_set()` в `scanner.py` (1264, 1714) +
  `code_fixer.py` (1681).
- `abort_callback` — **также** работает (совместимость).
- `_stop_event` в вызовах из GUI: 3150, 3313, 3643, 3803, 3838.

**Не реализовано (этот DS):**
- `_abort_state` (0 совпадений).
- `_resume_scan` (0 совпадений).
- `_resume_fix` (0 совпадений).
- Логирование resume.

---

## 2. Что делать

### 2.1. Разведка (уточнить перед правкой)

| Что | Где | Статус |
|-----|-----|--------|
| `_stop_event` | `gui_app.py:294` | ✅ есть |
| `on_abort_click` | `gui_app.py:1682–1702` | ✅ есть |
| `scan_aborted` | `gui_app.py:287` | ✅ есть (сохраняется) |
| `scan_file` (mid-file abort) | `SRC\analyzer\scanner.py:1256` | ✅ есть |
| `scan_directory` | `scanner.py:1678–1701` | ✅ есть |
| `code_fixer.py` (abort_callback) | `SRC\fixer\code_fixer.py:1678` | ✅ есть |
| **Ключ дедупликации** | `scanner.py:1626–1627` | ❓ уточнить: точные поля |
| `scan_results` | `gui_app.py:264` (dict) | ✅ |
| `_log_to_journal` | `gui_app.py` | ✅ |
| Сохранение в `settings.json` | `gui_app.py` (DS_086) | ✅ |

**РАЗВИЛКА-СТОП:**
- Если ключ дедупликации **не** `(file_path, line_number, issue_type,
  description, match_fragment)` — СТОП, вопрос автору.
- Если `scan_results` **не** расширяется — СТОП.

### 2.2. Сохранение состояния (часть A)

**При прерывании** (`on_abort_click` → `scan_aborted = True`) — **добавить**
(в **дополнение** к `_stop_event.set()`):

```python
self._abort_state = {
    'operation': 'scan' | 'fix',
    'scan_results': <частичный результат>,
    'processed_keys': [<ключи issue>],     # для скана
    'processed_files': [<пути файлов>],    # для фикса
    'current_file': <path>,
    'timestamp': <time>,
}
processed_keys — из scan_results (issues до прерывания).
Ключ: (file_path, line_number, issue_type, description, match_fragment).
Формат ключа — из scanner.py:1626–1627 (уточнить разведкой).

processed_files — файлы, завершённые до прерывания (для фикса).

2.3. Resume scanner (часть B)
При «Продолжить» (_stop_event.clear() + scan_aborted = False) —
проверить self._abort_state:

Если есть и operation == 'scan':

Пересканировать файлы (read-only, идемпотентно).

Отфильтровать issues с сохранёнными ключами.

Продолжить с новыми issues.

Логика:

python
def _resume_scan(self):
    prev_keys = set(self._abort_state['processed_keys'])
    # Пересканировать
    new_results = scanner.scan_directory(...)
    # Отфильтровать
    for issue in new_results:
        key = (issue.file_path, issue.line_number, issue.issue_type,
               issue.description, issue.match_fragment)
        if key not in prev_keys:
            self.scan_results['issues'].append(issue)
    self._abort_state = None  # очистить
2.4. Resume code_fixer (часть C)
При «Продолжить» — проверить self._abort_state:

Если есть и operation == 'fix':

Пропустить файлы, уже обработанные.

Продолжить с оставшихся.

Из DS_089_DIAG (F6): resume на уровне файлов идемпотентен.

Логика:

python
def _resume_fix(self):
    processed_files = set(self._abort_state['processed_files'])
    for file_path, issues in fix_tasks:
        if file_path in processed_files:
            continue  # пропустить
        # ... обработка файла ...
2.5. AI-цикл — не возобновляется (часть D)
При «Продолжить» после AI-цикла:

Не resume.

Пометка в ЖВ: [HH:MM:SS] AI-цикл не возобновляется. Новый цикл — по кнопке «3. В Ai».

python
if self._abort_state and self._abort_state['operation'] == 'ai':
    self._log_to_journal("[HH:MM:SS] AI-цикл не возобновляется. Новый цикл — по кнопке «3. В Ai»")
    self._abort_state = None
    return
2.6. Логирование (часть E)
В ЖВ:

При сохранении состояния: [HH:MM:SS] Состояние сохранено: N issues, M файлов.

При resume: [HH:MM:SS] Возобновление с N issues (пропущено M).

При завершении resume: [HH:MM:SS] Операция возобновлена и завершена.

В bot.log: те же метки (log.info).

3. Тесты
#	Тест	Ожидание
1	Сохранение состояния при прерывании скана	_abort_state заполнен
2	Сохранение processed_keys	ключи issues до прерывания
3	Сохранение processed_files	файлы до прерывания (фикс)
4	Resume scanner	пересканировать + фильтр
5	Resume scanner — пропуск обработанных	нет дублей
6	Resume scanner — новые issues	добавлены
7	Resume code_fixer	пропуск обработанных файлов
8	Resume code_fixer — идемпотентность	фикс по частям = фикс всех
9	AI-цикл — не возобновляется	пометка в ЖВ
10	Логирование resume	«Возобновление с N issues»
11	Логирование завершения	«Операция возобновлена»
12	Регресс DS_086/087/088a/088a_fix/088b/089a	PASSED
4. Ограничения
Правка: SRC\gui_app.py, SRC\analyzer\scanner.py (только resume),
SRC\fixer\code_fixer.py (только resume).

НЕ МЕНЯТЬ: tools\, SRC\ai_exchange.py, SRC\rule_engine.py.

НЕ ТРОГАТЬ: _stop_event (DS_089a), abort_callback (DS_089a).

Логи: EXCHANGE\bot.log + ЖВ. temp\ — можно.

GIT — НЕ КОММИТИТЬ.

5. Отчёт (OUTBOX\DS_089b_report.md)
5.1. Разведка — ключ дедупликации, структура scan_results.
5.2. Сохранение состояния — где, как (processed_keys + processed_files).
5.3. Resume scanner — где, как.
5.4. Resume code_fixer — где, как.
5.5. AI-цикл — пометка.
5.6. Логирование — формат.
5.7. Тесты 1–12 — PASSED/FAILED.
5.8. Расхождения / стоп.

6. Артефакты
SRC\gui_app.py (правка)

SRC\analyzer\scanner.py (правка — resume)

SRC\fixer\code_fixer.py (правка — resume)

EXCHANGE\OUTBOX\DS_089b_report.md

(опционально) SRC\tests\test_ds089b.py