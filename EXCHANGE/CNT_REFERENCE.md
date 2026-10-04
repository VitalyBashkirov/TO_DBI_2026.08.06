# CNT_REFERENCE.md — справочник по Continue (CNT) для TO_DBI

Справочник, не задание. Читать по ссылке из промпта чата CNT.
Версия: 1.4. Дата: 04.10.2026.

Полный образец config.yaml — в отдельном файле:
F:\TO_DBI\EXCHANGE\CNT_config_example.yaml

---

## 1. Slash-команды: что это

Slash-команда — короткое имя, начинающееся с `/`, которое подставляет
заранее заготовленный промпт в чат AI-ассистента. Вместо длинного текста
пишете `/имя` — Continue подставляет шаблон.

Аналогия: макрос / алиас в shell.

Два вида:
- **Built-in** — встроены в Continue (`/edit`, `/explain`, `/test`, `/fix`, `/comment`).
- **Custom** — задаются в config.yaml (наши: `/ds-template`, `/report` и т.д.).

Slash-команда = «что сказать модели». Результат — **текст**, не действие.

---

## 2. Slash vs MCP

| Критерий | Slash-команда | MCP |
|---|---|---|
| Что это | Сохранённый промпт | Протокол подключения к серверам |
| Результат | Текст в чат | Действие (shell/git/файлы) |
| Запуск CLI | ❌ | ✅ |
| Git-commit | ❌ | ✅ |
| Запись файла | ❌ | ✅ |
| Где в config.yaml | slashCommands | mcpServers |
| Риск ИБ | Низкий | Средний/высокий |

Формула: slash — «что сказать», MCP — «что разрешено делать».
Связка: /mcp-write EXCHANGE\OUTBOX\file.md → запись файла через MCP.

---

## 3. Целевые slash-команды для TO_DBI

| Команда | Категория | Назначение |
|---|---|---|
| /ds-template | DS | Черновик DS по DS_STANDARD.md |
| /report | Отчёты | Черновик отчёта в OUTBOX |
| /check-standard | Ревью | Проверка на DS_STANDARD.md (раздел 2) |
| /explain-log | Логи | Разбор последних 200 строк bot.log |
| /gen-test | Тесты | Заготовка unittest по test_ds089b.py |
| /mcp-shell | MCP | Пилот: CLI через MCP shell |
| /mcp-git | MCP | Пилот: git status через MCP git |
| /mcp-write | MCP | Пилот: запись в OUTBOX через MCP filesystem |

Built-in (`/edit`, `/explain`, `/test`, `/fix`, `/comment`) — используются
как есть, без настройки, для общих операций с кодом.

Тексты prompt для custom-команд — в CNT_config_example.yaml (§ slashCommands).

---

## 4. MCP — трек внедрения

MCP даёт CNT доступ к shell/git/filesystem (сближает с KODA, но не делает
полноценным исполнителем DS).

Шаги:
1. Проверить версию Continue (поддержка MCP) и политику ИБ банка.
2. Выбрать локальные MCP-серверы: shell (python/ollama), git, filesystem
   (OUTBOX/AI_IN/AI_OUT).
3. Настроить config.yaml → блок mcpServers.
4. Пилот:
   - python tools\ai_local_worker.py --check через MCP shell;
   - git status через MCP git;
   - запись тестового файла в EXCHANGE\OUTBOX через MCP filesystem.
5. Зафиксировать риски в agents-short.md (что CNT НЕ делает без указания).

Только локальные MCP-серверы. Внешние — запрещены (закрытый контур банка).

Образец блока mcpServers — в CNT_config_example.yaml.

---

## 5. config.yaml — где смотреть

Полный образец config.yaml вынесен в отдельный файл:
F:\TO_DBI\EXCHANGE\CNT_config_example.yaml

Там: models, rules, context, slashCommands (8 шт.), mcpServers (3 шт.).

Замечания:
- npx-серверы — пример. В закрытом контуре npx может быть недоступен;
  нужны локальные аналоги или свои серверы (разведка в чате CNT).
- ALLOWED_COMMANDS / REPO_PATH — иллюстрация.
- Образец. KODA уточнит синтаксис под вашу версию Continue.

---

## 6. Индексатор (свой)

