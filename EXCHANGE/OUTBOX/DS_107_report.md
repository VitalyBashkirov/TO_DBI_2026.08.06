# DS_107 — Отчёт: Расширение предупреждения о лимите логов

**Дата:** 07.10.2026
**Статус:** Выполнено

---

## 1. Разведка

**Функция:** `SRC\gui_app.py`, `_check_log_size` (строка 1342).

**Каталоги логов (строки 1344–1347):**
```python
log_dirs = [
    Path(__file__).parent.parent / 'logs',   # F:\TO_DBI\logs
    self.logs_deep_dir                        # F:\TO_DBI\logs_Deep
]
```

**Метод `_settings_path` (строка 1524):**
```python
def _settings_path(self) -> Path:
    return Path(__file__).parent / 'settings.json'
```
Возвращает `F:\TO_DBI\SRC\settings.json`.

**Лимит:** `MAX_LOG_SIZE_MB` (строка 49, default 2). Переопределяется из `settings.json` (поле `max_log_size_mb`).

**Сканируются:** `*.log` и `*.md` в обоих каталогах.

---

## 2. Правка: было/стало

**Было (строки 1368–1373):**
```python
result = messagebox.askyesno(
    "Лимит логов превышен",
    f"Размер файлов логов: {size_mb:.2f} МБ\n"
    f"Максимальный размер: {MAX_LOG_SIZE_MB} МБ\n\n"
    f"Удалить все файлы логов?"
)
```

**Стало (строки 1368–1381):**
```python
# Каталоги логов (только существующие)
log_dirs_str = '\n'.join(
    f'  - {d}' for d in log_dirs if d.exists()
)
# Путь к файлу настроек (единый источник — метод класса)
settings_path = self._settings_path()
result = messagebox.askyesno(
    "Лимит логов превышен",
    f"Размер файлов логов: {size_mb:.2f} МБ\n"
    f"Максимальный размер: {MAX_LOG_SIZE_MB} МБ\n\n"
    f"Настройка: {settings_path} (max_log_size_mb)\n"
    f"Каталоги для очистки:\n{log_dirs_str}\n\n"
    f"Удалить все файлы логов (.log, .md) из этих каталогов?"
)
```

Добавлено:
- Путь к `settings.json` (через `self._settings_path()`, не хардкод).
- Список существующих каталогов логов.
- Указание расширений `.log`, `.md` в вопросе.

---

## 3. Тесты

| Файл | Что делает с `_check_log_size` | Влияние правки |
|------|-------------------------------|----------------|
| `test_ds086_ui_hide.py` | Комментарий (строка 30) | Нет |
| `test_ds087_workflow.py` | `lambda self: None` (мок) | Нет |
| `test_ds088a_*.py` | Мок | Нет |
| `test_ds088b.py` | Мок | Нет |

Ни один тест не проверяет текст диалога. Правка не ломает существующие тесты.

---

## 4. Регресс

```
python -m pytest SRC/tests/ -v
60 PASSED
```

Без изменений.

---

## 5. Артефакты

| Файл | Действие |
|------|----------|
| `SRC\gui_app.py` | Расширен диалог `_check_log_size` (строки 1368–1381) |
| `EXCHANGE\OUTBOX\DS_107_report.md` | Отчёт |

---

## 6. Вывод

Диалог «Лимит логов превышен» расширен: пользователь видит путь к `settings.json` (поле `max_log_size_mb`), список каталогов для очистки и удаляемые расширения. Путь получается через `self._settings_path()` — без хардкода.

---

## 7. Расхождения

Нет.
