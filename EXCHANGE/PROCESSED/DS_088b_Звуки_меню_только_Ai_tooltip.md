# DS_088b — Звуки + контекстное меню + «Только Ai» + tooltip

Дата: 30.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация | Приоритет: средний
Зависит от: DS_088a_fix | Блокирует: DS_089
См.: DS_STANDARD.md (§2, §3, §5)

---

## 1. Цель

Четыре доработки к DS_088a_fix:

A. **Звуки** — для трёх кнопок (1, 2, 3): победные / печальные;
   `winsound.Beep` + fallback `MessageBeep`; порог `sound_min_duration`.

B. **Контекстное меню** — для всех `Entry` и всех `Text` в форме
   (включая ЖВ): Выделить всё / Копировать / Вставить / Очистить.

C. **Переименование** «Только AI» → «Только Ai» — все вхождения.

D. **Tooltip** — один на метку «Пороги confidence:» (заменить текущий
   на поле `conf_high`).

**НЕ МЕНЯТЬ:** логику цикла (DS_088a), `send_to_ai`, воркеры,
логику `ai_exchange.py`, пороги confidence (значения).

---

## 2. Что делать

### 2.1. Разведка (ОБЯЗАТЕЛЬНО)

| Что | Где искать |
|-----|------------|
| Обработчики кнопок 1, 2, 3 | `SRC\gui_app.py` (`btn_scan`, `btn_fix`, `btn_to_ai`) |
| Метод `_run_ai_cycle` | `SRC\gui_app.py` (DS_088a) |
| Все `Entry` в форме | `SRC\gui_app.py` — grep `Entry(` |
| Все `Text` в форме | `SRC\gui_app.py` — grep `Text(` |
| `log_text` (ЖВ) | `SRC\gui_app.py` |
| `ai_only_var` («Только AI») | `SRC\gui_app.py` (972) |
| Все вхождения «Только AI» | grep по `gui_app.py` + другие SRC-файлы |
| Tooltip `conf_high` | `SRC\gui_app.py` (DS_088a_fix) |
| `SRC\settings.json` | существующие ключи (`conf_low`, `conf_high`) |

**РАЗВИЛКА-СТОП:**
- Если `winsound` **недоступен** (не Windows) — СТОП (звуки — Windows-only).
- Если в форме **> 20 виджетов** `Entry`/`Text` — уточнить (возможно, нужен
  универсальный binding через `bind_class`).

### 2.2. Звуки (часть A)

**Функция `_play_result_sound(success, duration)`:**