### Что это
Свой пакетный семантический поиск по F:\TO_DBI. Не зависит от Continue.
Использует Ollama (nomic-embed-text) для эмбеддингов, SQLite + numpy
для хранения. Назначение — ночной поиск по документам, регламентам,
стандартам.

### Запуск
```
cd F:\TO_DBI
python -m tools.indexer.cli index
```

Опции:
- `--path F:\TO_DBI` — корень (по умолчанию).
- `--full` — полная переиндексация (стирает индекс). Осознанно.

### Поиск
```
python -m tools.indexer.cli query "матрица доступа"
python -m tools.indexer.cli query "svc_mcp" --top 5
```

### Статистика
```
python -m tools.indexer.cli stats
```

### Где индекс
- `F:\TO_DBI\logs\indexer\chunks.db` — тексты чанков (SQLite).
- `F:\TO_DBI\logs\indexer\embeddings.npy` — вектора (numpy).

### Параметры
- Модель: `nomic-embed-text` (Ollama, порт 11434, dim=768).
- Чанк: 256 слов, overlap 64.
- Rate limit: 1 req/sec (Ollama нестабильна при >50 req/min).
- Фильтр: JSON/SQL > 50 KB — пропускаются.
- SCHEMA_VERSION = 2.

### Что индексируется (26 файлов)
- Корень `F:\TO_DBI\*.md` (9 файлов, кроме ALGORITHM_FLOWCHART.md).
- `EXCHANGE\*.md` (5 файлов, кроме CNT_config_example.yaml,
  DS_031_NIGHTLY*, DS_054_AI-fallback_черновик.md).
- `DATA\Рубрикатор v5\*.md`, `*.txt` (5 файлов).
- `DATA\OUTERS\*.md` (1 файл).
- `DATA\*.txt` (1 файл).
- `.continue\rules\agents-short.md` (1 файл).
- `PROJECT_STATUS\*.md` (1 файл).
- `PROMPTS\*.md` (1 файл).

