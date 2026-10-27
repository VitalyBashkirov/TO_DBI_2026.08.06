# chat64_07_add_rule_64_10.ps1 (chat 64)
# Дописывает 64_10 в 01_Правила_PS.md (подпапка 01_08). BOM (.ps1, 64_4).

Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$p = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\01_Правила_PS.md'
if (-not (Test-Path $p)) { throw "Нет: $p" }
$size0 = (Get-Item $p).Length
if ($size0 -lt 1000) { throw "Мал: $size0 b" }
Write-Host "size_before=$size0"

$bkDir = 'F:\TO_DBI\PS\CHAT_RULES\_backup_path_fix'
if (-not (Test-Path $bkDir)) { New-Item -ItemType Directory -Path $bkDir | Out-Null }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$bk = Join-Path $bkDir ("01_Правила_PS.md.bak_{0}" -f $stamp)
Copy-Item -LiteralPath $p -Destination $bk -Force
Write-Host "backup=$bk"

$t = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
if ($t -match '## 64_10\.') { Write-Host '[SKIP] 64_10 already present'; return }
if (-not $t.EndsWith("`r`n")) { $t += "`r`n" }

$A = @(
'## 64_10. Удаление нулевых логов — не трогать активный Start-Transcript (чат 64)','
'`Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 } | Remove-Item -Force`','
'в конце шага может задеть АКТИВНЫЙ лог (свой или внешний), если','
'`Stop-Transcript` ещё не выполнен или лог пишется другим процессом.','
'Симптом: `Remove-Item : Cannot remove item ... being used by another process`','
'→ `gen_exitcode=1` при зелёных тестах (инцидент chat64_06_fix4).','
'Решение:','
'1. Исключать активный лог из удаления:','
'   `Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) }`','
'2. `Stop-Transcript` — ДО удаления (активный — внешний, не наш).','
'3. `Remove-Item -ErrorAction SilentlyContinue` + `try/catch`, чтобы не валить exit code.','
'4. Не удалять `*.log` с LastWriteTime < 1 мин (активные).','
'"'
')

$t += ($A -join "`r`n")
$encNoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($p, $t, $encNoBom)
$size1 = (Get-Item $p).Length
Write-Host "size_after=$size1"
if ($size1 -le $size0) { throw "Не выросло: $size0 -> $size1" }

$chk = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
Write-Host "=== 64_* ==="
(($chk -split "`r?`n") | Where-Object { $_ -match '^## 64_' }) -join "`n" | Write-Host
Write-Host '[OK] chat64_07_add_rule_64_10.ps1 finished'
