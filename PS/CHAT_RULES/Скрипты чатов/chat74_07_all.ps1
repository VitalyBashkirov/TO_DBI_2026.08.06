Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$base  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п'
$rules = Join-Path $base '01_Правила_PS.md'
$templ = Join-Path $base '07_Шаблон_PS.md'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw "Неизвестный хост: $hostName" }
$log = Join-Path $PSDir "${hostTag}_74_07_rules64_12_13.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag rules=$rules templ=$templ"
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $rules)) { throw "Нет файла: $rules" }
    if (-not (Test-Path $templ)) { throw "Нет файла: $templ" }
    $rb = [System.IO.File]::ReadAllBytes($rules)
    $rbB = ($rb.Length -ge 3 -and $rb[0] -eq 0xEF -and $rb[1] -eq 0xBB -and $rb[2] -eq 0xBF)
    $tb = [System.IO.File]::ReadAllBytes($templ)
    $tbB = ($tb.Length -ge 3 -and $tb[0] -eq 0xEF -and $tb[1] -eq 0xBB -and $tb[2] -eq 0xBF)
    Write-Host "BOM до: rules=$rbB templ=$tbB"
    Copy-Item $rules ($rules + '.ds74_07bak') -Force
    Copy-Item $templ ($templ + '.ds74_07bak') -Force
    $rt = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rt -notmatch '(?m)^##\s+64_12\.') {
        $add = "`r`n## 64_12. Без ``exit `$rc`` в конце PS-скрипта (чат 74)`r`n`r`n"
        $add += "В конце ``.ps1`` **не использовать** ``if (`$rc -ne 0) { exit `$rc }`` и аналогичные ``exit``.`r`n`r`n"
        $add += "- Скрипт завершается сам (10); ``finally`` гарантирует ``Stop-Transcript`` и ``Write-Host `"LOG: ...`" -ForegroundColor Green`` (64_11).`r`n"
        $add += "- Успех/сбой — по ``ERROR:`` в логе, ``git add/commit/push rc=...``, ``git status -sb`` без ``[ahead N]``, ``git log -1 --oneline``.`r`n"
        $add += "- ``$rc`` — внутренняя для ``try/catch``/откатов; наружу через ``exit`` не выводится.`r`n"
        $add += "- Причина: ``exit`` конфликтует с ``finally`` (68_1), ломает ``OUTER_RC``.`r`n`r`n"
        $add += "Эталон: ``chat74_06_all.ps1``."
        $rt = $rt.TrimEnd() + $add
        $encR = if ($rbB) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($rules, $rt, $encR)
        Write-Host "01_Правила_PS.md: 64_12 добавлен"
    } else { Write-Host "01_Правила_PS.md: 64_12 уже есть" }
    $rt2 = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rt2 -notmatch '(?m)^##\s+64_13\.') {
        $add2 = "`r`n## 64_13. Единственный способ создания ``.ps1``/``.py`` — генерация PS-кодом (чат 74)`r`n`r`n"
        $add2 += "Любой ``.ps1``/``.py`` создаётся **только** PS-скриптом через ``WriteAllLines``/``WriteAllText`` (64_1 п.1-4, 65_2). **VS Code, Блокнот, копирование из чата — не используются ни при каких обстоятельствах**, включая обход зависания (73_00, 73_02b, 74_03, 74_05).`r`n`r`n"
        $add2 += "- **Генератор** — ``.ps1`` в ``Скрипты чатов\``, UTF-8 **BOM** (64_4).`r`n"
        $add2 += "- **Тело** — ``List[string]`` + ``$L.Add('...')``, одна строка файла на элемент (61_7); ``WriteAllLines`` последней после проверок (64_2).`r`n"
        $add2 += "- **BOM** после записи: ``EF BB BF`` для ``.ps1``/``.py``; нет — для ``.md``/``.txt``/``.json``/msgfile (64_4).`r`n"
        $add2 += "- **Запуск** — ``& powershell -NoProfile -ExecutionPolicy Bypass -File <target>`` (65_2); в консоли — **одна строка**.`r`n"
        $add2 += "- **Разрыв курицы-яйца** — «нулевой» генератор пишется **консольным** ``WriteAllLines`` массивом (65_2), не редактором; вложенные кавычки — ``'`` (7/61_5), here-string в консоли **запрещён**.`r`n"
        $add2 += "- **Зависли** (``>>``) — ``Ctrl+C`` → ``Test-Path`` → **повторная генерация**; VS Code/Блокнот **запрещены**.`r`n`r`n"
        $add2 += "Эталон: ``chat74_06_all.ps1``."
        $rt2 = $rt2.TrimEnd() + $add2
        $encR2 = if ($rbB) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($rules, $rt2, $encR2)
        Write-Host "01_Правила_PS.md: 64_13 добавлен"
    } else { Write-Host "01_Правила_PS.md: 64_13 уже есть" }
    $tt = [System.IO.File]::ReadAllText($templ, [System.Text.Encoding]::UTF8)
    if ($tt -notmatch '(?m)^##\s+Генерация .ps1 — только PS-кодом') {
        $ins = "`r`n## Генерация .ps1 — только PS-кодом (64_13)`r`n`r`n``````powershell`r`n$target = 'F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\chatNN_all.ps1'`r`n$L = New-Object System.Collections.Generic.List[string]`r`n$L.Add('Clear-Host')`r`n# ... ровно одна строка файла на $L.Add (61_7) ...`r`n[System.IO.File]::WriteAllLines($target, $L, (New-Object System.Text.UTF8Encoding($true)))`r`n& powershell -NoProfile -ExecutionPolicy Bypass -File $target`r`n```````r`n# VS Code/Блокнот/копирование — запрещены (64_13).`r`n"
        $tt2 = $tt.TrimEnd() + $ins
        $encT = if ($tbB) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($templ, $tt2, $encT)
        Write-Host "07_Шаблон_PS.md: блок генерации добавлен"
    } else { Write-Host "07_Шаблон_PS.md: блок генерации уже есть" }
    $rb2 = [System.IO.File]::ReadAllBytes($rules)
    $rbB2 = ($rb2.Length -ge 3 -and $rb2[0] -eq 0xEF -and $rb2[1] -eq 0xBB -and $rb2[2] -eq 0xBF)
    $tb2 = [System.IO.File]::ReadAllBytes($templ)
    $tbB2 = ($tb2.Length -ge 3 -and $tb2[0] -eq 0xEF -and $tb2[1] -eq 0xBB -and $tb2[2] -eq 0xBF)
    Write-Host "BOM после: rules=$rbB2 templ=$tbB2"
    if ($rbB -ne $rbB2) { throw "BOM rules не совпал (65_3)" }
    if ($tbB -ne $tbB2) { throw "BOM templ не совпал (65_3)" }
    $rf = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rf -notmatch '(?m)^##\s+64_12\.') { throw "Маркер 64_12 не найден" }
    if ($rf -notmatch '(?m)^##\s+64_13\.') { throw "Маркер 64_13 не найден" }
    Write-Host "Проверки OK: rules=$($rb2.Length)B templ=$($tb2.Length)B"
} catch { Write-Host "ERROR: $_" -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
