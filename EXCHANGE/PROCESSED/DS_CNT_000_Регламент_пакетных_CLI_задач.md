# DS_CNT_000. Регламент пакетных CLI-задач (CNT = Ai-Continue, ночной режим)

## Цель
Утвердить единый регламент пакетных (неинтерактивных) CLI-задач
для Ai-Continue (CNT) в TO_DBI. Обязателен для всех DS_CNT_001..NNN.
Выполняется ПЕРВЫМ.

## Предусловия
- Репозиторий F:\TO_DBI, ветка feature/dockerization.
- Ai-Continue установлен, Ollama на порту 11434.
- MCP shell и MCP-скрипт НЕ используются. Только CLI и `.cmd`/`.ps1`.
- LM Studio не запущен.
- Каталоги `F:\TO_DBI\logs`, `F:\TO_DBI\tools` — существуют или создаются.

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа. Не путать.
- Пакетная задача — CLI-задача без интерактива. Ночная — по расписанию.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

---

## 1. Принципы пакетного режима

1.1. **Без интерактива** — все параметры через CLI/ENV/конфиг.
1.2. **Без MCP shell** — только `ai-continue`, `ollama`, `git`, `python`.
1.3. **Единый вывод** — лог/код/ошибки/отчёт по форматам разделов 2–4.
1.4. **Стоп при ошибке** — ненулевой код → останов, без обходов.
1.5. **Эскалация** — `.err` + отчёт в OUTBOX + уведомление Vitaly.
1.6. **Идемпотентность** — повтор не ломает; «already done» → код 0.
1.7. **Изоляция** — у каждой задачи свой набор `ds_cnt_<NNN>*`.
1.8. **Порядок блоков `config.yaml`:** models → slashCommands →
embeddingsProvider → mcpServers.
1.9. **Lock от параллельного запуска:** `F:\TO_DBI\logs\ds_cnt_<NNN>.lock`.
Есть lock → код 1, запись в `.err`. Снимается по завершении.
Содержимое lock — PID + время старта.
Если lock существует дольше N часов (N — по согласованию с
Администратором АРМа), он считается «зависшим». Не удалять
автоматически. Эскалация.
1.10. **Проверка предыдущего этапа.** Задача с номером <NNN> (кроме 000)
проверяет, что `ds_cnt_<NNN-1>.exit` существует и содержит 0.
Иначе — код 1, эскалация.

---

## 2. Логи

2.1. Файл: `F:\TO_DBI\logs\ds_cnt_<NNN>[_<step>].log`.
2.2. Строка: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [STEP] message`,
где LEVEL ∈ {INFO, WARN, ERROR, OK}.
2.3. Логируется: старт, шаги, ошибки, финиш (код + время).
2.4. Ротация: по умолчанию — перезапись. Архив
`ds_cnt_<NNN>_<YYYYMMDD>.log` — по согласованию с Администратором АРМа.

---

## 3. Коды возврата

3.1. Файл: `F:\TO_DBI\logs\ds_cnt_<NNN>.exit` — одно число:
- 0 — успех (в т.ч. already done);
- 1 — общая ошибка (в т.ч. lock, предыдущий этап);
- 2 — валидация (конфиг, YAML, структура);
- 3 — зависимость (Ollama, модель, MCP);
- 4 — права (ACL, доступ, запись в logs);
- 5 — индексация/данные;
- >5 — резерв.

3.2. Файл ошибок: `F:\TO_DBI\logs\ds_cnt_<NNN>.err` — текст последней
ошибки, перезапись при запуске.

---

## 4. Отчёт

4.1. Файл: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_<NNN>_report.md`.
4.2. Шаблон: `EXCHANGE\DS_089b_report.md` (приложение А).
4.3. Если шаблона нет — создать на шаге 4.

---

## 5. Шаблон скрипта ночной задачи

5.1. Файл: `F:\TO_DBI\tools\run_cnt_<NNN>_nightly.cmd`.
5.2. Структура — по шаблону `F:\TO_DBI\tools\_template_nightly.cmd`
(создаётся в DS_CNT_000, шаг 3). Обязательные элементы:
- проверка lock (код 1 при наличии);
- создание lock с PID + временем;
- `:check_deps` — проверка предыдущего этапа (код 1), Ollama/модели
  (код 3), каталоги и запись в logs (код 4);
