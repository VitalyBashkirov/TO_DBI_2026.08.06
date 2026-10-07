# DS_114 — .gitattributes (json/ini/sql/sh → LF) + пилот UX-диалога

**Дата:** 2026-10-07
**Автор DS:** DeepSeek
**Исполнитель:** KODA
**Ветка:** feature/dockerization
**Приоритет:** средний

## 1. Цель

Две независимые правки:

- **Часть A.** Дополнить `EXCHANGE\.gitattributes` правилами для
  `*.json`, `*.ini`, `*.sql`, `*.sh` → `text eol=lf`. Добавить комментарии.
  `*.md` — **оставить `eol=crlf`** (решение Vitaly), добавить поясняющий комментарий.
- **Часть B.** Пилот UX-диалога: заменить **один** `messagebox.showinfo("О программе", ...)`
  (строка 3123 в `SRC\gui_app.py`) на кастомный `tk.Toplevel` с кнопкой «Копировать».
  Образец — существующий Toplevel-диалог (строки 3574–3596).

Остальные 40+ messagebox **не трогать** — это следующий DS (DS_115, опционально).

## 2. Что менять

### Часть A — `EXCHANGE\.gitattributes`

Текущее содержимое (после DS_104):

```
# Auto detect text files and perform LF normalization
* text=auto

# Source code
*.py  text eol=lf
*.js  text eol=lf
*.ts  text eol=lf

# Windows scripts
*.cmd text eol=crlf
*.bat text eol=crlf
*.ps1 text eol=crlf

# Markdown
*.md  text eol=crlf

# YAML
*.yaml text eol=lf
*.yml  text eol=lf

# Binary
*.png binary
*.jpg binary
*.zip binary
```

**Целевое содержимое** (добавить 4 строки + комментарии):

```
# Auto detect text files and perform LF normalization
* text=auto

# Source code
*.py  text eol=lf
*.js  text eol=lf
*.ts  text eol=lf

# Data / config / scripts
*.json text eol=lf
*.ini  text eol=lf
*.sql  text eol=lf
*.sh   text eol=lf

# Windows scripts
*.cmd text eol=crlf
*.bat text eol=crlf
*.ps1 text eol=crlf

# Markdown — CRLF для корректного отображения в Notepad на Windows
# (отчёты KODA генерируются на Windows; git хранит с LF, checkout — CRLF)
*.md  text eol=crlf

# YAML
*.yaml text eol=lf
*.yml  text eol=lf

# Binary
*.png binary
*.jpg binary
*.zip binary
```

**Действия:**

1. Прочитать текущий `.gitattributes` (`Get-Content -Encoding UTF8`).
2. Сформировать новый текст через `-join` массив строк.
3. Записать `[System.IO.File]::WriteAllText($path, $text, UTF8Encoding($false))`.
4. **Не использовать** `@"..."@`.
5. Проверить: `Select-String -Path ".gitattributes" -Pattern "json|ini|sql|sh " -Encoding UTF8`.

### Часть B — пилот UX-диалога в `SRC\gui_app.py`

**Шаг B.1. Разведка — изучить прецедент.**

Прочитать `SRC\gui_app.py` строки **3570–3620** (контекст существующего Toplevel-диалога).
Зафиксировать в §5 отчёта:
- имя метода/класса;
- как создаётся Toplevel;
- как реализованы кнопки;
- есть ли уже копирование в буфер.

**Шаг B.2. Создать вспомогательный метод.**

Добавить в класс `DBIMigrationApp` метод (место — рядом с существующим
Toplevel-диалогом, после строки ~3620):

```python
def _show_copyable_dialog(self, title: str, text: str, kind: str = "info"):
    """DS_114: кастомный диалог с кнопкой «Копировать».

    kind: "info" | "warning" | "error" — влияет на иконку/заголовок.
    Нативный messagebox не поддерживает копирование — используется tk.Toplevel.
    """
    dialog = tk.Toplevel(self.root)
    dialog.title(title)
    dialog.transient(self.root)
    dialog.grab_set()
    dialog.resizable(True, True)

    # Текстовое поле (read-only, но с возможностью выделения)
    txt = tk.Text(dialog, wrap="word", width=80, height=15)
    txt.insert("1.0", text)
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True, padx=10, pady=(10, 5))

    # Фрейм кнопок
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))

    def _copy():
        dialog.clipboard_clear()
        dialog.clipboard_append(text)
        self.log("Текст диалога скопирован в буфер обмена", "info")

    tk.Button(btn_frame, text="Копировать", command=_copy).pack(side="left", padx=(0, 5))
    tk.Button(btn_frame, text="Закрыть", command=dialog.destroy).pack(side="right")

    dialog.update_idletasks()
    # Центрирование относительно root
    x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
    y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
    dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
```

**Шаг B.3. Заменить один messagebox.**

Найти строку **3123**:

```python
        messagebox.showinfo(
            "О программе",
            f"АРМ 'Адаптация под DBI' {current_version}\n\n"
            "Автоматизированное рабочее место для миграции\n"
            ...
        )
```

Заменить на:

