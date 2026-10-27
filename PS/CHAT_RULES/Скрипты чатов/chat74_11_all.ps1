Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$base  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п'
$rules = Join-Path $base '01_Правила_PS.md'
$templ = Join-Path $base '07_Шаблон_PS.md'
$envf  = Join-Path $base '08_Окружение.md'
$relRules = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/01_Правила_PS.md'
$relTempl = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/07_Шаблон_PS.md'
$relEnv   = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/08_Окружение.md'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_74_11_rules64_14_15.log')
$msgFile = Join-Path $PSDir ($hostTag + '_74_11_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $rules)) { throw 'Нет файла: ' + $rules }
    if (-not (Test-Path $templ)) { throw 'Нет файла: ' + $templ }
    if (-not (Test-Path $envf))  { throw 'Нет файла: ' + $envf }
    $rb = [System.IO.File]::ReadAllBytes($rules)
    $rbB = ($rb.Length -ge 3 -and $rb[0] -eq 0xEF -and $rb[1] -eq 0xBB -and $rb[2] -eq 0xBF)
    $tb = [System.IO.File]::ReadAllBytes($templ)
    $tbB = ($tb.Length -ge 3 -and $tb[0] -eq 0xEF -and $tb[1] -eq 0xBB -and $tb[2] -eq 0xBF)
    Write-Host 'BOM до: rules=' $rbB ' templ=' $tbB
    Copy-Item $rules ($rules + '.ds74_11bak') -Force
    Copy-Item $templ ($templ + '.ds74_11bak') -Force
    $rt = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rt -notmatch '(?m)^##\s+64_14\.') {
        $add = "`r`n## 64_14. Генерация .ps1 и запуск - одним блоком с Test-Path (чат 74)`r`n`r`n"
        $add += "Любой шаг, создающий .ps1, **обязан** содержать в **одном** консольном блоке: (1) WriteAllLines массивом; (2) Test-Path целевого файла **одной строкой**; (3) & powershell -File <target> - **только** если Test-Path = True.`r`n`r`n"
        $add += "- if/elseif/else на верхнем уровне консоли **запрещены** (64_15); проверка - Test-Path **одной строкой**, решение - глазами.`r`n"
        $add += "- Живой инцидент 74_09: -File на несуществующий .ps1 - The argument does not exist.`r`n`r`n"
        $add += "Эталон: chat74_09_all.ps1."
        $rt = $rt.TrimEnd() + $add
        $encR = if ($rbB) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($rules, $rt, $encR)
        Write-Host '01_Правила_PS.md: 64_14 добавлен'
    } else { Write-Host '01_Правила_PS.md: 64_14 уже есть' }
    $rt2 = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rt2 -notmatch '(?m)^##\s+64_15\.') {
        $add2 = "`r`n## 64_15. В консольном блоке - без if/elseif/else на верхнем уровне (чат 74)`r`n`r`n"
        $add2 += "В **консольной** вставке PS 5.1 if/elseif/else, try/finally, foreach на верхнем уровне **рвутся** (73_00, 74_09: elseif/else вне if - CommandNotFoundException).`r`n`r`n"
        $add2 += "- В консоли - **только** WriteAllLines массивом + Write-Host GEN OK. Проверки - Test-Path **одной строкой** (64_14).`r`n"
        $add2 += "- Все if/else - **внутри** .ps1 (try/catch/finally, 68_1).`r`n`r`n"
        $add2 += "Эталон: chat74_09_all.ps1."
        $rt2 = $rt2.TrimEnd() + $add2
        $encR2 = if ($rbB) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($rules, $rt2, $encR2)
        Write-Host '01_Правила_PS.md: 64_15 добавлен'
    } else { Write-Host '01_Правила_PS.md: 64_15 уже есть' }
    $tt = [System.IO.File]::ReadAllText($templ, [System.Text.Encoding]::UTF8)
    if ($tt -notmatch '(?m)^##\s+Генерация\+запуск - одним блоком') {
        $ins = "`r`n## Генерация+запуск - одним блоком с Test-Path (64_14)`r`n`r`n"
        $ins += "``````powershell`r`n"
        $ins += "$target = 'F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\chatNN_all.ps1'" + "`r`n"
        $ins += "$L = New-Object System.Collections.Generic.List[string]" + "`r`n"
        $ins += "# ... WriteAllLines массивом ..." + "`r`n"
        $ins += "[System.IO.File]::WriteAllLines($target, $L, (New-Object System.Text.UTF8Encoding($true)))" + "`r`n"
        $ins += "Write-Host GEN OK: $target -ForegroundColor Green" + "`r`n"
        $ins += "```````r`n`r`n"
        $ins += "Затем **одной строкой**: Test-Path $target; если True - **одной строкой** & powershell -NoProfile -ExecutionPolicy Bypass -File $target. **Без** if/else в консоли (64_15).`r`n"
        $tt2 = $tt.TrimEnd() + $ins
        $encT = if ($tbB) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($templ, $tt2, $encT)
        Write-Host '07_Шаблон_PS.md: блок 64_14 добавлен'
    } else { Write-Host '07_Шаблон_PS.md: блок 64_14 уже есть' }
    $rb2 = [System.IO.File]::ReadAllBytes($rules)
    $rbB2 = ($rb2.Length -ge 3 -and $rb2[0] -eq 0xEF -and $rb2[1] -eq 0xBB -and $rb2[2] -eq 0xBF)
    $tb2 = [System.IO.File]::ReadAllBytes($templ)
    $tbB2 = ($tb2.Length -ge 3 -and $tb2[0] -eq 0xEF -and $tb2[1] -eq 0xBB -and $tb2[2] -eq 0xBF)
    Write-Host 'BOM после: rules=' $rbB2 ' templ=' $tbB2
    if ($rbB -ne $rbB2) { throw 'BOM rules не совпал (65_3)' }
    if ($tbB -ne $tbB2) { throw 'BOM templ не совпал (65_3)' }
    $rf = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
    if ($rf -notmatch '(?m)^##\s+64_14\.') { throw 'Маркер 64_14 не найден' }
    if ($rf -notmatch '(?m)^##\s+64_15\.') { throw 'Маркер 64_15 не найден' }
    Write-Host 'Проверки OK: rules=' $rb2.Length 'B templ=' $tb2.Length 'B'
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('74_11: 64_14 (генерация+запуск одним блоком) + 64_15 (без if/else в консоли)')
    $msgLines.Add('')
    $msgLines.Add('- 01_Правила_PS.md: 64_14 - Test-Path одной строкой до -File; 64_15 - без if/elseif/else в консоли.')
    $msgLines.Add('- 07_Шаблон_PS.md: блок Генерация+запуск - одним блоком с Test-Path (64_14).')
    $msgLines.Add('- 08_Окружение.md: раздел CHAT_RULES в git (чат 74) (74_04).')
    $encNoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encNoBom)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    $msgBom = ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF)
    if ($msgBom) { throw 'msgfile с BOM - 11' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- $relRules $relTempl $relEnv 2>&1 | Out-String | Write-Host
        $addRc = $LASTEXITCODE
        Write-Host 'git add rc=' $addRc
        if ($addRc -ne 0) { throw 'git add rc=' + $addRc }
        & git -C $root commit -F $msgFile 2>&1 | Out-String | Write-Host
        $commitRc = $LASTEXITCODE
        Write-Host 'git commit rc=' $commitRc
        if ($commitRc -ne 0) { throw 'git commit rc=' + $commitRc }
        & git -C $root push origin feature/dockerization 2>&1 | Out-String | Write-Host
        $pushRc = $LASTEXITCODE
        Write-Host 'git push rc=' $pushRc
        if ($pushRc -ne 0) { throw 'git push rc=' + $pushRc }
        $sb = & git -C $root status -sb 2>&1
        $sb | Out-String | Write-Host
        if ($sb -match '\[ahead \d+\]') { throw 'После push осталось [ahead N]' }
        & git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host
    } finally { $ErrorActionPreference = $oldEAP }
    Write-Host 'Готово: 64_14 + 64_15 + 08_Окружение закоммичены и запушены'
} catch {
    Write-Host 'ERROR:' $_ -ForegroundColor Red
    if (Test-Path ($rules + '.ds74_11bak')) { Copy-Item ($rules + '.ds74_11bak') $rules -Force; Write-Host 'ОТКАТ: 01_Правила_PS.md восстановлен' }
    if (Test-Path ($templ + '.ds74_11bak')) { Copy-Item ($templ + '.ds74_11bak') $templ -Force; Write-Host 'ОТКАТ: 07_Шаблон_PS.md восстановлен' }
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
