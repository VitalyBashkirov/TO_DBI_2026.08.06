# DS_CNT_001..005. Настройка Ai-Continue (CNT) в TO_DBI

## Цель
Выполнить настройку Ai-Continue (CNT) в TO_DBI за пять этапов (001–005)
в пакетном ночном режиме, согласно `EXCHANGE\DS_CNT_000_regulation.md`.

Этапы:
1. (001) `agents-short.md` + slashCommands.
2. (002) `SEC_POLICY_AI.md` + ссылка в `agents-short.md`.
3. (003) Заполнить раздел 12.4 `SEC_POLICY_AI.md`.
4. (004) `mcpServers` в `config.yaml` + ACL.
5. (005) `@codebase`-индексация.

## Предусловия и общие требования
См. `EXCHANGE\DS_CNT_000_regulation.md`:
- предусловия — раздел «Предусловия»;
- терминология — раздел «Терминология»;
- матрица доступа (роль АРМ) — раздел «Матрица доступа»;
- форматы логов/кодов/ошибок/отчётов — разделы 2–4;
- шаблон скрипта `_template_nightly.cmd` — раздел 5;
- порядок запуска — раздел 6;
- мониторинг и эскалация — раздел 7.

Дополнительно для этого DS:
- DS_CNT_000 выполнен (`regulation.md`, `_template_nightly.cmd`,
  `DS_089b_report.md` созданы);
- подтверждения ИБ по пунктам 2, 3, 6, 7 получены;
- учётка `svc_mcp` создана (для этапа 004);
- MCP shell и MCP-скрипт НЕ используются.

Каждый этап выполняется через
`tools\run_cnt_<NNN>_nightly.cmd` на основе `_template_nightly.cmd`.
Специфика `:run_main` — в этапах ниже.
Проверка предыдущего этапа (код 1) — в `:check_deps` каждого скрипта
(кроме 000), согласно регламенту, п. 1.10.

---

## Этап 001. agents-short.md + slashCommands
Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7).
Обновить `agents-short.md`, добавить 8 slash-команд в `config.yaml`.

### Шаг 001.1. Обновить `agents-short.md`
Содержимое:

```markdown
# TO_DBI. Правило для Ai-Continue (CNT)

## Роль
CNT (Ai-Continue) — помощник в редакторе (Chat / Edit / Apply /
Autocomplete / Embed). НЕ исполнитель. Исполнитель DS — KODA.
CNT не пишет вне разрешённых каталогов, не делает git без указания.

## Контекст проекта
- Проект TO_DBI. АРМ «Адаптация под DBI».
- Перевод PL/SQL (Oracle) → PostgreSQL (DBI).
- Репозиторий F:\TO_DBI, ветка feature/dockerization.

## Ссылки
- EXCHANGE\DS_STANDARD.md — стандарт DS.
- EXCHANGE\DS_FILES.md, DS_CONTEXT.md — файлы и контекст.
- EXCHANGE\DS_089b_report.md — шаблон отчёта.
- EXCHANGE\test_ds089b.py — шаблон unittest.
- EXCHANGE\DS_CNT_000_regulation.md — регламент ночных задач.
- AGENTS.md — инструкция KODA (справочник).

## Формат DS (Text Copy Download)
Два блока: имя файла (code-блок) + содержимое DS.
Без прогноза KODA.

## Регламент
- Логи операций АРМа — F:\TO_DBI\logs.
- Лог АРМа — F:\TO_DBI\EXCHANGE\bot.log.
- Отчёты — F:\TO_DBI\EXCHANGE\OUTBOX\.
- GIT — только по запросу.
- SRC не трогать без указания.
- LM Studio + Ollama одновременно — запрещено.
- Пакетный режим — без интерактива.

## Матрица доступа (роль АРМ)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Запреты
- Не формировать DS на правку SRC, ai_local_worker, rule_based_fixer,
  scanner, code_fixer.
- Не дублировать задачи чата 9 (DS_090).
- Не использовать внешние AI.

## MCP (когда будет включён)
- Локальные MCP: shell (allow-list), git (read-only),
  filesystem (rw: logs, PATCH_OUT; ro: DATA, EXCHANGE, PATCH_IN).
- Внешние MCP запрещены.
- CNT не пишет в DATA, EXCHANGE, PATCH_IN.
- CNT не делает git push/commit без указания.

## Ограничения ИБ (кратко)
- Локальные модели (Ollama, 11434) и локальные MCP-серверы.
- Внешние AI и облачные MCP — запрещены.
- Логи — F:\TO_DBI\logs. Лог АРМа — EXCHANGE\bot.log.
- При отказе — не обходить, эскалировать.
- Пакетный режим: EXCHANGE\DS_CNT_000_regulation.md.
```