- `:run_main` — основная логика;
- запись кода в `.exit`, снятие lock (успех и ошибка);
- запись ошибки в `.err`.
5.3. Требования: без интерактива, абсолютные пути, коды 1/2/3/4/5.

---

## 6. Порядок и расписание

6.1. Порядок строгий: 000 → 001 → 002 → 003 → 004 → 005.
6.2. Следующая запускается только при коде 0 предыдущей
(проверяется в `:check_deps`, см. п. 1.10).
6.3. Окно 01:00–05:00, последовательно, lock обязателен.
Точное время — по согласованию с Администратором АРМа.

---

## 7. Мониторинг и эскалация

7.1. Утро: проверка `ds_cnt_*.exit` и `ds_cnt_*.err`, отсутствие
«зависших» lock-файлов.
7.2. Эскалация при: код ≠ 0; ошибка в `.err`; нет лога/отчёта; lock.
7.3. Куда: `.err` + отчёт в OUTBOX + уведомление ИБ (при инцидентах).
Контакты — `EXCHANGE\SEC_POLICY_AI.md`, раздел 12.5.
7.4. НЕ делать: не обходить ошибку; не менять allow-list; не писать
в DATA/EXCHANGE/PATCH_IN; не использовать внешние AI; не удалять lock
вручную без выяснения причины.

---

=== КОНЕЦ РЕГЛАМЕНТА ===
Далее — шаги выполнения DS_CNT_000 (в регламент не копируются).

---

## 8. Шаги выполнения DS_CNT_000

### Шаг 1. Каталоги
Проверить/создать: `F:\TO_DBI\logs`, `F:\TO_DBI\tools`,
`F:\TO_DBI\EXCHANGE\OUTBOX`.

### Шаг 2. `F:\TO_DBI\EXCHANGE\DS_CNT_000_regulation.md`
Скопировать разделы 1–7 (до `=== КОНЕЦ РЕГЛАМЕНТА ===`) с заголовком
(приложение Б).

### Шаг 3. `F:\TO_DBI\tools\_template_nightly.cmd`
Создать шаблон по разделу 5 (полный код — приложение В).
Затем создать `run_cnt_000_nightly.cmd` на его основе.

### Шаг 4. `F:\TO_DBI\EXCHANGE\DS_089b_report.md`
Создать, если нет (приложение А).

### Шаг 5. Пакетная проверка
Запустить `run_cnt_000_nightly.cmd`. Проверить:
`ds_cnt_000.exit` = 0, лог заполнен, `.err` пуст, lock удалён,
отчёт в OUTBOX.

### Шаг 6. `agents-short.md`
Добавить раздел (приложение Г).

---

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- MCP — только локальные.
- Соблюдать матрицу доступа.
- Не путать `logs` и `EXCHANGE\bot.log`.

## Артефакты
- `EXCHANGE\DS_CNT_000_regulation.md` — регламент.
- `EXCHANGE\DS_089b_report.md` — шаблон отчёта.
- `tools\_template_nightly.cmd` — шаблон скрипта.
- `tools\run_cnt_000_nightly.cmd` — скрипт задачи.
- `.continue\rules\agents-short.md` — раздел «Пакетный ночной режим».
- `logs\ds_cnt_000.log`, `ds_cnt_000.exit`, `ds_cnt_000.err`.
- Отчёт: `EXCHANGE\OUTBOX\DS_CNT_000_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы: Что сделано / Что проверено /
Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. `DS_CNT_000_regulation.md` создан (разделы 1–7).
2. `DS_089b_report.md` создан.
3. `_template_nightly.cmd` создан.
4. `run_cnt_000_nightly.cmd` создан и проверен.
5. `agents-short.md` содержит раздел «Пакетный ночной режим (DS_CNT_000)».
6. Пакетный запуск — код 0.
7. Lock удалён.
8. Отчёт в `EXCHANGE\OUTBOX\DS_CNT_000_report.md`.

---

## Приложение А. Шаблон `EXCHANGE\DS_089b_report.md`

```markdown
# Отчёт DS_CNT_<NNN>

## Что сделано
- ...

## Что проверено
- ...

## Результат
- Успех / Ошибка (код <N>).

## Проблемы
- ...

## Следующие шаги
- ...
```

## Приложение Б. Заголовок `DS_CNT_000_regulation.md`

```markdown
# DS_CNT_000. Регламент пакетных CLI-задач (CNT = Ai-Continue, ночной режим)

