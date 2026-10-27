Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$start75 = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\75.Старт.txt'
$pamyatka = 'F:\TO_DBI\PS\CHAT_RULES\Отчеты\Памятка_чатов.txt'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_74_10b_start_pam.log')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    $s = New-Object System.Collections.Generic.List[string]
    $s.Add('============================================')
    $s.Add('  75.СТАРТ (сгенерировано 2026-10-27 из чата 74)')
    $s.Add('  Хост: LGGRAMA8V7Q8U (hostTag=LG) / MATEBOOKE (hostTag=MBE)')
    $s.Add('============================================')
    $s.Add('')
    $s.Add('## Где искать правила (ОБЯЗАТЕЛЬНО в новом чате)')
    $s.Add('F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\')
    $s.Add('  CHAT_RULES в git с 7d64b18; PS/*.log вне git (DS_129).')
    $s.Add('  00_INDEX.md -> 01..08; 01_Правила_PS.md: 64_11, 64_12, 64_13, 64_14, 64_15.')
    $s.Add('')
    $s.Add('## Статус на 2026-10-27 (после чата 74)')
    $s.Add('- HEAD = 7d64b18 (до коммита 74_10c); origin == HEAD, ahead нет.')
    $s.Add('- Регресс: 401 passed / 1 skipped.')
    $s.Add('- Тест: SRC/tests/test_ds74_01_gui_checklist.py (12 passed / 1 skipped).')
    $s.Add('- Действуют: 64_11, 64_12, 64_13, 64_14, 64_15, ДВОБ.')
    $s.Add('')
    $s.Add('## Долги 74 -> 75')
    $s.Add('1. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.')
    $s.Add('2. Бэкапы *.ds*bak* — вне git (.gitignore), не коммитить.')
    $s.Add('3. Интерактивная вставка — 64_14/64_15 действуют; класс инцидентов закрыт.')
    $s.Add('4. BOM при правке существующих .py/.ps1 — 65_3; тест test_ds74_01_gui_checklist.py — BOM=True (= test_ds183).')
    $s.Add('5. Тест 02_k1_ika_has_plp SKIPPED — ИКА пуст; при желании создать F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\*.plp (вне теста).')
    $s.Add('')
    $s.Add('## Первые шаги чата 75')
    $s.Add('1. Прочитать 00_INDEX.md -> 01..08; 01_Правила_PS.md: 64_11, 64_12, 64_13, 64_14, 64_15.')
    $s.Add('2. Прочитать Отчеты\74.Отчёт.txt.')
    $s.Add('3. Взять долг 3/4/5 — или новую задачу.')
    $s.Add('4. Действовать по 04, 05, 06, 07, 64_11..64_15, 65_1..65_3, 66_1/66_2, 67_1, 68_1.')
    $encS = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($start75, $s, $encS)
    $sb = [System.IO.File]::ReadAllBytes($start75)
    if ($sb.Length -ge 3 -and $sb[0] -eq 0xEF -and $sb[1] -eq 0xBB -and $sb[2] -eq 0xBF) { throw '75.Старт.txt с BOM — 64_4' }
    Write-Host '75.Старт.txt записан:' $s.Count 'строк,' $sb.Length 'B, no-BOM'
    if (Test-Path $pamyatka) {
        Copy-Item $pamyatka ($pamyatka + '.ds74_10bbak') -Force
        Write-Host 'Бэкап: ' ($pamyatka + '.ds74_10bbak')
        $pb = [System.IO.File]::ReadAllBytes($pamyatka)
        $pBomBefore = ($pb.Length -ge 3 -and $pb[0] -eq 0xEF -and $pb[1] -eq 0xBB -and $pb[2] -eq 0xBF)
        $pt = [System.IO.File]::ReadAllText($pamyatka, [System.Text.Encoding]::UTF8)
        if ($pt -notmatch '(?m)^## Чат 74 \(ЗАКРЫТ\)') {
            $add = "`r`n## Чат 74 (ЗАКРЫТ)`r`n`r`n- CHAT_RULES в git (f5b79e2, dc37ca2, 7d64b18); 64_11..64_15; ДВОБ; тест 12 passed / 1 skipped; регресс 401/1.`r`n"
            $pt = $pt.TrimEnd() + $add
        }
        if ($pt -notmatch '(?m)^## Чат 75 \(В РАБОТЕ\)') {
            $add2 = "`r`n## Чат 75 (В РАБОТЕ)`r`n`r`n- Старт 75: 75.Старт.txt; первые шаги — см. 75.Старт.txt.`r`n"
            $pt = $pt.TrimEnd() + $add2
        }
        $encP = if ($pBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($pamyatka, $pt, $encP)
        $pb2 = [System.IO.File]::ReadAllBytes($pamyatka)
        $pBomAfter = ($pb2.Length -ge 3 -and $pb2[0] -eq 0xEF -and $pb2[1] -eq 0xBB -and $pb2[2] -eq 0xBF)
        if ($pBomBefore -ne $pBomAfter) { throw 'BOM Памятка_чатов.txt не совпал (65_3)' }
        Write-Host 'Памятка_чатов.txt дополнена:' $pb2.Length 'B, BOM=' $pBomAfter
    } else { Write-Host 'Памятка_чатов.txt не найдена — пропуск (не создаём)' }
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