### Шаг 001.2. Добавить блок `slashCommands` в `config.yaml`
8 команд. Существующие блоки не трогать.
Порядок: models → slashCommands → embeddingsProvider → mcpServers.

```yaml
slashCommands:
  - name: ds-template
    description: Черновик DS по шаблону DS_STANDARD.md
    prompt: |
      Ты — автор DS в TO_DBI. Стандарт: EXCHANGE\DS_STANDARD.md.
      Сформируй заготовку DS по теме: {{{ input }}}.
      Структура: Цель / Предусловия / Шаги / Ограничения / Артефакты /
      Формат отчёта / Критерии успеха.
      DS — Text Copy Download (два блока: имя файла + содержимое).
      SRC не трогать без указания. GIT — по запросу. Без прогноза KODA.

  - name: report
    description: Черновик отчёта в EXCHANGE\OUTBOX по шаблону DS_089b_report.md
    prompt: |
      Ты — автор отчёта в TO_DBI. Шаблон: EXCHANGE\DS_089b_report.md.
      Сформируй отчёт по теме: {{{ input }}}.
      Отчёт — в EXCHANGE\OUTBOX\. Без прогноза KODA.

  - name: check-standard
    description: Ревью файла на соответствие DS_STANDARD.md (раздел 2)
    prompt: |
      Проверь файл на соответствие EXCHANGE\DS_STANDARD.md (раздел 2).
      Укажи нарушения и правки. SRC не трогать без указания.
      Файл: {{{ input }}}

  - name: explain-log
    description: Разбор последних 200 строк EXCHANGE\bot.log (лог АРМа)
    prompt: |
      Разбери последние 200 строк EXCHANGE\bot.log.
      Ошибки, предупреждения, аномалии. Шаги диагностики.
      Только EXCHANGE\bot.log.

  - name: gen-test
    description: Заготовка unittest по шаблону test_ds089b.py
    prompt: |
      Сформируй заготовку unittest по шаблону EXCHANGE\test_ds089b.py.
      Тема: {{{ input }}}. SRC не трогать без указания.

  - name: mcp-shell
    description: Пилот — CLI через MCP shell (после включения MCP)
    prompt: |
      Через MCP shell выполни: {{{ input }}}.
      Локальные команды. Без записи вне разрешённых каталогов.

  - name: mcp-git
    description: Пилот — git status через MCP git (после включения MCP)
    prompt: |
      Через MCP git выполни: git status.
      Без commit/push/checkout. Только чтение.

  - name: mcp-write
    description: Пилот — запись в PATCH_OUT через MCP filesystem
    prompt: |
      Через MCP filesystem запиши тестовый файл в PATCH_OUT\.
      Имя: {{{ input }}}. Другие каталоги не трогать.
```

### Специфика `run_cnt_001_nightly.cmd`
`:check_deps`:
- проверка `ds_cnt_000.exit` = 0 (код 1);
- YAML-синтаксис `config.yaml` (код 2).

`:run_main`:
- `agents-short.md` содержит 9 разделов (Роль, Контекст проекта, Ссылки,
  Формат DS, Регламент, Матрица доступа, Запреты, MCP, Ограничения ИБ);
- `config.yaml` содержит 8 slash-команд;
- порядок блоков `config.yaml`: models → slashCommands (код 2).

### Результат этапа 001
- Отчёт: `EXCHANGE\OUTBOX\DS_CNT_001_report.md`.
- Код: `logs\ds_cnt_001.exit` = 0.
- Lock: `logs\ds_cnt_001.lock` удалён.

---

## Этап 002. SEC_POLICY_AI.md + ссылка в agents-short.md
Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7).
Создать `SEC_POLICY_AI.md`, дополнить `agents-short.md` ссылкой.

### Шаг 002.1. Создать `SEC_POLICY_AI.md`
Содержимое:

