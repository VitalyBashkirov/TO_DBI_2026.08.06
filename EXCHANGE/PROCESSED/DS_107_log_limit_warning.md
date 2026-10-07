# DS_107 — Расширение предупреждения о лимите логов

## Цель
Дополнить диалог «Лимит логов превышен» (gui_app.py,
_check_log_size) информацией:
1. Путь к файлу конфигурации, где задан лимит
   (SRC\settings.json, поле max_log_size_mb).
2. Путь к каталогу (каталогам), откуда будут удалены логи.

Это делает диалог информативнее: пользователь видит, что и откуда
будет удалено.

## Контекст (разведка 07.10.2026, F:\TO_DBI)
- Функция: SRC\gui_app.py, def _check_log_size (строка 1342).
- Каталоги логов (строки 1344–1347):
    log_dirs = [
        Path(__file__).parent.parent / 'logs',        # F:\TO_DBI\logs
        self.logs_deep_dir                            # F:\TO_DBI\logs_Deep
    ]
- Оба каталога существуют (Test-Path True).
- Сканируются: *.log и *.md в этих каталогах.
- Лимит: MAX_LOG_SIZE_MB (строка 49, default 2).
  Переопределяется из settings.json (строка 2890):
    max_log_size = settings.get('max_log_size_mb', 2)
- Файл конфигурации: SRC\settings.json, поле max_log_size_mb
  (строка 11: "max_log_size_mb": 2).
- Текущий диалог (строки 1368–1373):
    result = messagebox.askyesno(
        "Лимит логов превышен",
        f"Размер файлов логов: {size_mb:.2f} МБ\n"
        f"Максимальный размер: {MAX_LOG_SIZE_MB} МБ\n\n"
        f"Удалить все файлы логов?"
    )
- Удаление (строки 1375–1386): файлы с .log и .md в log_dirs.
- Метод self._settings_path() (строка 1524) возвращает путь
  к settings.json — использовать его для получения пути.

## Что делает KODA

### Фаза 1 — Разведка (подтверждение)

1. Открыть SRC\gui_app.py, найти _check_log_size (1342).
2. Прочитать строки 1342–1391.
3. Подтвердить: self._settings_path() (строка 1524) возвращает
   Path(__file__).parent / 'settings.json'.
4. Зафиксировать в отчёте: точный путь к settings.json.

### Фаза 2 — Правка диалога

Файл: SRC\gui_app.py, функция _check_log_size (1342).

Найти блок messagebox.askyesno (строки 1368–1373).
Заменить на расширенный вариант:

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

ВАЖНО:
- log_dirs_str — только существующие каталоги.
- settings_path = self._settings_path() (не хардкод!).
- Расширения (.log, .md) — упомянуть в вопросе.
- Кириллица, UTF-8 без BOM.

### Фаза 3 — Обновление тестов (если нужно)

Проверить SRC\tests\ на тесты, связанные с _check_log_size:
- test_ds086_ui_hide.py (строка 30) — упоминает.
- test_ds087_workflow.py (строка 31) — мок _check_log_size.
- test_ds088a_*.py — мок _check_log_size.
- test_ds088b.py — мок _check_log_size.

Эти тесты МОКАЮТ _check_log_size — не проверяют текст.
Изменение текста их не сломает.

Если найдётся тест, проверяющий текст диалога — обновить.

### Фаза 4 — Регресс

    python -m pytest SRC\tests\ -v

Ожидание: 60 PASSED (без изменений).
Если сломается — разобраться, доложить.

### Фаза 5 — Отчёт

Формат: EXCHANGE\OUTBOX\DS_107_report.md
- UTF-8 без BOM.
- РУССКИЙ. Транслит не использовать (DS_STANDARD.md §3.1).

Содержание:
1. Разведка: log_dirs, settings_path (self._settings_path()),
   лимит (цитаты).
2. Правка: было/стало (цитата).
3. Тесты: количество, статус.
4. Регресс: N PASSED.
5. Артефакты: SRC\gui_app.py.
6. Вывод: диалог расширен, пути отображаются.
7. Расхождения (если есть).

## Что НЕ делает KODA
- Не трогает exchange_bot.py.
- Не трогает EXCHANGE\bot.log.
- Не трогает settings.json (только чтение).
- Не выполняет git/push/GP.

## Ограничения
- SRC — правка допустима только в gui_app.py.
- BOM — избегать (DS_STANDARD.md §6.1).
- Прогноз KODA не нужен.
- Логи — EXCHANGE/bot.log.

## Артефакты
- SRC\gui_app.py (правка диалога).
- EXCHANGE\OUTBOX\DS_107_report.md.

## Ожидание (сводно)
- Диалог содержит путь к settings.json (из self._settings_path()).
- Диалог содержит список каталогов (logs, logs_Deep).
- Диалог уточняет, что удаляются .log и .md.
- pytest: 60 PASSED.