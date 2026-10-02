# AGENTS_SHORT.md — Контекст проекта для Continue

> Краткая выжимка `AGENTS.md` для Continue (Ollama, локальные модели).
> Для KODA (koda-base) — полный `F:\TO_DBI\AGENTS.md`.

## Проект

**АРМ «Адаптация под DBI»** — миграция PL/Plus кода с Oracle на PostgreSQL (DBI).

| Параметр | Значение |
|----------|----------|
| Версия рубрикатора | 5.3.0 |
| Источник правил | `F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` |
| Активные рубрикаторы | v53, тдс20240828, тклоик20240828, PlpCheck |
| Устаревшие | v50, v5.0.0 |

## Структура

### Модули (SRC)

| Файл | Назначение |
|------|-----------|
| `SRC\gui_app.py` | GUI (Tkinter), `DBIMigrationApp` |
| `SRC\analyzer\scanner.py` | Сканер PLPlus, `PLPlusScanner` |
| `SRC\fixer\code_fixer.py` | Детерминированный фиксер, `PLPlusFixer` |
| `SRC\ai_exchange.py` | Файловый обмен AI (AI_IN/AI_OUT) |
| `SRC\rule_engine.py` | Маппинг кодов, bucketing правил |
| `SRC\rubricator_prompts.py` | Загрузка `4.RUBRICATOR_PROMPT v5.json` |

### Инструменты (tools)

| Файл | Назначение |
|------|-----------|
| `tools\rule_based_fixer.py` | Rule-based фиксер тривиальных issues |
| `tools\ai_local_worker.py` | Local AI worker (Ollama) |
| `tools\ai_local_worker_config.json` | Конфиг (model, batch_size, num_ctx) |

### Рабочие каталоги (EXCHANGE)

| Каталог | Назначение |
|---------|-----------|
| `EXCHANGE\INBOX\` | Задачи KODA (DS_XXX) |
| `EXCHANGE\OUTBOX\` | Отчёты DS |
| `EXCHANGE\PROCESSED\` | Выполненные DS |
| `EXCHANGE\AI_IN\` | AI-запросы (AI_REQUEST_*.md) |
| `EXCHANGE\AI_OUT\` | AI-ответы (AI_RESPONSE_*.md) |
| `EXCHANGE\AI_IN_PROCESSED\`, `AI_OUT_PROCESSED\` | Архивы AI |

### Данные

| Каталог | Назначение |
|---------|-----------|
| `DATA\Рубрикатор v5\` | Правила рубрикатора |

## Методология

- **Формат:** `Было: <код>` → `Стало: <код>`.
- **Поиск:** regex из рубрикатора.
- **Правки:** минимальные, не ломать логику.
- **Тесты:** запуск имеющихся после правок.

## Термины

| Термин | Значение |
|--------|----------|
| Issue | Проблема в PLPlus-коде |
| PLAN | План исправления (`[auto]` / `[ignore]`) |
| `needs_ai_fix` | Issues, требующие AI (остаток после фиксера) |
| AI-fallback | Обмен `AI_IN` ↔ `AI_OUT` |
| МКР | Максимальная колонка правила (форматирование) |

## AI-контур

1. Сканер → issues.
2. Детерминированный фиксер → `PLUSFixer` (195 fix).
3. Фильтр «Только AI» → 96 issues.
4. Rule-based fixer (`tools\rule_based_fixer.py`) → 35 fix.
5. Local AI worker (`tools\ai_local_worker.py`) → 61 fix через Ollama.
6. `receive_from_ai` → применение + rescan.
7. `needs_manual` → артефакт для ручного разбора.

## Роли KODA vs Continue

| Действие | KODA | Continue |
|----------|------|----------|
| DS-задания (INBOX → PROCESSED) | ✅ | ❌ |
| `bot.log` | ✅ | ❌ |
| GIT / PUSH | ✅ | ❌ |
| AI-обмен `AI_IN`/`AI_OUT` | ✅ | ❌ |
| Chat / Edit / Autocomplete | ❌ | ✅ |
| Локальные модели Ollama | ❌ | ✅ |

## Модели Continue (Ollama)

- **Chat / Edit / Apply:** `qwen2.5-coder:7b` (contextLength: 8192)
- **Autocomplete:** `qwen2.5-coder:1.5b-base` (contextLength: 2048)
- **Embed:** `nomic-embed-text:latest`

Промпт ограничен `contextLength: 8192`. Компактный контекст — критичен.

## Правила работы

- Файлы `EXCHANGE\` — рабочие данные, не исходники.
- `AGENTS.md` — для KODA, `AGENTS_SHORT.md` — для Continue.
- Конкретный код — прикреплять через `@file`.
- Архитектура — `@AGENTS.md` (полный) или `@DS_CONTEXT.md`.
- Поиск — `@codebase` (требует индексации).

## Ограничения

- `SRC\analyzer\scanner.py`, `SRC\fixer\code_fixer.py`, `SRC\rule_engine.py` — не менять без указания.
- `DATA\` — не менять.
- `bot.log` — только `F:\TO_DBI\EXCHANGE\bot.log`.

## Метрики проекта (актуальные)

| Метрика | Значение |
|---------|----------|
| Скан (PSH_DEP_PRIV_GO) | 5067 issues |
| Детерминированный фиксер | 195 fix |
| Фильтр «Только AI» | 96 issues |
| Rule-based | 35 fix |
| Local AI | 61 fix (~28 мин) |
| Автопокрытие | 95/96 = 99% |
| Время на файл | ~28 мин (batch 10 + fallback) |