```markdown
# SEC_POLICY_AI.md — Политика ИБ по AI и MCP в TO_DBI

Статус: черновик, требует согласования с ИБ.
Версия: 0.1.

## 1. Область применения
Распространяется на сотрудников, AI-ассистентов (CNT/KODA/ai_local_worker),
MCP-серверы, локальные LLM (Ollama). Не распространяется на штатные
средства без AI и средства ИБ.

## 2. Термины
AI/LLM, CNT (Ai-Continue), KODA, ai_local_worker, MCP, локальный контур,
внешний сервис, чувствительные данные, allow-list.

## 3. Матрица доступа TO_DBI

| Каталог | Администратор АРМа | Пользователь АРМа | АРМ | ИБ |
|---|---|---|---|---|
| DATA | add/del/ren/read/write | read | read | read |
| EXCHANGE | add/del/ren/read/write | read | read | read |
| EXCHANGE\<подкаталоги> | add/del/ren/read/write | read | read | read |
| logs | — | read | add/del/ren/read/write | read |
| PATCH_IN | add/del/ren/read/write | add/del/ren/read/write | read | read |
| PATCH_OUT | read | add/del/ren/read/write | add/del/ren/read/write | read |

## 4. Общие принципы
Закрытый контур. Локальность данных. Минимизация прав. Явное согласие.
Аудит. Ответственность — на сотруднике.

## 5. Разрешённые технологии
5.1. LLM: qwen2.5-coder:7b, qwen2.5-coder:1.5b-base, nomic-embed-text
(embed). Локально через Ollama, 11434.
5.2. MCP: shell (allow-list), git (read-only),
filesystem (rw: logs, PATCH_OUT; ro: DATA, EXCHANGE, PATCH_IN).
5.3. Версии — из внутреннего реестра.

## 6. Запрещённые технологии
Внешние AI. Облачные MCP. MCP из публичных реестров. MCP с сетью/БД/
системными каталогами/секретами. LM Studio + Ollama одновременно.

## 7. Ограничения на действия AI
Без явного указания: не писать вне разрешённых каталогов; не трогать
SRC, ai_local_worker, rule_based_fixer, scanner, code_fixer; не делать
commit/push/merge/rebase/checkout; не запускать произвольные shell;
не читать вне воркспейса; не отправлять данные вовне; не ставить пакеты.

## 8. Ограничения на данные
Не передавать в промпт: пароли, токены, ключи, ПДн, банковскую тайну,
фрагменты SRC без согласования, содержимое .git/.env, системные каталоги.

## 9. Логирование и аудит
Логи операций АРМа — F:\TO_DBI\logs. Лог АРМа — EXCHANGE\bot.log.
Логи ночных задач — F:\TO_DBI\logs\ds_cnt_<NNN>*.log.
Срок хранения 3–12 мес. Доступ: сотрудник, ИБ, руководитель.
Аудит: еженедельно, внепланово при инциденте.

## 10. Ответственность
Ответственность за действие AI — на сотруднике. Нарушение —
дисциплинарная. Инциденты — по регламенту банка.

## 11. Порядок согласования
11.1. MCP-сервер: заявка → ревью ИБ → решение → allow-list → config.
11.2. LLM: заявка → ревью (telemetry, cloud fallback) → решение →
allow-list → Ollama.
11.3. Расширение прав MCP: заявка → ревью → решение → обновление.

## 12. Приложения
12.1. Allow-list MCP-серверов (таблица).
12.2. Allow-list команд shell.
12.3. Шаблон записи лога MCP.
12.4. Чек-лист перед внедрением MCP (заполняется в DS_CNT_003).
12.5. Контакты: ИБ, руководитель, Vitaly.
```

### Шаг 002.2. Обновить `agents-short.md`
Добавить в конец блок:

```markdown
## Ограничения ИБ (кратко)
- Локальные модели (Ollama, 11434) и локальные MCP-серверы.
- Внешние AI и облачные MCP — запрещены.
- MCP: shell (allow-list), git (read-only),
  filesystem (rw: logs, PATCH_OUT; ro: DATA, EXCHANGE, PATCH_IN).
- CNT не пишет в DATA, EXCHANGE, PATCH_IN.
- CNT не делает commit/push/checkout без указания.
- CNT не читает SRC, .git, секреты, системные каталоги.
- SRC, ai_local_worker, rule_based_fixer, scanner, code_fixer — не трогать.
- Логи — F:\TO_DBI\logs. Лог АРМа — EXCHANGE\bot.log.
- LM Studio + Ollama одновременно — запрещено.
- Пакетный режим — без интерактива.

Полная политика ИБ: EXCHANGE\SEC_POLICY_AI.md.
```

