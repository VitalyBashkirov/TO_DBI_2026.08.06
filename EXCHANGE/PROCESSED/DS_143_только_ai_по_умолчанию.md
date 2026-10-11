# DS_143 — «Только Ai»: поведение галки и запись only_ai в шапки

## Шапка

- **DS:** DS_143
- **Автор:** DeepSeek
- **Пользователь:** Vitaly
- **Дата:** 11.10.2026
- **Ветка:** feature/dockerization
- **База:** 92c25ea
- **Sync:** origin/feature/dockerization (без ahead/behind)
- **Предшественники:** DS_140 (pytest-миграция), DS_142 (§6.6.10–§6.6.17)
- **Статус:** в работе

## §1. Цель

1. **Поведение галки `chk_ai_only` = поведение K3 `btn_to_ai`**:
   `state='normal'` <=> `k3_normal = has_plp AND ai_in_empty`.
   (Правка в `_update_main_buttons`.)

2. **Запись `only_ai` в шапки артефактов:**

   - **убрать** из `scan_report_*.md` (K1) — удалить
     `_append_only_ai_flag_line` (gui_app.py:3595);
   - **убрать** из `save_scan_only_log` (K2) — не передавать
     `only_ai` в `fix_flags` при вызовах K1/K2;
   - **добавить** в `AI_REQUEST_*.md` (K3) — в строку `Флаги:`;
   - **добавить** в `AI_RESPONSE_*.md` (K4) — через CLI-флаг
     `--only-ai` в воркеры.

3. **`_current_header_flags` очистить от `only_ai`.** Новый
   отдельный метод `_only_ai_flag()` -> `{'only_ai': True/False}`
   используется только там, где нужно (K3, K4).

## §2. Объём работ

### 2.1. gui_app.py

| # | Место | Действие |
|---|-------|----------|
| 1 | _update_main_buttons (после 1371) | Добавить state галки по k3_normal |
| 2 | _run_scan (3594–3595) | Удалить self._append_only_ai_flag_line(output_path) |
| 3 | _current_header_flags (2886) | Убрать flags['only_ai'] = ... |
| 4 | Добавить метод _only_ai_flag() | Возвращает {'only_ai': bool(...)} |
| 5 | K3 — send_to_ai (5490) | Оставить чтение ai_only_var.get() — оно уже правильное |
| 6 | K3 — _run_ai_cycle (5947) | Передать --only-ai воркерам rule_based_fixer.py и ai_local_worker.py |
| 7 | K4 — receive_from_ai | (если нужно) добавить запись в лог/бот-лог |

### 2.2. SRC/ai_exchange.py

| # | Место | Действие |
|---|-------|----------|
| 1 | build_request_text (129) | Добавить only_ai=V/x в строку Флаги: |
| 2 | write_request (217) | Прокинуть only_ai в build_request_text (или в flags) |

### 2.3. tools/rule_based_fixer.py

| # | Место | Действие |
|---|-------|----------|
| 1 | argparse | Добавить --only-ai (значения V/x, default V) |
| 2 | Функция формирования AI_RESPONSE_*.md | Добавить строку only_ai=V/x в шапку |

### 2.4. tools/ai_local_worker.py

| # | Место | Действие |
|---|-------|----------|
| 1 | argparse | Добавить --only-ai |
| 2 | Функция формирования AI_RESPONSE_*.md | Добавить only_ai=V/x в шапку |

### 2.5. SRC/tests/

Новые тесты (pytest):

- **Галка chk_ai_only:**
  - state='disabled' при scan_results=None;
  - state='normal' при k3_normal=True;
  - state='disabled' при AI_IN непусто;
- **only_ai в шапках:**
  - отсутствует в scan_report_*.md;
  - отсутствует в save_scan_only_log (K2);
  - присутствует в AI_REQUEST_*.md в Флаги:;
  - присутствует в AI_RESPONSE_*.md в шапке.

