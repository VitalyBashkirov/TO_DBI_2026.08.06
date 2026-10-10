# DS_141 — Кириллица U+FFFD в ЖВ. Отчёт

**Дата:** 2026-10-10
**Чат:** 30
**Автор DS:** DeepSeek
**Пользователь:** Vitaly
**Тип:** Правка кода (кодировка)
**Статус:** ✅ Выполнен

## Причина

При работе AI-цикла (К3) русский текст от ai_local_worker.py
отображался в Журнале выполнения (Tkinter Text) как U+FFFD (�).

Диагностика:
- ai_local_worker.py пишет в sys.stdout в системной кодировке
  Windows (cp1251/cp866). Своего переключения на UTF-8 НЕ имеет.
- gui_app.py читает stdout воркера через iter(proc.stdout.readline, b'')
  → raw.decode('utf-8', errors='replace') (строка ~5859).
- UTF-8-декодер на cp1251-байтах даёт U+FFFD.

rule_based_fixer.py проверен — уже переключает sys.stdout на UTF-8
внутри main() (строки 333-336). НЕ трогали.

## Действие (вариант C — belt and suspenders)

### tools/ai_local_worker.py (после блока импортов)

    # DS_141: принудительный UTF-8 для stdout/stderr, чтобы кириллица не
    # превращалась в U+FFFD при чтении GUI (см. Урок EE).
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                      errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8',
                                      errors='replace')

### SRC/gui_app.py — 2 точки Popen

Перед каждым Popen (rule_based_fixer, ai_local_worker):

    env_ai = dict(os.environ, PYTHONIOENCODING='utf-8')
    proc = subprocess.Popen([...], ..., env=env_ai)

## Результат

| Параметр | Было | Стало |
|----------|------|-------|
| ai_local_worker.py | 1018 строк | 1027 строк (+9) |
| gui_app.py | 6059 строк | 6063 строк (+4) |
| BOM (оба) | False | False |
| ast.parse (оба) | — | OK |
| ai_local_worker.py --check | — | OK |
| pytest | 77 passed | 77 passed |
| DS_133 | 18/18 | 18/18 PASSED |
| DS_086 | 15/15 | 15/15 PASSED |

## Проверки

- ast.parse OK для обоих файлов.
- ai_local_worker.py --check: ollama available.
- pytest exit=0, 77 passed.
- DS_133 exit=0, 18/18.
- DS_086 exit=0, 15/15.

## Инцидент

Шаг 3 (первая попытка фикса gui_app.py) — fail-fast по
WildcardPatternException: оператор -like в PowerShell трактует
символы [ ] как wildcard-класс. Заменено на $content.Contains($old).
Файл НЕ пострадал (ast.parse OK, +0 байт). См. Урок JJJ (новый).

## Артефакты

- Задание: EXCHANGE\PROCESSED\DS_141_utf8_ai_worker.md
- Отчёт: EXCHANGE\OUTBOX\DS_141_utf8_ai_worker_report.md
- Логи: PS\ds141_*.log (7 файлов)
- Бэкапы: ai_local_worker.py.bak_ds141, gui_app.py.bak_ds141,
  gui_app.py.bak_ds141v2

## Уроки

- Урок DD подтверждён (Python-код в PS-консоли → ParserError).
- Урок EE закрыт (ai_local_worker теперь пишет UTF-8).
- Новый Урок JJJ (для DS_STANDARD §6.6.x): -like в PowerShell —
  wildcard, не строковое сравнение. Для .Contains — только .Contains.

## Замечание

EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md — modified ДО начала
DS_141 (вероятно ночной pipeline CNT). В коммит DS_141 не включён.

## bot.log

Запись добавлена.