### Специфика `run_cnt_002_nightly.cmd`
`:check_deps`:
- проверка `ds_cnt_001.exit` = 0 (код 1);
- YAML-синтаксис `config.yaml` (код 2).

`:run_main`:
- `SEC_POLICY_AI.md` содержит 12 разделов + матрицу доступа в разделе 3;
- `agents-short.md` содержит блок «Ограничения ИБ» и ссылку.

### Результат этапа 002
- Отчёт: `EXCHANGE\OUTBOX\DS_CNT_002_report.md`.
- Код: `logs\ds_cnt_002.exit` = 0.
- Lock: `logs\ds_cnt_002.lock` удалён.

---

## Этап 003. Заполнение раздела 12.4 SEC_POLICY_AI.md
Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7).
Заменить пустой чек-лист в разделе 12.4 на заполненный.

### Шаг 003.1. Заполнить раздел 12.4
Содержимое:

```markdown
### 12.4. Чек-лист перед внедрением MCP (заполненный)

#### 1. Версия Ai-Continue поддерживает MCP
- Вопрос ИБ: какая версия, поддерживает ли MCP?
- Типовой ответ: MCP с 0.9.x (блок mcpServers).
- Что делать: зафиксировать; если < 0.9.x — обновить/отложить.
- Статус: требует проверки на АРМ.

#### 2. Политика ИБ банка получена и учтена
- Вопрос ИБ: есть ли политика по AI/MCP?
- Типовой ответ: есть, выдаётся выжимка.
- Что делать: запросить выжимку, сверить с SEC_POLICY_AI.md.
- Статус: требует запроса в ИБ.

#### 3. MCP-серверы из allow-list
- Вопрос ИБ: какие MCP-серверы разрешены?
- Типовой ответ: shell (allow-list), git (read-only), filesystem (rw/ro).
- Что делать: использовать только эти три.
- Статус: подтверждено.

#### 4. Права MCP — минимальные
- Вопрос ИБ: какие права?
- Типовой ответ: минимально необходимые.
- Что делать: настроить по матрице доступа.
- Статус: требует настройки.

#### 5. Логирование включено
- Вопрос ИБ: куда пишутся логи?
- Типовой ответ: в F:\TO_DBI\logs.
- Что делать: включить логирование.
- Статус: требует настройки.

#### 6. Изоляция процесса MCP
- Вопрос ИБ: запускается ли MCP под отдельной учёткой?
- Типовой ответ: да, отдельная учётка + ACL.
- Что делать: создать svc_mcp, настроить ACL.
- Статус: требует согласования.

#### 7. DLP-контроль на промпты и ответы
- Вопрос ИБ: есть ли DLP?
- Типовой ответ: внешние AI блокируются, локальные — выборочный аудит.
- Что делать: не передавать чувствительные данные.
- Статус: подтверждено.

#### 8. Инструктаж сотрудника
- Вопрос ИБ: проведён ли инструктаж?
- Типовой ответ: обязателен.
- Что делать: провести, зафиксировать.
- Статус: требует проведения.

#### Сводная таблица

| № | Пункт | Типовой ответ ИБ | Статус |
|---|---|---|---|
| 1 | Версия Ai-Continue | MCP с 0.9.x | требует проверки |
| 2 | Политика ИБ | Выжимка | требует запроса |
| 3 | Allow-list MCP | shell/git/filesystem | подтверждено |
| 4 | Права MCP | Минимальные | требует настройки |
| 5 | Логирование | F:\TO_DBI\logs | требует настройки |
| 6 | Изоляция MCP | Отдельная учётка + ACL | требует согласования |
| 7 | DLP | Внешние AI блокируются | подтверждено |
| 8 | Инструктаж | Обязателен | требует проведения |
```

### Специфика `run_cnt_003_nightly.cmd`
`:check_deps`:
- проверка `ds_cnt_002.exit` = 0 (код 1);
- YAML-синтаксис `config.yaml` (код 2).

`:run_main`:
- `SEC_POLICY_AI.md` существует и содержит раздел 12.4 (код 2);
- раздел 12.4 содержит 8 пунктов + сводную таблицу;
- каждый пункт: вопрос, ответ, действие, статус.

### Результат этапа 003
- Отчёт: `EXCHANGE\OUTBOX\DS_CNT_003_report.md`.
- Код: `logs\ds_cnt_003.exit` = 0.
- Lock: `logs\ds_cnt_003.lock` удалён.

