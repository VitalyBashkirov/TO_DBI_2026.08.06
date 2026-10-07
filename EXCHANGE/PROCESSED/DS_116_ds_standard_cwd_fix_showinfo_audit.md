# DS_116. §6.2: откат подмены + правильные пункты CWD + аудит showinfo

## Мета
- Автор: DS (DeepSeek)
- Исполнитель: KODA
- Пользователь: Vitaly
- Ветка: feature/dockerization
- База: b7737b3 (DS_115)
- Тип: исправление документации + аудит кода (SRC — только чтение)
- Приоритет: средний

## Контекст

DS_115 должен был добавить в §6.2 DS_STANDARD.md:
- Пункт 0: `Set-Location -LiteralPath 'F:\TO_DBI'` + `Write-Host CWD`.
- Пункт 6 (запреты): запрет BOM-check/git/Select-String без `Set-Location`.

Фактически KODA вставил ДРУГИЕ пункты:
- Пункт 2: проверка `$OutputEncoding.BodyName` после Write-Host с кириллицей.
- Пункт 6 (запреты): запрет `MessageBox` для длинного текста.

Часть B DS_115 (3 messagebox → `_show_copyable_dialog`) выполнена КОРРЕКТНО
(строки 2754, 5376, 5590) — не трогаем.

Решение Vitaly:
1. Откатить подмену в §6.2 и переделать с нуля.
2. Зафиксировать корректность showinfo = 12.

Факты до DS_116 (проверено из корня):
- git: clean, HEAD = b7737b3, ahead 0.
- Есть untracked файл: `EXCHANGE/PROCESSED/DS_115_ds_standard_cwd_ux.md` —
  упущение DS_115, включить в коммит DS_116.
- §6.2 начинается со строки 228.
- `messagebox.showinfo` = 12 (после DS_115).
- `messagebox.showerror` = 18.
- `messagebox.showwarning` = 6.
- `_show_copyable_dialog` = 5.
- BOM = False для DS_STANDARD.md и gui_app.py.

### Уточнение по showinfo (важно!)
Исходно (до DS_115) было **15** вхождений showinfo, а НЕ 14, как ошибочно
указано в стартовом файле чата 17. После −3 (2754, 5376, 5590) = 12.
Это корректно, KODA в отчёте DS_115 был прав.
Расхождение 12 vs 11 — ошибка DS в стартовом подсчёте, НЕ пропуск KODA.

## Часть A. §6.2 DS_STANDARD.md — откат подмены + правильные пункты

Файл: `EXCHANGE\DS_STANDARD.md`

### A.1. «Обязательные элементы» — убрать BodyName-пункт 2

УДАЛИТЬ блок (факт после DS_115):

```
2. **После каждого `Write-Host` с кириллицей** — проверка вывода:
   `$OutputEncoding.BodyName` должен быть `utf-8`/`cp65001`. Иначе следующая
   команда может прочитать байты как cp1251.
```

### A.2. «Обязательные элементы» — вернуть нумерацию 2–5

ПОСЛЕ удаления BodyName-пункта восстановить:

```
2. Секции с заголовками: `# --- N. <назначение> ---`.
3. Готовность к одной кнопке (без промежуточного ввода).
4. Ожидание — таблицей **вне** блока.
5. Чтение — `-Encoding UTF8`; запись .py/.ini/.json/.md —
   `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))`.
```

### A.3. «Обязательные элементы» — добавить правильный пункт 0

ДОБАВИТЬ перед пунктом 1 («Команда 0 — кодировка»):

```
0. **`Set-Location -LiteralPath 'F:\TO_DBI'`** + `Write-Host "Текущий каталог: $(Get-Location)"`
   — первой командой после `chcp`, для контроля CWD (урок чата 16).
```

Итоговая нумерация: 0, 1, 2, 3, 4, 5.

### A.4. «Запреты» — убрать MessageBox-запрет 6

УДАЛИТЬ блок (факт после DS_115):

```
6. **`MessageBox` для длинного текста** — `messagebox.showinfo` не даёт копировать
   текст. Для лога/отчёта/длинного текста — `_show_copyable_dialog` (ScrolledText +
   кнопка «Копировать»). Пилот: DS_114, строка 3655.
```

### A.5. «Запреты» — добавить правильный пункт 6

ДОБАВИТЬ после пункта 5 («Большие блоки дробить»), ПЕРЕД подзаголовком
«Git-гигиена»:

```
6. **BOM-check / git-операции / `Select-String` без предварительного
   `Set-Location` в корень проекта** — читается не тот файл (урок чата 16).
