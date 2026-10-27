Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$base  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п'
$envfile = Join-Path $base '08_Окружение.md'
$rep73  = 'F:\TO_DBI\PS\CHAT_RULES\Отчеты\73.Отчёт.txt'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw "Неизвестный хост: $hostName" }
$log = Join-Path $PSDir "${hostTag}_74_04_env_chatrules.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag env=$envfile rep73=$rep73"
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $envfile)) { throw "Нет файла: $envfile" }
    if (-not (Test-Path $rep73))  { throw "Нет файла: $rep73" }
    $eb = [System.IO.File]::ReadAllBytes($envfile)
    $eBom = ($eb.Length -ge 3 -and $eb[0] -eq 0xEF -and $eb[1] -eq 0xBB -and $eb[2] -eq 0xBF)
    $rb = [System.IO.File]::ReadAllBytes($rep73)
    $rBom = ($rb.Length -ge 3 -and $rb[0] -eq 0xEF -and $rb[1] -eq 0xBB -and $rb[2] -eq 0xBF)
    Write-Host "BOM до: env=$eBom rep73=$rBom"
    Copy-Item $envfile ($envfile + '.ds74_04bak') -Force
    Copy-Item $rep73  ($rep73  + '.ds74_04bak') -Force
    $et = [System.IO.File]::ReadAllText($envfile, [System.Text.Encoding]::UTF8)
    if ($et -notmatch '(?m)^##\s+CHAT_RULES в git') {
        $add = "`r`n## CHAT_RULES в git (чат 74)`r`n`r`n"
        $add += "- ``.gitignore``: ``PS/*`` + ``!PS/CHAT_RULES/`` + ``!PS/CHAT_RULES/**``; ``PS/*.log`` вне git (DS_129 цел).`r`n"
        $add += "- Коммиты: ``f5b79e2`` (CHAT_RULES в git + 64_11 + ДВОБ), ``dc37ca2`` (64_12 + 64_13).`r`n"
        $add += "- Миф «коммит 73_03b» развеян: ``git log -- PS/CHAT_RULES`` до 74 был пуст.`r`n"
        $add += "- Действуют 64_11 (обрамление сеанса), 64_12 (без ``exit``), 64_13 (генерация PS-кодом).`r`n"
        $et = $et.TrimEnd() + $add
        $encE = if ($eBom) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($envfile, $et, $encE)
        Write-Host "08_Окружение.md: раздел CHAT_RULES в git добавлен"
    } else { Write-Host "08_Окружение.md: раздел уже есть" }
    $rt = [System.IO.File]::ReadAllText($rep73, [System.Text.Encoding]::UTF8)
    if ($rt -match 'коммит 01_Правила_PS\.md') {
        $rt2 = [regex]::Replace($rt, 'коммит 01_Правила_PS\.md', 'локальная запись 01_Правила_PS.md (в git — с чата 74, коммит f5b79e2)')
        $encR = if ($rBom) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($rep73, $rt2, $encR)
        Write-Host "73.Отчёт.txt: формулировка про коммит 01_Правила_PS.md поправлена"
    } else { Write-Host "73.Отчёт.txt: формулировка уже поправлена или отсутствует" }
    $eb2 = [System.IO.File]::ReadAllBytes($envfile)
    $eBom2 = ($eb2.Length -ge 3 -and $eb2[0] -eq 0xEF -and $eb2[1] -eq 0xBB -and $eb2[2] -eq 0xBF)
    $rb2 = [System.IO.File]::ReadAllBytes($rep73)
    $rBom2 = ($rb2.Length -ge 3 -and $rb2[0] -eq 0xEF -and $rb2[1] -eq 0xBB -and $rb2[2] -eq 0xBF)
    Write-Host "BOM после: env=$eBom2 rep73=$rBom2"
    if ($eBom -ne $eBom2) { throw "BOM 08_Окружение.md не совпал (65_3)" }
    if ($rBom -ne $rBom2) { throw "BOM 73.Отчёт.txt не совпал (65_3)" }
    $ef = [System.IO.File]::ReadAllText($envfile, [System.Text.Encoding]::UTF8)
    if ($ef -notmatch '(?m)^##\s+CHAT_RULES в git') { throw "Маркер CHAT_RULES в git не найден" }
    $rf = [System.IO.File]::ReadAllText($rep73, [System.Text.Encoding]::UTF8)
    if ($rf -match 'коммит 01_Правила_PS\.md') { throw "Старая формулировка осталась" }
    Write-Host "Проверки OK: env=$($eb2.Length)B rep73=$($rb2.Length)B"
} catch { Write-Host "ERROR: $_" -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