---

## Этап 004. mcpServers + ACL
Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7).
Добавить блок `mcpServers` в `config.yaml`, проверить ACL.

### Шаг 004.1. Проверки (CLI)
```
ai-continue --version
ai-continue mcp list
```
Версия ≥ 0.9.x. Три сервера из внутреннего реестра.

### Шаг 004.2. Добавить блок `mcpServers` в `config.yaml`
В конец файла. Существующие блоки не трогать.

```yaml
mcpServers:
  - name: shell
    command: python
    args: ["-m", "mcp_shell_server"]
    env:
      MCP_SHELL_ALLOW: "python,git status,dir,ls"
      MCP_SHELL_CWD: "F:\\TO_DBI"

  - name: git
    command: python
    args: ["-m", "mcp_git_server"]
    env:
      MCP_GIT_MODE: "readonly"
      MCP_GIT_CWD: "F:\\TO_DBI"

  - name: filesystem
    command: python
    args: ["-m", "mcp_filesystem_server"]
    env:
      MCP_FS_ROOTS_RW: "F:\\TO_DBI\\logs;F:\\TO_DBI\\PATCH_OUT"
      MCP_FS_ROOTS_RO: "F:\\TO_DBI\\DATA;F:\\TO_DBI\\EXCHANGE;F:\\TO_DBI\\PATCH_IN"
      MCP_FS_MODE: "rw+ro"
```

### Специфика `run_cnt_004_nightly.cmd`
`:check_deps`:
- проверка `ds_cnt_003.exit` = 0 (код 1);
- версия Ai-Continue ≥ 0.9.x (код 2);
- YAML-синтаксис `config.yaml` (код 2);
- три MCP-сервера зарегистрированы (код 3);
- учётка `svc_mcp` существует (код 4, если нет — эскалация).

`:run_main`:
- порядок блоков `config.yaml`: models → slashCommands →
  embeddingsProvider → mcpServers (код 2 при нарушении);
- ACL: `svc_mcp` не пишет в DATA, EXCHANGE, PATCH_IN (код 4);
- ACL: `svc_mcp` пишет в logs, PATCH_OUT (код 4);
- ACL: `svc_mcp` читает DATA, EXCHANGE, PATCH_IN (код 4).

Проверка ACL:
```
icacls F:\TO_DBI\DATA
icacls F:\TO_DBI\EXCHANGE
icacls F:\TO_DBI\PATCH_IN
icacls F:\TO_DBI\logs
icacls F:\TO_DBI\PATCH_OUT
```
Ожидаемо для `svc_mcp`: DATA, EXCHANGE, PATCH_IN — `(RX)`;
logs, PATCH_OUT — `(RX,W)`.

### Шаг 004.3. Зафиксировать в `agents-short.md`
Добавить строки:
- MCP shell — только allow-list команд.
- MCP git — только read-only.
- MCP filesystem: rw — logs, PATCH_OUT; ro — DATA, EXCHANGE, PATCH_IN.
- Запись в DATA, EXCHANGE, PATCH_IN — запрещена.
- MCP-серверы запускаются под учёткой `svc_mcp`.
- При отказе MCP — не обходить, эскалировать.

### Результат этапа 004
- Отчёт: `EXCHANGE\OUTBOX\DS_CNT_004_report.md`.
- Код: `logs\ds_cnt_004.exit` = 0.
- Lock: `logs\ds_cnt_004.lock` удалён.

---

## Этап 005. @codebase-индексация
Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7).
Настроить `embeddingsProvider`, `.continueignore`, выполнить индексацию.

### Шаг 005.1. Проверить Ollama и embed-модель
```
ollama list
```
Ожидаемо: `nomic-embed-text`. Иначе — код 3.

### Шаг 005.2. Настроить `embeddingsProvider` в `config.yaml`
```yaml
embeddingsProvider:
  provider: ollama
  model: nomic-embed-text
  apiBase: http://localhost:11434
```
Не трогать `mcpServers` и `slashCommands`.

### Шаг 005.3. Настроить `.continueignore`
```
# Не индексировать
.git/
logs/
PATCH_IN/
PATCH_OUT/
node_modules/
__pycache__/
*.pyc
*.log
*.tmp
EXCHANGE/AI_IN/
EXCHANGE/AI_OUT/
EXCHANGE/OUTBOX/
```
`DATA/` и `EXCHANGE/` (кроме исключённых) — индексировать.
Если `.continueignore` существует — дополнить.

