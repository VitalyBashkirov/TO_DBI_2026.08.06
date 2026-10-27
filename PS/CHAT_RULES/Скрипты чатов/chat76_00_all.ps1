Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$start76 = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\76.Старт.txt'
$relStart = 'PS/CHAT_RULES/Старт новых чатов/76.Старт.txt'
$pamyatka = 'F:\TO_DBI\PS\CHAT_RULES\Отчеты\Памятка_чатов.txt'
$relPam = 'PS/CHAT_RULES/Отчеты/Памятка_чатов.txt'
$relSelf = 'PS/CHAT_RULES/Скрипты чатов/chat76_00_all.ps1'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_76_00_start.log')
$msgFile = Join-Path $PSDir ($hostTag + '_76_00_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    $s = New-Object System.Collections.Generic.List[string]
    $s.Add('============================================')
    $s.Add('  76.СТАРТ (сгенерировано 2026-10-27 из чата 75)')
    $s.Add('  Хост: LGGRAMA8V7Q8U (hostTag=LG) / MATEBOOKE (hostTag=MBE)')
    $s.Add('============================================')
    $s.Add('')
    $s.Add('## Где искать правила (ОБЯЗАТЕЛЬНО в новом чате)')
    $s.Add('F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\')
    $s.Add('  CHAT_RULES в git с 7d64b18; PS/*.log вне git (DS_129).')
    $s.Add('  00_INDEX.md -> 01..08; 01_Правила_PS.md: 64_11, 64_12, 64_13, 64_14, 64_15, 64_16.')
    $s.Add('')
    $s.Add('## Статус на 2026-10-27 (после чата 75)')
    $s.Add('- HEAD = d5cc216; origin == HEAD, ahead нет; ?? — нет.')
    $s.Add('- Регресс: 401 passed / 1 skipped.')
    $s.Add('- Тест: SRC/tests/test_ds74_01_gui_checklist.py (12 passed / 1 skipped).')
    $s.Add('- Действуют: 64_11, 64_12, 64_13, 64_14, 64_15, 64_16, ДВОБ.')
    $s.Add('- Скрипты чатов: 74, 75_00..75_06 — в git; 76_00 — самокоммит (B).')
    $s.Add('')
    $s.Add('## Долги 75 -> 76')
    $s.Add('1. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1) — не коммитить (M; .gitignore не трогает уже отслеживаемые).')
    $s.Add('2. *.ds*bak* — вне git (.gitignore).')
    $s.Add('3. Интерактивная вставка — 64_14/64_15; класс закрыт.')
    $s.Add('4. BOM — 65_3 действует.')
    $s.Add('5. 02_k1_ika_has_plp SKIPPED — ИКА пуст; при желании создать F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\*.plp.')
    $s.Add('6. *.ps1 «хвост» — закрыт (75_06, B: самокоммит); в 76 — B для всех скриптов.')
    $s.Add('')
    $s.Add('## Первые шаги чата 76')
    $s.Add('1. Прочитать 00_INDEX.md -> 01..08; 01_Правила_PS.md: 64_11..64_16.')
    $s.Add('2. Прочитать Отчеты\74.Отчёт.txt, 75_00..75_06 в git.')
    $s.Add('3. Взять долг 3/4/5/6 — или новую задачу (например, ИКА: patch_suboptimal_test_3\*.plp).')
    $s.Add('4. Действовать по 04, 05, 06, 07, 64_11..64_16, 65_1..65_3, 66_1/66_2, 67_1, 68_1.')
    $encS = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($start76, $s, $encS)
    $sb = [System.IO.File]::ReadAllBytes($start76)
    if ($sb.Length -ge 3 -and $sb[0] -eq 0xEF -and $sb[1] -eq 0xBB -and $sb[2] -eq 0xBF) { throw '76.Старт.txt с BOM — 64_4' }
    Write-Host '76.Старт.txt записан:' $s.Count 'строк,' $sb.Length 'B, no-BOM'
    if (Test-Path $pamyatka) {
        Copy-Item $pamyatka ($pamyatka + '.ds76_00bak') -Force
        Write-Host 'Бэкап: ' ($pamyatka + '.ds76_00bak')
        $pb = [System.IO.File]::ReadAllBytes($pamyatka)
        $pBomBefore = ($pb.Length -ge 3 -and $pb[0] -eq 0xEF -and $pb[1] -eq 0xBB -and $pb[2] -eq 0xBF)
        $pt = [System.IO.File]::ReadAllText($pamyatka, [System.Text.Encoding]::UTF8)
        if ($pt -notmatch '(?m)^## Чат 75 \(ЗАКРЫТ\)') {
            $add = "`r`n## Чат 75 (ЗАКРЫТ)`r`n`r`n- 75_00..75_06; HEAD d5cc216; ?? — нет; регресс 401/1; скрипты 75 в git; самокоммит B.`r`n"
            $pt = $pt.TrimEnd() + $add
        }
        if ($pt -notmatch '(?m)^## Чат 76 \(В РАБОТЕ\)') {
            $add2 = "`r`n## Чат 76 (В РАБОТЕ)`r`n`r`n- Старт 76: 76.Старт.txt; первые шаги — см. 76.Старт.txt.`r`n"
            $pt = $pt.TrimEnd() + $add2
        }
        $encP = if ($pBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($pamyatka, $pt, $encP)
        $pb2 = [System.IO.File]::ReadAllBytes($pamyatka)
        $pBomAfter = ($pb2.Length -ge 3 -and $pb2[0] -eq 0xEF -and $pb2[1] -eq 0xBB -and $pb2[2] -eq 0xBF)
        if ($pBomBefore -ne $pBomAfter) { throw 'BOM Памятка_чатов.txt не совпал (65_3)' }
        Write-Host 'Памятка_чатов.txt дополнена:' $pb2.Length 'B, BOM=' $pBomAfter
    } else { Write-Host 'Памятка_чатов.txt не найдена — пропуск (не создаём)' }
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('76_00: старт чата 76')
    $msgLines.Add('')
    $msgLines.Add('- 76.Старт.txt: HEAD d5cc216, 64_11..64_16, долги 75->76, первые шаги.')
    $msgLines.Add('- Памятка_чатов.txt: 75 ЗАКРЫТ, 76 В РАБОТЕ.')
    $msgLines.Add('- chat76_00_all.ps1 — самокоммит (B): скрипт сам себя добавляет в git.')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- $relStart $relPam $relSelf 2>&1 | Out-String | Write-Host
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
        $sb2 = & git -C $root status -sb 2>&1
        $sb2 | Out-String | Write-Host
        if ($sb2 -match '\[ahead \d+\]') { throw 'После push осталось [ahead N]' }
        & git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host
    } finally { $ErrorActionPreference = $oldEAP }
    Write-Host 'Готово: 76_00 закоммичен и запушен (самокоммит B)'
} catch {
    Write-Host 'ERROR:' $_ -ForegroundColor Red
    if (Test-Path ($pamyatka + '.ds76_00bak')) { Copy-Item ($pamyatka + '.ds76_00bak') $pamyatka -Force; Write-Host 'ОТКАТ: Памятка_чатов.txt восстановлена' }
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
