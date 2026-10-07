# DS_115. DS_STANDARD §6.2 (Set-Location + CWD) + UX-расширение пилота

## Мета
- Автор: DS (DeepSeek)
- Исполнитель: KODA
- Пользователь: Vitaly
- Ветка: feature/dockerization
- База: 0205d62
- Тип: объединённый (документация + код)
- Приоритет: средний

## Контекст
Чат 16 выявил два урока:
1. BOM-check и любые ручные блоки PowerShell должны начинаться с
   Set-Location -LiteralPath 'F:\TO_DBI' + Write-Host CWD.
2. Пилот UX-диалога _show_copyable_dialog (DS_114) показал работоспособность.
   Требуется расширить на 3 messagebox.

Факты до DS (получены от KODA):
- git: clean, ahead 0, HEAD=0205d62.
- messagebox.showinfo — 14 вхождений, из них выбраны 3.
- _show_copyable_dialog: строка 3123 (вызов), 3655 (определение).
- BOM=False: DS_STANDARD.md (17879 B), gui_app.py (347202 B).

## Часть A. DS_STANDARD.md — §6.2 дополнение

Файл: EXCHANGE\DS_STANDARD.md

### A.1. В раздел «Обязательные элементы» §6.2 добавить пункт 0:

0. Первой командой после chcp:
   Set-Location -LiteralPath 'F:\TO_DBI'
   Write-Host "Текущий каталог: $(Get-Location)"
   — гарантия корректного CWD и контроль в выводе.

### A.2. В раздел «Запреты» §6.2 добавить пункт:

6. Запускать BOM-check / git-операции / Select-String без предварительного
   Set-Location в корень проекта — читается не тот файл (урок чата 16).

### A.3. Требования
- Кодировка: UTF-8 без BOM.
- Запись через [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false))).
- Сохранить CRLF (по .gitattributes *.md eol=crlf).
- Никаких других правок в DS_STANDARD.md — только §6.2.

## Часть B. UX-расширение _show_copyable_dialog

Файл: SRC\gui_app.py

### B.1. Замена №1 — строка 2754

БЫЛО:
    messagebox.showinfo("Копирование", "Журнал скопирован в буфер обмена")

СТАЛО:
    self._show_copyable_dialog("Копирование", "Журнал скопирован в буфер обмена", kind="info")

### B.2. Замена №2 — строки 5376–5379

БЫЛО:
    messagebox.showinfo(
        "Нет issues, требующих AI",
        "После фильтра «только Ai» не осталось проблем.\n"
        "Снимите галку «Только Ai» для отправки всех issues.")

СТАЛО:
    self._show_copyable_dialog(
        "Нет issues, требующих AI",
        "После фильтра «только Ai» не осталось проблем.\n"
        "Снимите галку «Только Ai» для отправки всех issues.",
        kind="info")

### B.3. Замена №3 — строки 5590–5593

БЫЛО:
    messagebox.showinfo(
        "AI-ответы обработаны",
        f"Обработано файлов: {total_ok} из {len(results)}\n\n"
        "См. Журнал выполнения и Журнал изменений.")

СТАЛО:
    self._show_copyable_dialog(
        "AI-ответы обработаны",
        f"Обработано файлов: {total_ok} из {len(results)}\n\n"
        "См. Журнал выполнения и Журнал изменений.",
        kind="info")

### B.4. Правила
- Текст и заголовок — не менять.
- Сигнатуру _show_copyable_dialog — не трогать.
- parent=self — убрать, если был (в этих трёх его нет).
- Не трогать остальные 11 messagebox (в т.ч. lambda и showerror).
- Не рефакторить метод _show_copyable_dialog.
- Не менять импорты без необходимости.

## Часть C. Проверка (§5 обязателен)

### C.1. BOM-check (из корня!)
```powershell
Set-Location -LiteralPath 'F:\TO_DBI'
$files = @('EXCHANGE\DS_STANDARD.md','SRC\gui_app.py')
foreach ($f in $files) {
  $abs = (Resolve-Path -LiteralPath $f).Path
  $bytes = [System.IO.File]::ReadAllBytes($abs)
  $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
  Write-Host "$f : BOM=$hasBom size=$($bytes.Length)"
}
C.2. Проверка замен
powershell
Select-String -Path 'SRC\gui_app.py' -Pattern '_show_copyable_dialog' |
  Select-Object LineNumber, Line | Format-Table -AutoSize -Wrap
Ожидание: 5 вхождений (определение + 1 из DS_114 + 3 новых).

C.3. Проверка, что messagebox.showinfo осталось 11
powershell
(Select-String -Path 'SRC\gui_app.py' -Pattern 'messagebox\.showinfo').Count
Ожидание: 11.

C.4. Регресс
powershell
python -m pytest SRC\tests\ -q
Ожидание: exit code 0.

C.5. git diff
powershell
git diff --stat
git diff EXCHANGE/DS_STANDARD.md
Часть D. Git
D.1. Порядок (2 коммита + push)
text
git add EXCHANGE/DS_STANDARD.md
git add EXCHANGE/OUTBOX/DS_115_ds_standard_cwd_ux_report.md
git commit -m "DS_115 A: DS_STANDARD 6.2 Set-Location + CWD"

git add SRC/gui_app.py
git add EXCHANGE/OUTBOX/DS_115_ds_standard_cwd_ux_report.md
git commit -m "DS_115 B: UX _show_copyable_dialog +3 messagebox"

git push
D.2. Проверки
Перед push: git status -sb → clean.

После push: git branch -vv → ahead 0.

Часть E. Отчёт
Файл: EXCHANGE\OUTBOX\DS_115_ds_standard_cwd_ux_report.md

Содержание:

Что изменено в §6.2 (до/после, номера пунктов).

Таблица трёх замен: строка, заголовок, статус.

BOM-check результат.

Select-String _show_copyable_dialog.

Count messagebox.showinfo (ожидание 11).

pytest exit code.

git log --oneline -5.

git branch -vv.

Проблемы (если были).

Требования:

UTF-8 без BOM.

Русский язык (DS_STANDARD.md §3.1).

Без транслита.

Имя строго: DS_115_ds_standard_cwd_ux_report.md.

Часть F. Ограничения
Не трогать SRC без явного указания (здесь указано только gui_app.py).

Логи — только EXCHANGE\bot.log.

Никаких return / @"..."@ в ручных блоках PowerShell.

Прямые слэши в git add.

Дробить большие блоки на маленькие шаги.

Критерии приёмки
§6.2 дополнен пунктами 0 и 6.

3 messagebox заменены на _show_copyable_dialog (2754, 5376-5379, 5590-5593).

messagebox.showinfo осталось 11.

BOM=False для обоих файлов.

pytest exit 0.

2 коммита + push, ahead 0.

Отчёт по регламенту.