### Шаг 005.4. Индексация
```
ai-continue index --path F:\TO_DBI
```
Лог → `F:\TO_DBI\logs\ds_cnt_005_index.log`.
Код → `F:\TO_DBI\logs\ds_cnt_005.exit`.

### Шаг 005.5. Проверка
```
ai-continue index status --path F:\TO_DBI
dir F:\TO_DBI\.continue\index
```
Ожидаемо: индекс создан, размер > 0.

Контрольные запросы `@codebase`:
```
ai-continue chat --query "@codebase Где описана матрица доступа TO_DBI?"
ai-continue chat --query "@codebase Что такое CNT в TO_DBI?"
ai-continue chat --query "@codebase Чем logs отличается от EXCHANGE\bot.log?"
ai-continue chat --query "@codebase Какие MCP-серверы разрешены?"
```
Ожидаемо:
- матрица доступа → `SEC_POLICY_AI.md`, раздел 3;
- CNT → Ai-Continue;
- logs vs bot.log → разграничены;
- allow-list MCP → shell, git, filesystem.

Примечание: если CLI не поддерживает `index status` или `chat --query` —
использовать альтернативу или отложить до ручной проверки.
Способ зафиксировать в отчёте.

### Шаг 005.6. Зафиксировать в `agents-short.md`
```markdown
## Индексация @codebase
- Индексируется: F:\TO_DBI (кроме .continueignore).
- Embed-модель: nomic-embed-text (Ollama, 11434).
- Исключено: logs/, PATCH_IN/, PATCH_OUT/, .git/,
  EXCHANGE/AI_IN|AI_OUT|OUTBOX, *.log.
- Лог: F:\TO_DBI\logs\ds_cnt_005_index.log.
- При ошибке — не обходить, эскалировать.
```

### Специфика `run_cnt_005_nightly.cmd`
`:check_deps`:
- проверка `ds_cnt_004.exit` = 0 (код 1);
- версия Ai-Continue ≥ 0.9.x (код 2);
- YAML-синтаксис `config.yaml` (код 2).

`:run_main`:
- `config.yaml` содержит `embeddingsProvider` с `nomic-embed-text` (код 2);
- порядок блоков `config.yaml`: models → slashCommands →
  embeddingsProvider → mcpServers (код 2 при нарушении);
- Ollama и `nomic-embed-text` доступны (код 3);
- `ai-continue index --path F:\TO_DBI` выполнен;
- лог → `ds_cnt_005_index.log`;
- код → `ds_cnt_005.exit`.

### Результат этапа 005
- Отчёт: `EXCHANGE\OUTBOX\DS_CNT_005_report.md`.
- Код: `logs\ds_cnt_005.exit` = 0.
- Lock: `logs\ds_cnt_005.lock` удалён.

---

## Ограничения (общие)
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- MCP-серверы — только локальные, под учёткой `svc_mcp`.
- Соблюдать матрицу доступа.
- Не путать `logs` и `EXCHANGE\bot.log`.
- Не расширять allow-list без согласования с ИБ.

## Артефакты (сводно)
- `.continue/rules/agents-short.md` — обновлён (этапы 001, 002, 004, 005).
- `~/.continue/config.yaml` — блоки slashCommands, embeddingsProvider,
  mcpServers.
- `EXCHANGE\SEC_POLICY_AI.md` — создан (002), раздел 12.4 заполнен (003).
- `F:\TO_DBI\.continueignore` — создан/обновлён (005).
- `F:\TO_DBI\.continue\index` — индекс (005).
- `tools\run_cnt_001..005_nightly.cmd` — скрипты.
- `logs\ds_cnt_001..005.*` — логи, коды, ошибки.
- Отчёты `EXCHANGE\OUTBOX\DS_CNT_001..005_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Отдельный отчёт на каждый этап:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха (сводно)
1. Этапы 001–005 выполнены, каждый с кодом 0.
2. Все артефакты созданы.
3. Отчёты `DS_CNT_001..005_report.md` в OUTBOX.
4. Цепочка 000 → 001 → 002 → 003 → 004 → 005 пройдена без обходов.
5. Проверка предыдущего этапа (п. 1.10 регламента) — во всех скриптах,
   кроме 000.
6. Lock-файлы удалены после каждого этапа.