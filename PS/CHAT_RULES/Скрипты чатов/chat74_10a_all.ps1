Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$rep74 = 'F:\TO_DBI\PS\CHAT_RULES\Отчеты\74.Отчёт.txt'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_74_10a_rep.log')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (Test-Path $rep74) { Copy-Item $rep74 ($rep74 + '.ds74_10abak') -Force; Write-Host 'Бэкап: ' ($rep74 + '.ds74_10abak') } else { Write-Host '74.Отчёт.txt не было — создаём с нуля' }
    $r = New-Object System.Collections.Generic.List[string]
    $r.Add('# Отчёт чата 74 (2026-10-27, LG)')
    $r.Add('')
    $r.Add('## Главное')
    $r.Add('- Регресс на HEAD 7d64b18: 401 passed / 1 skipped (было 389; +12 новых тестов test_ds74_01_gui_checklist.py).')
    $r.Add('- CHAT_RULES в git: .gitignore PS/* + !PS/CHAT_RULES/ + !PS/CHAT_RULES/**; PS/*.log вне git (DS_129).')
    $r.Add('- Новые правила: 64_11 (обрамление: Clear-Host первой, LOG: зелёным последней), 64_12 (без exit в конце .ps1), 64_13 (единственный способ .ps1/.py — генерация PS-кодом, без VS Code/Блокнота), 64_14 (генерация+запуск одним блоком), 64_15 (без if/elseif/else в консоли).')
    $r.Add('- ДВОБ (Действую В Обход Блокировки) — в 02_Сокращения_GUI.md; ДОСБ отменён.')
    $r.Add('- Тест test_ds74_01_gui_checklist.py: 12 passed / 1 skipped; skip = 02_k1_ika_has_plp (ИКА пуст).')
    $r.Add('')
    $r.Add('## Коммиты чата 74')
    $r.Add('- f5b79e2: CHAT_RULES в git + 64_11 + ДВОБ.')
    $r.Add('- dc37ca2: 64_12 без exit + 64_13 генерация PS-кодом.')
    $r.Add('- eb5fc8a: .gitignore — *.ds*bak / *.ds*_prev / *.bak_*.')
    $r.Add('- 7d64b18: 64_14 + 64_15 + 08_Окружение.md.')
    $r.Add('- (74_10) — коммит отчёта/старта/памятки/теста — см. 74_10c.')
    $r.Add('')
    $r.Add('## Долги 74 -> 75')
    $r.Add('1. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.')
    $r.Add('2. Бэкапы *.ds*bak* — вне git (.gitignore), не коммитить.')
    $r.Add('3. Интерактивная вставка — 64_14/64_15 действуют; класс инцидентов закрыт.')
    $r.Add('4. BOM при правке существующих .py/.ps1 — 65_3; тест test_ds74_01_gui_checklist.py — BOM=True (= test_ds183).')
    $r.Add('5. Тест 02_k1_ika_has_plp SKIPPED — ИКА пуст; при желании создать F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\*.plp (вне теста).')
    $r.Add('')
    $r.Add('## Артефакты')
    $r.Add('- Тест: SRC/tests/test_ds74_01_gui_checklist.py (12 passed / 1 skipped).')
    $r.Add('- Логи: LG_74_00_regress.log … LG_74_10a_rep.log.')
    $encR = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($rep74, $r, $encR)
    Write-Host '74.Отчёт.txt записан:' $r.Count 'строк'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