```python
def _play_result_sound(self, success: bool, duration: float):
    """Играет звук по завершении операции.
    duration — время операции в секундах.
    Если duration < sound_min_duration (из settings.json, по умолчанию 30) —
    звук не играет."""
    min_dur = self.settings.get('sound_min_duration', 30)
    if duration < min_dur:
        return
    try:
        import winsound
        if success:
            # победные: 1000 → 1200 → 1500
            winsound.Beep(1000, 300)
            winsound.Beep(1200, 300)
            winsound.Beep(1500, 500)
        else:
            # печальные: 1500 → 1200 → 1000
            winsound.Beep(1500, 300)
            winsound.Beep(1200, 300)
            winsound.Beep(1000, 500)
    except (ImportError, RuntimeError):
        # fallback на встроенные
        try:
            import winsound
            if success:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception:
            pass  # тихо игнорируем
Вызовы:

Обработчик кнопки «1. Сканировать» — по завершении.

Обработчик кнопки «2. Исправить код» — по завершении.

Обработчик кнопки «3. В Ai» — по завершении (_run_ai_cycle).

Замер duration: время от старта операции до завершения (time.time()
до/после).

Конфиг: в SRC\settings.json добавить (если нет):

json
"sound_min_duration": 30
2.3. Контекстное меню (часть B)
Для всех Entry и всех Text в форме.

Метод _attach_context_menu(widget, is_text=False):

python
def _attach_context_menu(self, widget, is_text=False):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Выделить всё",
                     command=lambda: widget.event_generate('<<SelectAll>>'))
    menu.add_command(label="Копировать",
                     command=lambda: widget.event_generate('<<Copy>>'))
    menu.add_command(label="Вставить",
                     command=lambda: widget.event_generate('<<Paste>>'))
    if is_text:
        menu.add_separator()
        menu.add_command(label="Очистить",
                         command=lambda: widget.delete('1.0', 'end'))
    widget.bind('<Button-3>',
                lambda e: menu.tk_popup(e.x_root, e.y_root))
Применить ко всем Entry и Text — после создания виджетов
(например, обход winfo_children() рекурсивно).

Исключения (не трогать):

Treeview (таблица рубикатора) — отменено ранее.

Combobox (Уровень логирования) — отменено ранее.

Checkbutton, Label — отменено ранее.

2.4. Переименование «Только AI» → «Только Ai» (часть C)
Найти все вхождения в SRC\ (grep):

переменная ai_only_var (972);

текст чекбокса на форме;

tooltip чекбокса (если есть);

упоминания в ЖВ, логах, комментариях.

Заменить текст «Только AI» → «Только Ai» (AI → Ai).

Переменную ai_only_var не переименовывать (только текст на форме).

2.5. Tooltip (часть D)
Заменить текущий tooltip на поле conf_high (из DS_088a_fix) —
на один tooltip на метку «Пороги confidence:».

Текст tooltip:

«Пороги confidence для AI-фиксов:
— ниже нижнего порога: needs_manual (ручная проверка);
— между порогами: средняя уверенность;
— выше верхнего порога: авто-применение.
Диапазон ввода: 0.0–1.0. Рекомендуемые значения: 0.5–0.8.»

Привязка: tooltip на метку «Пороги confidence:», не на поля 0.5 / 0.8.

3. Тесты
#	Тест	Ожидание
1	Звук победный (> 30 сек)	Beep 1000→1200→1500
2	Звук печальный (> 30 сек)	Beep 1500→1200→1000
3	Звук < 30 сек	не играет
4	Fallback Beep → MessageBeep	при RuntimeError
5	sound_min_duration в config	ключ существует
6	Звук из 1, 2, 3	вызовы в обработчиках
7	Контекстное меню Entry	правый клик → меню
8	Контекстное меню log_text (ЖВ)	правый клик → меню
9	Контекстное меню других Text	правый клик → меню
10	Копировать/Вставить работает	через меню
11	Treeview/Combobox — без меню	правый клик — без меню
12	«Только Ai» — текст	на форме
13	«Только AI» — нет вхождений	grep пусто
14	Tooltip на метке confidence	при наведении — текст из §2.5
15	Tooltip поля conf_high — убран	нет
16	Регресс DS_086/087/088a/088a_fix	PASSED
4. Ограничения
Правка: SRC\gui_app.py, SRC\settings.json.

НЕ МЕНЯТЬ: SRC\ai_exchange.py, tools\, SRC\analyzer\, SRC\fixer\,
SRC\rule_engine.py.

Логи: EXCHANGE\bot.log + ЖВ. temp\ — можно.

GIT — НЕ КОММИТИТЬ.

5. Отчёт (OUTBOX\DS_088b_report.md)
5.1. Разведка — где виджеты, где «Только AI», конфиг.
5.2. Звуки — функция, вызовы, порог.
5.3. Контекстное меню — сколько виджетов получили, какие.
5.4. «Только Ai» — все вхождения заменены.
5.5. Tooltip — на метке, текст.
5.6. Тесты 1–16 — PASSED/FAILED.
5.7. Расхождения / стоп.

6. Артефакты
SRC\gui_app.py (правка)

SRC\settings.json (правка — sound_min_duration)

EXCHANGE\OUTBOX\DS_088b_report.md

(опционально) SRC\tests\test_ds088b.py