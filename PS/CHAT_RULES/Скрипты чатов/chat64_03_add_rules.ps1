# chat64_03_add_rules.ps1 (chat 64)
# Дописывает 64_1, 64_2, 64_3, 64_4 в 01_Правила_PS.md (подпапка 01_08).
# Файл .ps1 записан с BOM (64_4).

Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$p = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\01_Правила_PS.md'
if (-not (Test-Path $p)) { throw "Нет файла: $p" }
$size0 = (Get-Item $p).Length
if ($size0 -lt 1000) { throw "Файл подозрительно мал: $size0 b" }
Write-Host "size_before=$size0"

$bkDir = 'F:\TO_DBI\PS\CHAT_RULES\_backup_path_fix'
if (-not (Test-Path $bkDir)) { New-Item -ItemType Directory -Path $bkDir | Out-Null }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$bk = Join-Path $bkDir ("01_Правила_PS.md.bak_{0}" -f $stamp)
Copy-Item -LiteralPath $p -Destination $bk -Force
Write-Host "backup=$bk"

$t = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
if ($t -match '## 64_1\.') { Write-Host '[SKIP] 64_1 already present'; return }
if (-not $t.EndsWith("`r`n")) { $t += "`r`n" }

$A = @(
'## 64_1. Генерация .ps1/.py — только PS-кодом, запуск одним блоком (чат 64)','
'Если в чате требуется создать файл .ps1 или .py:','
'1. Пишется PS-код, который генерирует файл через WriteAllText/WriteAllLines.','
'2. Генератор кладётся в F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\.','
'3. Сгенерированные .ps1/.py — тоже туда.','
'4. Генерация и запуск — ОДНИМ блоком/шагом (62_1).','
'5. Копирование в Блокнот/VS Code вручную — ЗАПРЕЩЕНО (63_1, 6at-1, 7, 61_5).','
'6. Кодировка по расширению — см. 64_4.','
'"'
'## 64_2. Многострочные блоки, меняющие файлы — только как .ps1 через -File (чат 64)','
'Построчная вставка многострочного блока в консоль PS 5.1:','
'- выполняет каждую строку независимо;','
'- throw / $ErrorActionPreference='Stop' НЕ останавливают последующие строки;','
'- WriteAllText/WriteAllLines с пустым/частичным $idx может УНИЧТОЖИТЬ файл.','
'Правило:','
'1. Любой блок >5 строк, меняющий файлы, — в .ps1 (Скрипты чатов\) и запускать через -File.','
'2. Перед записью — Test-Path и проверка размера исходника (>0).','
'3. WriteAllText — только последней строкой, после успешных проверок.','
'4. Бэкап исходника — ДО любых чтений/замен.','
'"'
'## 64_3. Первая команда в новом PS-сеансе — Clear-Host (чат 64)','
'В начало любого нового сеанса PS 5.1:','
'  Clear-Host','
'  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8','
'  $OutputEncoding = [System.Text.Encoding]::UTF8','
'  $PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'','
'  $ErrorActionPreference = 'Stop'','
'Clear-Host — ДО 60_1 (русская кодировка). Причина: убрать шум предыдущего','
'сеанса, чтобы лог Start-Transcript начинался с чистого экрана.','
'"'
'## 64_4. BOM / кодировка по расширению — сводная таблица (чат 64)','
'PS 5.1 при -File читает .ps1 БЕЗ BOM как ANSI → кириллица превращается','
'в кракозябры → parse error (инцидент chat64_02b, 2026-10-25).','
'Кодировка записи зависит ОТ РАСШИРЕНИЯ:','
'| Расширение | BOM | Кодировка | Правило |','
'|---|---|---|---|','
'| .ps1 (с кириллицей) | ДА (EF BB BF) | UTF-8 BOM | 64_4 |','
'| .ps1 (только ASCII) | можно без, но с BOM безопаснее | UTF-8 | 64_4 |','
'| .py (с кириллицей) | ДА | UTF-8 BOM | 6at-1, 64_4 |','
'| .py (только ASCII) | без | UTF-8 | 6at-1 |','
'| .md | НЕТ | UTF-8 no-BOM | 11, 63_1, 64_4 |','
'| .txt (отчёты, старты) | НЕТ | UTF-8 no-BOM | 11, 13, 64_4 |','
'| .json | НЕТ | UTF-8 no-BOM | 11, 64_4 |','
'| msgfile (git commit -F) | НЕТ | UTF-8 no-BOM | 11, 64_4 |','
'"'
'Проверка для .ps1/.py:','
'  $b = [System.IO.File]::ReadAllBytes($p)','
'  $isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)','
'Проверка для .md/.txt/.json/msgfile: $isBom должно быть $false.','
'"'
'Практика:','
'  UTF8Encoding($true)  — BOM  (.ps1/.py с кириллицей)','
'  UTF8Encoding($false) — no-BOM (.md/.txt/.json/msgfile)','
')

$t += ($A -join "`r`n")
$encNoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($p, $t, $encNoBom)
$size1 = (Get-Item $p).Length
Write-Host "size_after=$size1"
if ($size1 -le $size0) { throw "После записи не выросло: $size0 -> $size1" }

$chk = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
Write-Host "=== проверка: заголовки 64_* ==="
(($chk -split "`r?`n") | Where-Object { $_ -match '^## 64_' }) -join "`n" | Write-Host
Write-Host '[OK] chat64_03_add_rules.ps1 finished'