Статус: утверждён.
Дата: <YYYY-MM-DD>.
Ответственный за AI-контур: Vitaly.

(далее — разделы 1–7 из DS_CNT_000)
```

## Приложение В. Шаблон `tools\_template_nightly.cmd`

```cmd
@echo off
setlocal
REM === DS_CNT_<NNN> nightly runner ===
REM Лог/Код/Ошиб/Lock: F:\TO_DBI\logs\ds_cnt_<NNN>.*

set LOG=F:\TO_DBI\logs\ds_cnt_<NNN>.log
set EXIT=F:\TO_DBI\logs\ds_cnt_<NNN>.exit
set ERR=F:\TO_DBI\logs\ds_cnt_<NNN>.err
set LOCK=F:\TO_DBI\logs\ds_cnt_<NNN>.lock

REM --- Шаг 0: lock ---
if exist "%LOCK%" (
  echo [%DATE% %TIME%] [ERROR] [lock] already running >> "%LOG%"
  echo 1 > "%EXIT%"
  echo lock exists > "%ERR%"
  exit /b 1
)
echo %DATE% %TIME% > "%LOCK%"

echo [%DATE% %TIME%] [INFO] [start] DS_CNT_<NNN> >> "%LOG%"

call :check_deps
if errorlevel 1 goto :fail
call :run_main
if errorlevel 1 goto :fail

echo 0 > "%EXIT%"
echo [%DATE% %TIME%] [OK] [finish] DS_CNT_<NNN> >> "%LOG%"
del "%LOCK%"
exit /b 0

:fail
echo %ERRORLEVEL% > "%EXIT%"
echo [%DATE% %TIME%] [ERROR] [finish] DS_CNT_<NNN> >> "%LOG%"
del "%LOCK%"
exit /b %ERRORLEVEL%

:check_deps
REM --- Проверка предыдущего этапа (код 1, кроме 000) ---
REM Для <NNN>=000 эту проверку убрать.
if not exist "F:\TO_DBI\logs\ds_cnt_<NNN-1>.exit" exit /b 1
for /f %%i in (F:\TO_DBI\logs\ds_cnt_<NNN-1>.exit) do if not "%%i"=="0" exit /b 1

REM --- Проверка Ollama и моделей (код 3) ---
where ollama >nul 2>&1 || exit /b 3
ollama list | findstr "qwen2.5-coder:7b" >nul || exit /b 3
ollama list | findstr "qwen2.5-coder:1.5b-base" >nul || exit /b 3
ollama list | findstr "nomic-embed-text" >nul || exit /b 3

REM --- Проверка каталогов (код 4) ---
if not exist "F:\TO_DBI\logs" exit /b 4
if not exist "F:\TO_DBI\tools" exit /b 4
if not exist "F:\TO_DBI\EXCHANGE\OUTBOX" exit /b 4

REM --- Проверка записи в logs (код 4) ---
echo test > "F:\TO_DBI\logs\_write_test.tmp" 2>nul || exit /b 4
del "F:\TO_DBI\logs\_write_test.tmp" >nul 2>&1

exit /b 0

:run_main
REM Основная логика задачи.
REM Возврат: 0 — успех, 2/3/4/5 — ошибка.
exit /b 0
```

## Приложение Г. Раздел для `agents-short.md`

```markdown
## Пакетный ночной режим (DS_CNT_000)
- Регламент: EXCHANGE\DS_CNT_000_regulation.md.
- Логи: F:\TO_DBI\logs\ds_cnt_<NNN>*.log.
- Коды: F:\TO_DBI\logs\ds_cnt_<NNN>.exit.
- Ошибки: F:\TO_DBI\logs\ds_cnt_<NNN>.err.
- Lock: F:\TO_DBI\logs\ds_cnt_<NNN>.lock.
- Отчёты: F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_<NNN>_report.md.
- Запуск: F:\TO_DBI\tools\run_cnt_<NNN>_nightly.cmd.
- Шаблон: F:\TO_DBI\tools\_template_nightly.cmd.
- Порядок: 000 → 001 → 002 → 003 → 004 → 005.
- Проверка предыдущего этапа — обязательна.
- При ошибке — не обходить, эскалировать.
- Полная политика ИБ: EXCHANGE\SEC_POLICY_AI.md (DS_CNT_002).
```