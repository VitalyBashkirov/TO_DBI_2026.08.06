# Задание для Koda: Добавление кнопок интеграции с Koda в gui_app.py

**Режим:** Агент (Agent Mode) — нужно изменять файлы и запускать терминал.

**Цель:** Добавить в `F:\TO_DBI\SRC\gui_app.py` две новые кнопки для интеграции с Koda через файловый обмен.

## Шаги для выполнения:
1. **Прочитай** `F:\TO_DBI\SRC\gui_app.py` (используй `read_file`).
2. **Добавь две новые кнопки** в панель управления (`control_frame`), сразу после кнопки `btn_show_sql`:
   - Кнопка **«Отправить в Koda»** (создать метод `send_to_koda`)
   - Кнопка **«Получить ответ»** (создать метод `receive_from_koda`)
3. **Замени** старый метод `send_to_koda(self, code, prompt, clean_mode)` (если он есть) на новый метод без аргументов, который выполняет:
   - Создание файла задания в `F:\TO_DBI\EXCHANGE\INBOX`
   - Запись проблем из `scan_results` в формате Markdown
   - Логирование и уведомление пользователя
4. **Добавь метод** `receive_from_koda()`, который:
   - Читает последний файл из `F:\TO_DBI\EXCHANGE\OUTBOX`
   - Парсит JSON или Markdown
   - Вставляет результат в «Журнал изменений» (`changelog_text`)
   - Перемещает задание из `INBOX` в `PROCESSED`
5. **Управление доступностью:** Кнопки должны быть доступны после сканирования.
6. **Сохрани изменения** в `F:\TO_DBI\SRC\gui_app.py` (кодировка UTF-8, CRLF).
7. **Сохрани результат** в `F:\TO_DBI\EXCHANGE\OUTBOX` (Markdown).
8. **Запиши лог** в `F:\TO_DBI\EXCHANGE\bot.log` (Windows-1251, `-Encoding Default`).
9. **При успешном выполнении** выведи: `-= DS 004_add_koda_integration.md успешно выполнен =-` + ?? ?? ??
10. **При ошибке** выведи: `-= DS 004_add_koda_integration.md не выполнен =-` + ?? ?? ?? + причина.

## Требования к коду:
- **Кодировка файла `gui_app.py`:** UTF-8.
- **Перевод строк:** Windows CRLF.
- **Метод `send_to_koda`:** должен использовать `Path(__file__).parent.parent / 'EXCHANGE' / 'INBOX'` и `datetime.now()` для уникального имени.
- **Метод `receive_from_koda`:** должен использовать `Path(__file__).parent.parent / 'EXCHANGE' / 'OUTBOX'`.
- **Проверка:** После изменения запусти `python -m py_compile F:\TO_DBI\SRC\gui_app.py` и сообщи результат.