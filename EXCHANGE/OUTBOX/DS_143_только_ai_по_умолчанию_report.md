# DS_143 — «Только Ai»: поведение галки и запись only_ai в шапки

## Шапка

- **DS:** DS_143
- **Автор:** DeepSeek
- **Пользователь:** Vitaly
- **Дата:** 11.10.2026
- **Ветка:** feature/dockerization
- **База:** 92c25ea
- **Предшественники:** DS_140 (pytest-миграция), DS_142 (§6.6.10-§6.6.17)

## §1. Цель

1. Поведение галки chk_ai_only = поведение K3 btn_to_ai:
   state='normal' <=> k3_normal = has_plp AND ai_in_empty.
2. Запись only_ai в шапки артефактов:
   - убрать из scan_report_*.md (K1);
   - убрать из save_scan_only_log (K2);
   - добавить в AI_REQUEST_*.md (K3);
   - добавить в AI_RESPONSE_*.md (K4);
3. Метод _current_header_flags очистить от only_ai; новый метод
   _only_ai_flag() — для K3/K4.

## §2. Объём работ

### 2.1. SRC/gui_app.py

| # | Место | Действие |
|---|-------|----------|
| C.1 | _update_main_buttons (1373) | Добавлено управление chk_ai_only по k3_normal |
| C.2 | _run_scan (3594-3595) | Удалён вызов _append_only_ai_flag_line |
| C.3 | _current_header_flags (2886) | Убран flags['only_ai']; добавлен _only_ai_flag() |
| C.4 | _run_ai_cycle (5960-5985) | Проброс --only-ai V/x в воркеры |
| D.2 | send_to_ai (5492) | flags.update(self._only_ai_flag()) |

### 2.2. SRC/ai_exchange.py

| # | Место | Действие |
|---|-------|----------|
| D.1 | flags_line (91) | Ветка only_ai (подвариант A2) |

### 2.3. tools/rule_based_fixer.py

| # | Место | Действие |
|---|-------|----------|
| E.1 v2 | write_response (295) | Параметр only_ai + строка в шапке |
| E.1 v2 | argparse (342) | Флаг --only-ai {V,x} |
| E.1b | process_request (318) | Параметр only_ai + проброс |
| E.1b | main (358, 373) | Проброс args.only_ai в 2 вызова |

### 2.4. tools/ai_local_worker.py

| # | Место | Действие |
|---|-------|----------|
| E.2 | write_response (562) | Параметр only_ai + строка |
| E.2 | build_parser (915) | Флаг --only-ai |
| E.2 | main (943) | cfg['only_ai'] = args.only_ai |
| E.2 | run_request (833) | Проброс only_ai=cfg.get('only_ai','V') |

### 2.5. SRC/tests/test_ds143_ai_only_pytest.py (новый, 8 тестов)

- 3 теста flags_line (без/с True/с False);
- 2 теста write_request (only_ai=V, only_ai=x);
- 3 теста chk_ai_only (exists, state=k3_normal, _only_ai_flag).

## §3. Ключевые решения

### 3.1. Галка = K3

В _update_main_buttons после цикла state K1/K2/K3 добавлен блок:

    chk = getattr(self, 'chk_ai_only', None)
    if chk is not None:
        if k3_normal:
            chk.state(['!disabled'])
        else:
            chk.state(['disabled'])

### 3.2. only_ai в шапках (подвариант A2)

flags_line не перебирает FLAG_ORDER для only_ai. Добавлена
отдельная ветка:

    if flags and 'only_ai' in flags:
        on = bool(flags.get('only_ai', False))
        parts.append(f"only_ai={'V' if on else 'x'}")

Печатается только если передан. Обратная совместимость сохранена.

### 3.3. Проброс в воркеры

_run_ai_cycle формирует only_ai_arg = 'V' if ai_only else 'x'
и передаёт --only-ai в оба Popen (rule_based_fixer, ai_local_worker).

## §4. Результаты

### 4.1. Тесты

    pytest SRC/tests/ -q
    118 passed in ~26s

110 старых (без регресса) + 8 новых DS_143.

### 4.2. Smoke

- K1: галка disabled (K3 не активна);
- K2: галка disabled;
- K3: галка normal (K3 активна);
- K4: галка disabled.
- scan_report_*.md: нет only_ai;
- AI_REQUEST_*.md: only_ai=V/x в строке Флаги:;
- AI_RESPONSE_*.md: only_ai=V/x в шапке.

### 4.3. git diff

    SRC/ai_exchange.py        |   5 +
    SRC/gui_app.py            |  22 +- (C.1-C.4, D.2)
    tools/rule_based_fixer.py |  16 +- (E.1v2, E.1b)
    tools/ai_local_worker.py  |   8 +- (E.2)

## §5. Файлы

### Изменённые

- SRC/gui_app.py (C.1-C.4, D.2)
- SRC/ai_exchange.py (D.1)
- tools/rule_based_fixer.py (E.1 v2, E.1b)
- tools/ai_local_worker.py (E.2)

### Новые

- SRC/tests/test_ds143_ai_only_pytest.py (8 тестов)
- EXCHANGE/PROCESSED/DS_143_только_ai_по_умолчанию.md (задание)

### Бэкапы

- tools/_archive/gui_app.py.bak_ds143 (до C.1)
- tools/_archive/gui_app.py.bak_ds143_after_c2
- tools/_archive/gui_app.py.bak_ds143_after_c3
- tools/_archive/gui_app.py.bak_ds143_after_c4
- tools/_archive/gui_app.py.bak_ds143_after_d2
- tools/_archive/ai_exchange.py.bak_ds143 (до D.1)
- tools/_archive/ai_exchange.py.bak_ds143_after_d1
- tools/_archive/rule_based_fixer.py.bak_ds143 (до E.1)
- tools/_archive/ai_local_worker.py.bak_ds143 (до E.2)

## §6. Итог

DS_143 закрыт. Галка «Только Ai» ведёт себя как K3. Запись only_ai
перенесена из K1/K2 в K3/K4. Тесты зелёные (118 passed).
