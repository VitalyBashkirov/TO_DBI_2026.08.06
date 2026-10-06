# DS_096b — Удаление мусорных файлов

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация (cleanup)
**Приоритет:** низкий
**Зависит от:** —
**Блокирует:** DS_096 (git)

**См.:** `DS_STANDARD.md`.

## 1. Цель

Удалить мусорные файлы из корня проекта, оставшиеся от предыдущих прогонов тестов.

## 2. Файлы к удалению

| # | Файл | Причина |
|---|------|---------|
| 1 | `F:\TO_DBI\pytest_out.txt` | Пустой (только заголовок pytest) |
| 2 | `F:\TO_DBI\pytest_summary.txt` | Пустой (только заголовок pytest) |

**Оба файла — от прогона `pytest ... > pytest_out.txt` (или аналогичного), не входят ни в один DS.**

## 3. Действия

```powershell
Remove-Item F:\TO_DBI\pytest_out.txt -Force -ErrorAction SilentlyContinue
Remove-Item F:\TO_DBI\pytest_summary.txt -Force -ErrorAction SilentlyContinue
```

## 4. Проверка

```powershell
Test-Path F:\TO_DBI\pytest_out.txt       # → False
Test-Path F:\TO_DBI\pytest_summary.txt   # → False
```

## 5. Ограничения

Стандартные. Удалять **только** два указанных файла. Больше ничего не трогать.

## 6. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + раздел:

```
## Проверка
- pytest_out.txt: удалён
- pytest_summary.txt: удалён
- git status: чисто (по этим файлам)
```

## 7. Артефакты

- `EXCHANGE\OUTBOX\DS_096b_report.md`