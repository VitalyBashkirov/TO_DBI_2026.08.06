# DS_104 — Отчёт: Гигиена репозитория

**Дата:** 07.10.2026
**Статус:** Выполнено
**Коммит:** `dff1d80` (feature/dockerization)

---

## 1. Правка .gitignore

**Файл:** `F:\TO_DBI\.gitignore` (UTF-8 без BOM, BOM удалён)

### Было (строки 16–20):
```
# Exchange and log
EXCHANGE/bot.log
EXCHANGE/INBOX/
EXCHANGE/OUTBOX/
EXCHANGE/PROCESSED/
```

### Стало (строки 16–21):
```
# Exchange and log (нужные для воспроизводимости — версионируются, DS_104)
# EXCHANGE/bot.log            — версионируется (DS_104)
EXCHANGE/INBOX/
# EXCHANGE/OUTBOX/            — версионируется (DS_104)
# EXCHANGE/PROCESSED/         — версионируется (DS_104)
```

### Добавлено в конец:
```
# Cleanup DS_104: отладочные бэкапы, мусор, исключение для bot.log
*.bak_*
*.broken_*
*.before_*
*.lnk
test_cyr.bat
cleanup_report.csv
!EXCHANGE/bot.log
```

**Важно:** `!EXCHANGE/bot.log` идёт после `*.log` — последнее правило выигрывает.

---

## 2. git rm --cached — удалено из индекса

**Всего удалено: 46 файлов** (на диске остались).

| Категория | Кол-во | Примеры |
|-----------|--------|---------|
| `.bak_*` | 35 | `Ollama и LM Studio.bat.bak_*`, `test_all_models.ps1.bak_*`, `tools/*.bak_*` |
| `.broken_*` | 1 | `test_all_models.ps1.broken_20261006_202441` (85.85 MB) |
| `.before_*` | 1 | `test_all_models.ps1.before_bomfix_20261005_142946` |
| `.lnk` | 4 | `EXCHANGE/OUTBOX — ярлык.lnk`, `Ollama и LM Studio.lnk`, `PATCH_IN — ярлык.lnk`, `Запускать из под админа cleanup.lnk` |
| Отладочные | 2 | `test_cyr.bat`, `cleanup_report.csv` |
| `.bak_2026*` (без `_`) | 3 | `Ollama и LM Studio.bat.bak_20261005_141456` и др. |

---

## 3. git add — добавлено в git

| Каталог/файл | Кол-во |
|--------------|--------|
| `EXCHANGE/PROCESSED/` | 149 файлов |
| `EXCHANGE/OUTBOX/` | 47 файлов |
| `EXCHANGE/bot.log` | 1 (git add -f) |

---

## 4. Коммит

```
[feature/dockerization dff1d80] DS_104: гигиена репо — версионирование PROCESSED/OUTBOX/bot.log, удаление 46 файлов мусора
 244 files changed, 32828 insertions(+), 2114674 deletions(-)
```

---

## 5. Push

```
39292b9..dff1d80  feature/dockerization -> feature/dockerization
```

Успешно.

---

## 6. Проверка

| Метрика | До | После |
|---------|----|-------|
| `size-pack` | 1.25 MiB | 1.25 MiB (не изменился) |
| PROCESSED в git | 0 | 149 |
| OUTBOX в git | 0 | 47 |
| bot.log в git | нет | есть |
| Мусор (`.bak_*`, `.broken_*`, `.lnk`) | 46 | 0 |
| `git status` | clean | clean |
| Ветка | — | `feature/dockerization` синхр. с origin |

---

## 7. Вывод

Репозиторий очищен. PROCESSED/OUTBOX/bot.log версионируются. Мусор удалён из индекса. `.gitignore` защищает от повторного замусоривания. pack не вырос.