```python
        self._show_copyable_dialog(
            "О программе",
            f"АРМ 'Адаптация под DBI' {current_version}\n\n"
            "Автоматизированное рабочее место для миграции\n"
            ...
        )
```

**Полный текст сообщения «О программе»** — сохранить без изменений
(взять из текущего кода, строки 3123–3130).

**Шаг B.4. Проверка синтаксиса.**

- `python -c "import ast; ast.parse(open('SRC/gui_app.py', encoding='utf-8').read())"` — exit 0.
- `python -m pytest SRC\tests\ -q` — exit 0 (регресс).

## 3. Стандартные ограничения

- Не трогать остальные messagebox (40+).
- Не трогать валидацию путей (3190–3720).
- Не трогать `AGENTS.md`, `DS_STANDARD.md`.
- Логи — только `EXCHANGE\bot.log`.
- Отчёт — `EXCHANGE\OUTBOX\DS_114_gitattributes_ux_pilot_report.md`.
- Задание — `EXCHANGE\PROCESSED\DS_114_gitattributes_ux_pilot.md`.
- Кодировка .py/.md — UTF-8 **без BOM** (`UTF8Encoding($false)`).
- **Русский язык** отчёта. Транслит запрещён.
- Git add — прямые слэши.

## 4. Разведка (перед правкой)

Выполнить и зафиксировать в §5:

1. `Get-Content ".gitattributes" -Encoding UTF8` — текущее содержимое.
2. `Select-String -Path "SRC\gui_app.py" -Pattern "_show_copyable_dialog|def _show.*dialog" -Encoding UTF8`
   — убедиться, что метода ещё нет.
3. `Select-String -Path "SRC\gui_app.py" -Pattern "messagebox.showinfo\(\s*$" -Encoding UTF8 -Context 0,1`
   — найти строку 3123 «О программе».
4. Прочитать строки 3570–3620 `SRC\gui_app.py` — прецедент Toplevel.
5. `(Get-Content "SRC\gui_app.py" -Encoding UTF8).Count` — текущее число строк.

## 5. Реализация

### Часть A — .gitattributes

1. Прочитать, сформировать новый текст `-join`.
2. Записать `WriteAllText` + `UTF8Encoding($false)`.
3. `Select-String` по `json|ini|sql|sh ` — должно найтись.

### Часть B — gui_app.py

1. Прочитать строки 3570–3620 (прецедент).
2. Вставить метод `_show_copyable_dialog` после ~3620.
3. Заменить `messagebox.showinfo("О программе", ...)` (строка ~3123)
   на `self._show_copyable_dialog("О программе", ...)`.
4. Проверить `ast.parse`.
5. pytest — exit 0.

### Проверка

- `Select-String` по `_show_copyable_dialog` — 2 вхождения
  (определение + вызов).
- BOM-check: `SRC\gui_app.py BOM=False`, `.gitattributes BOM=False`.
- `git diff --stat` — `SRC/gui_app.py` + `.gitattributes`.
- pytest — exit 0.

### Отчёт

- `EXCHANGE\OUTBOX\DS_114_gitattributes_ux_pilot_report.md` (UTF-8 без BOM, русский).
- §5 обязателен: Select-String / BOM / git log / pytest.

### Перенос задания

- Переместить `DS_114_gitattributes_ux_pilot.md` из INBOX (или откуда фактически)
  в `EXCHANGE\PROCESSED\`.
- **Проверить** `Test-Path` в PROCESSED.

## 6. Формат отчёта

Стандартный (DS_STANDARD.md §3, 6 разделов):
1. Что сделано
2. Изменённые файлы
3. Результат тестов (pytest — exit code)
4. Расхождения
5. **Проверка** (Select-String / BOM / git log / pytest — обязательно)
6. Артефакты (коммит, push)

## 7. Git

- **Не коммитить** без отдельной команды `GIT` от Vitaly.
- Имя коммита (если будет): `DS_114: .gitattributes (json/ini/sql/sh → LF) + пилот UX-диалога (О программе)`.
- Push — только по команде `PUSH`.

## 8. Ожидание

| Параметр | Ожидание |
|---|---|
| `.gitattributes` | +4 правила + 2 комментария |
| `SRC\gui_app.py` | +1 метод (~35 строк), −1 messagebox, +1 вызов |
| BOM | False для обоих файлов |
| pytest | exit 0 |
| `git diff --stat` | 2 файла |
| Отчёт | `DS_114_gitattributes_ux_pilot_report.md` |
| Задание | `DS_114_gitattributes_ux_pilot.md` в PROCESSED |

## 9. Риски

- **Tk-потокобезопасность:** messagebox «О программе» вызывается из главного потока
  (не из `root.after`), поэтому Toplevel безопасен. Если бы вызов был из потока —
  потребовался бы `root.after(0, ...)`.
- **Дублирование стиля:** существующий Toplevel (3574–3596) может иметь свой стиль.
  Новый метод — самостоятельный, но визуально совместимый. Если прецедент сильно
  отличается — согласовать с Vitaly.
- **Размер gui_app.py:** +35 строк — не критично (было 345392 B).