Оценка: ~6–8 новых тестов.

## §3. Ограничения

- Не трогать EXCHANGE/OUTBOX/DS_CNT_007_pilot_report.md (M в git status).
- Не запускать KODA; все DS — вручную PowerShell (правило F, DS_125).
- BOM: .py/.md/.json/.ini/.sql — UTF-8 без BOM; .ps1 с кириллицей — с BOM.
- Не открывать LM Studio одновременно с Ollama.
- Тесты — только SRC/tests/, без правок SRC/ без явного указания.
- N7 v6 для всех PS-блоков: очистка PS\, кроме активного лога и PS\persist\.

## §4. Контекст: анализ F:\\TO_DBI\\ollama_lms.log

### 4.1. Назначение файла

ollama_lms.log — журнал переключений между двумя локальными AI-бэкендами:

- **Ollama** — http://localhost:11434;
- **LM Studio** — второй локальный сервер (используется в DS_CNT_007).

Файл лежит в корне проекта. Формат — плоский, без уровня
(INFO/WARN/ERROR), без PID и ID сессии.

### 4.2. Словарь событий

| Метка | Смысл |
|-------|-------|
| UNLOAD_BOTH | выгрузка обеих моделей из RAM |
| START_OLLAMA_SERVER | подъём демона Ollama |
| OK: ollama server started | демон поднят |
| START_CODER: model=... | загрузка кодер-модели |
| START_CHAT_MODEL: model=... | загрузка чат-модели (llama3.1:8b) |
| config updated: model=... batch=... | правка ai_local_worker_config.json |
| OLLAMA_LOAD_CHOSEN: ... | выбор Ollama-модели через GUI |
| LMS_LOAD_CHOSEN: ... / OK: LMS model loaded | выбор LM Studio-модели |
| KILL_LMS | принудительная остановка LM Studio |
| ERROR: coder load failed | сбой загрузки модели |
| EXIT | завершение воркера/GUI |

### 4.3. Хронология (сводка)

| Дата | События | Оценка |
|------|---------|--------|
| 02.10 | deepseek-coder:6.7b OK -> KILL_LMS | штатно |
| 03.10 | ERROR: coder load failed (10:30:43), пачки UNLOAD_BOTH, START_CODER без OK | проблемный день |
| 04.10 | только EXIT | простой |
| 05.10 | OLLAMA_LOAD_CHOSEN qwen2.5-coder:3b, LMS_LOAD_CHOSEN local-bank@q3_k_m OK | эксперименты |
| 06.10 | два KILL_LMS, два EXIT | тишина |
| 07.10 | START_OLLAMA_SERVER OK, переход на qwen2.5-coder:7b, 4x START_CODER подряд, закрытие трека CNT | насыщенный |
| 08-11.10 | только KILL_LMS x4 | хвост без запусков |

### 4.4. Наблюдения

1. **Асимметрия гигиены.**
   KILL_LMS — 16 раз, START_OLLAMA_SERVER — 5, OK: ollama server started — 4.
   LM Studio гасят чаще, чем поднимают Ollama. Обратной гигиены
   (KILL_OLLAMA перед LMS) в логе нет.

2. **Пачки UNLOAD_BOTH.**
   03.10 (x3), 05.10 (x4+x3), 07.10 (x2) — либо многократные нажатия кнопки,
   либо отсутствие идемпотентности в обработчике.

3. **Неполные пары START_CODER -> OK/config updated.**
   03.10 11:23 и 11:44; 07.10 01:59 и 02:01 — START_CODER есть,
   подтверждения нет.

4. **Единственный явный сбой — 03.10 10:30:43.**
   START_CODER deepseek-coder:6.7b (10:29:32) -> через ~71 сек
   ERROR: coder load failed. Вероятная причина — нехватка RAM/VRAM.

