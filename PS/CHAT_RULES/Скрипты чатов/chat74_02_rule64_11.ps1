Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$PSDir  = 'F:\TO_DBI\PS'
$rules  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\01_Правила_PS.md'
$templ  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\07_Шаблон_PS.md'

$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }

$log = Join-Path $PSDir "${hostTag}_74_02_rule64_11.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

$rc = -1
try {
    if (-not (Test-Path $rules)) { throw "Нет файла: $rules" }
    if (-not (Test-Path $templ)) { throw "Нет файла: $templ" }

    $rb = [System.IO.File]::ReadAllBytes($rules)
    $rulesBomBefore = ($rb.Length -ge 3 -and $rb[0] -eq 0xEF -and $rb[1] -eq 0xBB -and $rb[2] -eq 0xBF)
    $tb = [System.IO.File]::ReadAllBytes($templ)
    $templBomBefore = ($tb.Length -ge 3 -and $tb[0] -eq 0xEF -and $tb[1] -eq 0xBB -and $tb[2] -eq 0xBF)
    Write-Host "BOM до: rules=$rulesBomBefore templ=$templBomBefore"

    Copy-Item $rules ($rules + '.ds74_02bak') -Force
    Copy-Item $templ ($templ + '.ds74_02bak') -Force

    $rt = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rt -notmatch '(?m)^##\s+64_11\.') {
        $add = "`r`n## 64_11. Обрамление PS-сеанса: первая — Clear-Host, последняя — полное имя лога зелёным (чат 74)`r`n`r`n"
        $add += "Любой ``.ps1`` (и консольный стартовый блок, 65_2) **начинается** командой ``Clear-Host`` и **заканчивается** командой ``Write-Host `"LOG: <полный_путь_к_логу>`" -ForegroundColor Green``.`r`n`r`n"
        $add += "- ``Clear-Host`` — самая первая исполняемая команда, **до** кодировок (60_1), ``$ErrorActionPreference``, ``Start-Transcript``. Цель: лог начинается с чистого экрана (64_3).`r`n"
        $add += "- ``Write-Host `"LOG: ...`"`` — самая последняя исполняемая команда, **после** ``Stop-Transcript``, очистки нулевых логов (64_10), любых ``Write-Host``-итогов. Паузы нет (10).`r`n"
        $add += "- В строке — **полный путь** к файлу лога, не только имя. Цвет — ``Green``.`r`n"
        $add += "- Между ними — всё тело. После ``Write-Host `"LOG: ...`"`` команд нет.`r`n"
        $add += "- Если скрипт упал — ``finally`` всё равно печатает ``LOG: ...`` зелёным (68_1).`r`n`r`n"
        $add += "Эталон: ``chat74_00_regress.ps1``, ``chat74_01_guicheck.ps1``.`r`n"
        $rt = $rt.TrimEnd() + $add
        $encR = if ($rulesBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($rules, $rt, $encR)
        Write-Host "01_Правила_PS.md: 64_11 добавлен"
    } else { Write-Host "01_Правила_PS.md: 64_11 уже есть" }

    $tt = [System.IO.File]::ReadAllText($templ, [System.Text.Encoding]::UTF8)
    if ($tt -notmatch '(?m)^##\s+Первая/последняя команда') {
        $m = [regex]::Match($tt, '(?s)(##\s+Первая строка.*?)(?=\r?\n##\s|\z)')
        if (-not $m.Success) { throw "Не найден раздел '## Первая строка' в 07_Шаблон_PS.md" }
        $ins = "`r`n## Первая/последняя команда (64_11, 64_3, 10, 04)`r`n`r`nПервая — ``Clear-Host``. Последняя — ``Write-Host `"LOG: `$log`" -ForegroundColor Green`` (полный путь).`r`n`r`n``````powershell`r`n# ПЕРВАЯ (64_11)`r`nClear-Host`r`n# ... тело ...`r`n# ПОСЛЕДНЯЯ (64_11)`r`nWrite-Host `"LOG: `$log`" -ForegroundColor Green`r`n```````r`n`r`nПосле ``LOG:`` команд нет; пауза запрещена (10).`r`n"
        $tt2 = $tt.Substring(0, $m.Index + $m.Length) + $ins + $tt.Substring($m.Index + $m.Length)
        $encT = if ($templBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($templ, $tt2, $encT)
        Write-Host "07_Шаблон_PS.md: раздел добавлен"
    } else { Write-Host "07_Шаблон_PS.md: раздел уже есть" }

    $rb2 = [System.IO.File]::ReadAllBytes($rules)
    $rulesBomAfter = ($rb2.Length -ge 3 -and $rb2[0] -eq 0xEF -and $rb2[1] -eq 0xBB -and $rb2[2] -eq 0xBF)
    $tb2 = [System.IO.File]::ReadAllBytes($templ)
    $templBomAfter = ($tb2.Length -ge 3 -and $tb2[0] -eq 0xEF -and $tb2[1] -eq 0xBB -and $tb2[2] -eq 0xBF)
    Write-Host "BOM после: rules=$rulesBomAfter templ=$templBomAfter"
    if ($rulesBomBefore -ne $rulesBomAfter) { throw "BOM rules не совпал (65_3)" }
    if ($templBomBefore -ne $templBomAfter) { throw "BOM templ не совпал (65_3)" }

    $rf = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rf -notmatch '(?m)^##\s+64_11\.') { throw "Маркер 64_11 не найден" }
    $tf = [System.IO.File]::ReadAllText($templ, [System.Text.Encoding]::UTF8)
    if ($tf -notmatch 'LOG:') { throw "Маркер LOG не найден в шаблоне" }
    Write-Host "Проверки OK: rules=$($rb2.Length)B templ=$($tb2.Length)B"
    $rc = 0
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    $rc = 1
} finally {
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
if ($rc -ne 0) { exit $rc }