### Что НЕ индексируется
`SRC\`, `tools\`, `PATCH_IN\`, `PATCH_OUT\`, `logs\`, `logs_Deep\`,
`.git\`, `.github\`, `.kilo\`, `.kilocode\`, `.vscode\`, `.pytest_cache\`,
`reports\`, `temp\`, `temp_fix\`, `RubricatorTemp\`, `Презентация\`,
`Вопросы-ответы\`, `done\`, `EXCHANGE\*` (подкаталоги),
`INBOX\`, `OUTBOX\`, `PROCESSED\`, `AI_IN\`, `AI_OUT\`,
`DATA\CFT Platform IDE Documentation\`, `DATA\Patch_USERNAME\`,
`DATA\Тестовые файлы\`, `DATA\*.md` (корень — DS_037, DS_039),
JSON/SQL > 50 KB.
Шум (DS_CNT_015): `DS_031_NIGHTLY.md`, `DS_031_NIGHTLY_report.md`,
`DS_054_AI-fallback_черновик.md`.

### Запуск в ночном режиме
```
F:\TO_DBI	ools\run_cnt_005c_index.cmd
```
Регистрация в Task Scheduler — 01:00–05:00 (по согласованию
с Администратором АРМа).

### Ограничения
- Только локальная Ollama.
- Внешние AI — запрещены.
- Скрипт не пишет вне `logs\` и `PATCH_OUT\`.
- При ошибке — не обходить, эскалировать.

### Регламент
Подробности — `EXCHANGE\DS_CNT_000_regulation.md` (п. 1.13, 1.14, 1.15).

---

## 7. Ночной pipeline CNT

### Что это
Связка инструментов CNT для пакетного ночного прогона без оператора:
индекс + /check-standard + /explain-log + отчёт.

### Состав
1. `tools\run_cnt_005c_index.cmd` — инкрементальная переиндексация.
2. `tools\check_standard.ps1` → `tools\check_standard.py` — проверка
   файла на соответствие `DS_STANDARD.md` (раздел 2) через Ollama.
3. `tools\explain_log.ps1` → `tools\explain_log.py` — разбор хвоста
   `EXCHANGE\bot.log` через Ollama.
4. `tools\make_pilot_report.ps1` — сборка сводного отчёта в OUTBOX.
5. `tools\run_cnt_007_nightly.cmd` — оркестратор (все шаги по цепочке).

### Модель
`qwen2.5-coder:3b` (Ollama, порт 11434). Обоснование: компромисс
между качеством и скоростью на CPU. 1.5b давала шаблонные ответы и
зацикливания; 7b слишком медленна для ночного окна.

### Параметры
- `num_ctx = 4096`, `num_predict = 600`, `temperature = 0.1`.
- Tail лога: 200 строк.
- Rate limit: 1 req/sec.

### Запуск вручную
```
F:\TO_DBI	ools\run_cnt_007_nightly.cmd
```

### Логи и артефакты
- `logs\ds_cnt_007.log` — лог шагов.
- `logs\ds_cnt_007.exit` — код выхода (0 = успех).
- `logs\ds_cnt_007_check_standard.md` — результат /check-standard.
- `logs\ds_cnt_007_explain_log.md` — результат /explain-log.
- `EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md` — сводный отчёт.

### Task Scheduler
- Имя задачи: `TO_DBI_CNT_NightlyPipeline`.
- Триггер: ежедневно, 01:00.
- Условие: питание от сети.
- Регистрация — только после успешного ручного прогона и по
  согласованию с Администратором АРМ.

### Регламент
`EXCHANGE\DS_CNT_000_regulation.md` п. 1.16.

---

## 8. Индексация @codebase в Continue

### Что это
Встроенный семантический поиск Continue по воркспейсу. Отдельный
индекс. Не связан со своим индексатором (§6).

### Запуск
- VS Code → Continue → Settings → Index → «Index workspace».
- Или в чате: `@codebase <запрос>` → «Index your workspace».

### Ограничения (текущая версия)
- **Индекс не построен** (в текущей версии Continue).
- `@codebase` работает «по памяти» модели.
- **Галлюцинации** — ссылается на несуществующие файлы.
- Раздел Index в Settings отсутствует.

### Рекомендация
- Для точных данных — читать файлы напрямую.
- Для пакетного поиска — свой индексатор (§6).
- `@codebase` — только как вспомогательный, с проверкой результата.
- При ссылке на файл — проверить его существование:
  ```
  Get-ChildItem F:\TO_DBI -Recurse -Filter "<имя>"
  ```

### Зафиксировано
- `DS_CNT_005b_report.md` — раздел «Состояние @codebase».
- `.continue\rules\agents-short.md` — блок «@codebase — ограничения».
- `DS_CNT_010_report.md` — фиксация галлюцинаций.

---

## 9. Ссылки

- F:\TO_DBI\AGENTS.md — инструкция KODA (полная).
- F:\TO_DBI\AGENTS_SHORT.md — эталон выжимки для Continue.
- F:\TO_DBI\.continue\rules\agents-short.md — рабочее правило.
- F:\TO_DBI\EXCHANGE\DS_STANDARD.md — стандарт DS.
- F:\TO_DBI\EXCHANGE\DS_CONTEXT.md — контекст (§9.5 — AI-контур).
- F:\TO_DBI\EXCHANGE\DS_FILES.md — карта файлов.
- F:\TO_DBI\EXCHANGE\CNT_config_example.yaml — образец config.yaml.

### Индексатор
- `EXCHANGE\DS_CNT_000_regulation.md` — регламент (п. 1.13, 1.14, 1.15).
- `EXCHANGE\DS_CNT_005c_report.md` — отчёт о создании.
- `EXCHANGE\DS_CNT_005c_run_report.md` — отчёт о прогоне.
- `EXCHANGE\DS_CNT_012_optimal_index_list_report.md` — список для индексации.
- `EXCHANGE\DS_CNT_013_optimal_index_clarifications_report.md` — уточнения.
- `EXCHANGE\DS_CNT_014_report.md` — применение рекомендаций.
- `EXCHANGE\DS_CNT_015_report.md` — устранение шума, исследование матрицы.

### Планировщик (Task Scheduler)
- `EXCHANGE\DS_CNT_000_regulation.md` — регламент (п. 8 — Планировщик).
- `EXCHANGE\DS_CNT_019_report.md` — отчёт о регистрации задачи.
- Задача: `TO_DBI_CNT_NightlyPipeline` (Ready, daily 01:00).

---

**Конец CNT_REFERENCE.md.**