```

### A.6. «Git-гигиена» — проверить нумерацию 7–9

Было после DS_115 (факт): 7, 8, 9.
После DS_116 (с учётом нового запрета 6): должно остаться 7, 8, 9.

Проверить, что «Git-гигиена (связано)» начинается с 7.

### A.7. Требования
- Кодировка: UTF-8 без BOM.
- Запись через `[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))`.
- Сохранить CRLF (по `.gitattributes` `*.md eol=crlf`).
- Только §6.2.

### A.8. Итоговая структура §6.2 после DS_116
- «Обязательные элементы»: 0, 1, 2, 3, 4, 5.
- «Запреты»: 1, 2, 3, 4, 5, 6 (п.6 — новый про BOM-check без Set-Location).
- «Git-гигиена (связано)»: 7, 8, 9.

## Часть B. Аудит showinfo — зафиксировать корректность

### B.1. Факт
- До DS_115: 15 showinfo (НЕ 14 — ошибка DS в стартовом подсчёте).
- DS_115 заменил 3 (2754, 5376, 5590) → 15 − 3 = 12.
- Факт после DS_115: 12 (Select-String, проверено).
- showerror = 18, showwarning = 6 — отдельные метрики, не смешаны.

### B.2. Вывод
Расхождение 12 vs 11 — ошибка DS в стартовом файле чата 17, НЕ пропуск KODA.
KODA в отчёте DS_115 указал корректно (15 → 12).

### B.3. Что зафиксировать в отчёте DS_116
- Полный список 12 вхождений showinfo (таблица: № / строка / тип / заголовок).
- Классификация: одиночные / многострочные / lambda.
- Явный вывод: 15 − 3 = 12, всё корректно.
- Указать, что стартовый подсчёт DS (14) был ошибочным.

## Часть C. Проверки (§5 обязателен)

### C.1. BOM-check (из корня!)
```powershell
Set-Location -LiteralPath 'F:\TO_DBI'
$files = @('EXCHANGE\DS_STANDARD.md')
foreach ($f in $files) {
  $abs = (Resolve-Path -LiteralPath $f).Path
  $bytes = [System.IO.File]::ReadAllBytes($abs)
  $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
  Write-Host "$f : BOM=$hasBom size=$($bytes.Length)"
}
```

### C.2. §6.2 — фактическая структура после правок
```powershell
$content = Get-Content -LiteralPath 'EXCHANGE\DS_STANDARD.md' -Encoding UTF8
$idx = ($content | Select-String -Pattern '^### 6\.2' | Select-Object -First 1).LineNumber
if ($idx) {
  Write-Host "§6.2 начинается со строки $idx"
  $content[($idx-1)..([Math]::Min($idx+70, $content.Count-1))] | ForEach-Object { Write-Host $_ }
}
```

### C.3. Аудит showinfo — финальный список
```powershell
Set-Location -LiteralPath 'F:\TO_DBI'
$m = Select-String -Path 'SRC\gui_app.py' -Pattern 'messagebox\.showinfo' -Encoding UTF8
Write-Host "Всего вхождений: $($m.Count)"
$m | ForEach-Object { Write-Host ("{0}: {1}" -f $_.LineNumber, $_.Line.Trim()) }
```
Ожидание: 12.

### C.4. showerror / showwarning
```powershell
$e = (Select-String -Path 'SRC\gui_app.py' -Pattern 'messagebox\.showerror' -Encoding UTF8).Count
$w = (Select-String -Path 'SRC\gui_app.py' -Pattern 'messagebox\.showwarning' -Encoding UTF8).Count
Write-Host "showerror = $e"
Write-Host "showwarning = $w"
```
Ожидание: showerror=18, showwarning=6.

### C.5. Регресс
```powershell
python -m pytest SRC\tests\ -q
```
Ожидание: exit code 0.

### C.6. git status после правок
```powershell
git status -sb
```

## Часть D. Git

### D.1. Один коммит + push (включая упущенное задание DS_115)
```
git add EXCHANGE/DS_STANDARD.md
git add EXCHANGE/PROCESSED/DS_115_ds_standard_cwd_ux.md
git add EXCHANGE/OUTBOX/DS_116_ds_standard_cwd_fix_showinfo_audit_report.md
git commit -m "DS_116: otkat podmeny v 6.2 + punkt CWD + audit showinfo + DS_115 zadanie"
git push
```

### D.2. Проверки
- Перед push: `git status -sb` → clean (не должно быть `??`).
- После push: `git branch -vv` → ahead 0.

## Часть E. Отчёт

Файл: `EXCHANGE\OUTBOX\DS_116_ds_standard_cwd_fix_showinfo_audit_report.md`

Содержание:
- §6.2 до/после: что удалено, что добавлено, итоговая нумерация.
- `git diff EXCHANGE/DS_STANDARD.md` (фактический).
- `git add PROCESSED/DS_115...` — подтверждение.
- Аудит showinfo: полная таблица 12 вхождений.
- Классификация: одиночные / многострочные / lambda.
- Вывод по 15 → 12: корректно, DS ошибся в стартовом подсчёте.
- showerror=18 / showwarning=6.
- BOM-check.
- pytest exit code.
- `git log --oneline -5`.
- `git branch -vv`.
- Проблемы (если были).

Требования:
- UTF-8 без BOM.
- Русский язык.
- Имя строго: `DS_116_ds_standard_cwd_fix_showinfo_audit_report.md`.

## Часть F. Ограничения
- SRC не трогать (только чтение для аудита).
- Логи — только `EXCHANGE\bot.log`.
- Никаких `return` / `@"..."@` в ручных блоках PowerShell.
- Прямые слэши в `git add`.
- Дробить большие блоки на маленькие шаги.

## Критерии приёмки
1. §6.2: BodyName-пункт удалён, нумерация 2–5 восстановлена.
2. §6.2: пункт 0 (Set-Location + Write-Host CWD) добавлен.
3. §6.2: MessageBox-запрет удалён.
4. §6.2: новый запрет 6 (BOM-check без Set-Location) добавлен.
5. §6.2: итог — обязательные 0–5, запреты 1–6, git-гигиена 7–9.
6. Аудит showinfo: полный список 12 вхождений в отчёте.
7. Вывод: 15 − 3 = 12, DS ошибся в стартовом подсчёте.
8. `EXCHANGE/PROCESSED/DS_115_ds_standard_cwd_ux.md` в git (закоммичен).
9. BOM=False для DS_STANDARD.md.
10. pytest exit 0.
11. Коммит + push, ahead 0.
12. Отчёт по регламенту.

---
