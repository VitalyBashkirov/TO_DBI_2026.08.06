Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$pam = 'F:\TO_DBI\PS\CHAT_RULES\Отчеты\Памятка_чатов.txt'
$blk = 'F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\chat69_01c_block.txt'
if (-not (Test-Path $pam)) { throw "Нет Памятки: $pam" }
if (-not (Test-Path $blk)) { throw "Нет блока: $blk" }
$old = [System.IO.File]::ReadAllText($pam, [System.Text.Encoding]::UTF8)
$add = [System.IO.File]::ReadAllText($blk, [System.Text.Encoding]::UTF8)
$new = $old.TrimEnd() + "`r`n" + $add
$enc = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($pam, $new, $enc)
$b = [System.IO.File]::ReadAllBytes($pam)
$isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
if ($isBom) { throw "BOM в Памятке — нарушение 64_4" }
Write-Host ("Памятка обновлена: {0} байт, BOM={1}" -f $b.Length, $isBom)
Write-Host "--- tail ---"
[System.IO.File]::ReadAllLines($pam, [System.Text.Encoding]::UTF8) | Select-Object -Last 16 | Out-String | Write-Host
Write-Host "LOG: chat69_01d_pamyatka DONE" -ForegroundColor Green
