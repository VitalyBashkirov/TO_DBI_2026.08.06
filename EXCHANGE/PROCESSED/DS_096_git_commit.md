# DS_096 — Git-фиксация: DS_091b + DS_092 + DS_093 + DS_094 + DS_095 + DS_096a/b

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** feature (git)
**Приоритет:** высокий
**Зависит от:** DS_096a, DS_096b
**Блокирует:** —

**См.:** `DS_STANDARD.md`, `AGENTS.md` (команды `GIT`, `GP`, `PUSH`).

## 1. Цель

Зафиксировать в git накопленные изменения: 5 DS (091b, 092, 093, 094, 095) + фиксы (096a, 096b) + ранее незакоммиченный DS_089b (если есть).

## 2. Команда

**Команда:** `GP` (полный цикл: `GIT` + `PUSH`).

**Альтернатива:** `GIT` (только коммит, без push) — по решению Vitaly.

## 3. Что войдёт в коммит

### Изменённые файлы (M) — 11

| # | Файл | Источник |
|---|------|----------|
| 1 | `AGENTS.md` | Правка Vitaly (команда GP) |
| 2 | `EXCHANGE/DS_STANDARD.md` | DS_095 (раздел 6.1) |
| 3 | `SRC/tests/test_ds056_is_in_comment.py` | DS_091b |
| 4 | `SRC/tests/test_ds077.py` | DS_091b |
| 5 | `SRC/tests/test_ds086_ui_hide.py` | DS_091b |
| 6 | `SRC/tests/test_ds087_workflow.py` | DS_091b |
| 7 | `SRC/tests/test_ds088a_ai_cycle.py` | DS_091b |
| 8 | `SRC/tests/test_ds088a_fix.py` | DS_091b |
| 9 | `SRC/tests/test_ds088b.py` | DS_091b |
| 10 | `tools/ai_local_worker.py` | DS_093 + DS_094 |
| 11 | `tools/ai_local_worker_config.json` | DS_096a (BOM убран) |

### Новые файлы (??) — 4

| # | Файл | Источник |
|---|------|----------|
| 1 | `SRC/tests/test_ds092_e2e.py` | DS_092 |
| 2 | `SRC/tests/test_ds093_validate.py` | DS_093 |
| 3 | `SRC/tests/test_ds094_resume.py` | DS_094 + DS_096a |
| 4 | `pytest.ini` | DS_091a |

## 4. Действия

1. `cd F:\TO_DBI`
2. `git status --short` — **убедиться**, что **11 M + 4 ??**, мусора нет.
3. **Команда `GP`:** полный цикл (`git add -A` + `git commit` + `git pull --rebase` + `git push`).
4. Запись в `EXCHANGE\bot.log` (метка `GIT_YYYYMMDD_HHMM`).

## 5. Проверка

| # | Команда | Ожидание |
|---|---------|----------|
| 1 | `git log --oneline -3` | Новый коммит `GIT_YYYYMMDD_HHMM Выполнено` |
| 2 | `git status --short` | Пусто |
| 3 | `git log --oneline -10` | Коммит виден |
| 4 | `python -m pytest -v` | 57 PASSED |

## 6. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2, `AGENTS.md` → команды `GIT`/`GP`). **Не** `git push --force`. **Не** откатывать историю. При rebase-конфликте — остановиться, доложить Vitaly.

## 7. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + раздел:

```
## Коммит
- Хеш: <hash>
- Сообщение: GIT_YYYYMMDD_HHMM Выполнено
- Файлов: 15

## Push
- Статус: OK / Everything up-to-date
- Ветка: feature/dockerization

## git log --oneline -3
<вывод>
```

## 8. Критерии успеха

- Все изменения — в коммите.
- `pytest.ini` — в коммите.
- `git status --short` — чисто.
- Push в `origin/feature/dockerization` — OK.
- `python -m pytest -v` — 57 PASSED.

## 9. Артефакты

- Коммит в git
- Запись в `EXCHANGE\bot.log`
- `EXCHANGE\OUTBOX\DS_096_report.md`