5. **Дубли config updated.**
   07.10: запись model=qwen2.5-coder:7b batch=10 — четыре раза
   с интервалом 5-40 мин.

6. **Хвост 08-11.10 — KILL_LMS без START_*.**
   Автоматика гасит LMS и ничего не запускает; либо ручная чистка
   после экспериментов DS_CNT_007.

### 4.5. Рекомендации (вход в DS_143)

| № | Рекомендация | Приоритет |
|---|--------------|-----------|
| R1 | Найти писателя лога: grep -r ollama_lms.log F:\\TO_DBI\\SRC F:\\TO_DBI\\tools | высокий |
| R2 | Ввести уровень (INFO/WARN/ERROR) + ID сессии + PID | средний |
| R3 | Сделать UNLOAD_BOTH идемпотентным | средний |
| R4 | Воспроизвести сбой 03.10 | высокий |
| R5 | При «только Ai» — KILL_LMS + START_OLLAMA_SERVER автоматически на старте | высокий |
| R6 | Проверить дубли START_CODER при config updated | средний |

### 4.6. Связь с DS_143

- «Только Ai» как дефолт означает: связка
  KILL_LMS -> START_OLLAMA_SERVER -> START_CODER выполняется
  автоматически при старте АРМ.
- Пачки UNLOAD_BOTH и хвост KILL_LMS без START_* исчезают
  по определению — их порождает ручное переключение.
- Сбой 03.10 (coder load failed) — риск и для DS_143: при неудаче
  автоматического старта должен быть диагностируемый ERROR.

### 4.7. Результаты разведки R-A и recon-2/3/4

**Галка chk_ai_only (gui_app.py:1005):**

- создаётся хардкодом `tk.BooleanVar(value=True)`;
- не сохраняется в settings.json;
- не имеет `.state(...)` — всегда активна;
- читается в двух местах: `_current_header_flags` (2886) и `send_to_ai` (5490).

**K1–K4 (btn_scan/btn_fix/btn_to_ai/btn_from_ai):**

- состояние управляется в `_update_main_buttons` (1318–1382)
  по артефактам на диске;
- `k3_normal = has_plp AND ai_in_empty`.

**Цепочка использования ai_only:**

| K | Читает ai_only? | Что делает |
|---|-----------------|------------|
| K1 | да (2886) | _append_only_ai_flag_line -> scan_report_*.md |
| K2 | да (2886) | fixer.flags -> save_scan_only_log -> шапка фиксера |
| K3 | да (5490) | filter_ai_issues — реальная фильтрация issues |
| K4 | нет | — |

**Форматы шапок (recon-4):**

- scan_report_*.md — есть блок «Флаги замены», строка only_ai: V;
- save_scan_only_log — то же;
- AI_REQUEST_*.md — своя шапка (## Метаданные, строка Флаги: regex=V, ...),
  only_ai в ней НЕТ;
- AI_RESPONSE_*.md — своя шапка (Источник, Дата, Исправлений),
  только_ai в ней НЕТ.

## §5. Проверка

1. `pytest SRC/tests/ -q` -> 110 + N passed (N = новые).
2. Ручной smoke:
   - K1 -> галка disabled (K3 не активна);
   - K2 -> галка disabled;
   - K3 -> галка normal;
   - K4 -> галка disabled;
   - scan_report_*.md — нет only_ai;
   - AI_REQUEST_*.md — only_ai=V/x в Флаги:;
   - AI_RESPONSE_*.md — only_ai=V/x в шапке.

## §6. Результат

- [ ] Правки в gui_app.py.
- [ ] Правки в SRC/ai_exchange.py.
- [ ] Правки в tools/rule_based_fixer.py, tools/ai_local_worker.py.
- [ ] Тесты зелёные.
- [ ] Отчёт EXCHANGE/OUTBOX/DS_143_только_ai_по_умолчанию_report.md.
- [ ] Запись в EXCHANGE/bot.log.
- [ ] Коммит + push.
