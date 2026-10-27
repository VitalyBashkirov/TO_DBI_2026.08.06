Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$base  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п'
$envf  = Join-Path $base '08_Окружение.md'
$gitignore = Join-Path $root '.gitignore'
$relRep   = 'PS/CHAT_RULES/Отчеты/74.Отчёт.txt'
$relRep73 = 'PS/CHAT_RULES/Отчеты/73.Отчёт.txt'
$relPam   = 'PS/CHAT_RULES/Отчеты/Памятка_чатов.txt'
$relSt75  = 'PS/CHAT_RULES/Старт новых чатов/75.Старт.txt'
$relEnv   = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/08_Окружение.md'
$relTest  = 'SRC/tests/test_ds74_01_gui_checklist.py'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_74_10c_commit.log')
$msgFile = Join-Path $PSDir ($hostTag + '_74_10c_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $envf)) { throw 'Нет файла: ' + $envf }
    if (-not (Test-Path $gitignore)) { throw 'Нет файла: ' + $gitignore }
    $eb = [System.IO.File]::ReadAllBytes($envf)
    $eBomBefore = ($eb.Length -ge 3 -and $eb[0] -eq 0xEF -and $eb[1] -eq 0xBB -and $eb[2] -eq 0xBF)
    Copy-Item $envf ($envf + '.ds74_10cbak') -Force
    $et = [System.IO.File]::ReadAllText($envf, [System.Text.Encoding]::UTF8)
    if ($et -notmatch 'test_ds74_01_gui_checklist') {
        $et += "`r`n## Тест test_ds74_01_gui_checklist.py (чат 74)`r`n`r`n- 12 passed / 1 skipped (skip = 02_k1_ika_has_plp: ИКА пуст).`r`n- BOM=True (как у test_ds183_k4_model_setting.py); 65_3.`r`n"
        $encE = if ($eBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($envf, $et, $encE)
        Write-Host '08_Окружение.md: пометка о тесте добавлена'
    } else { Write-Host '08_Окружение.md: пометка о тесте уже есть' }
    $eb2 = [System.IO.File]::ReadAllBytes($envf)
    $eBomAfter = ($eb2.Length -ge 3 -and $eb2[0] -eq 0xEF -and $eb2[1] -eq 0xBB -and $eb2[2] -eq 0xBF)
    if ($eBomBefore -ne $eBomAfter) { throw 'BOM 08_Окружение.md не совпал (65_3)' }
    $gb = [System.IO.File]::ReadAllBytes($gitignore)
    $gBomBefore = ($gb.Length -ge 3 -and $gb[0] -eq 0xEF -and $gb[1] -eq 0xBB -and $gb[2] -eq 0xBF)
    Copy-Item $gitignore ($gitignore + '.ds74_10cbak') -Force
    $gt = [System.IO.File]::ReadAllText($gitignore, [System.Text.Encoding]::UTF8)
    if ($gt -notmatch '\*\.ds\*bak\*') {
        $gt2 = [regex]::Replace($gt, '(?m)^\*\.ds\*bak\s*$', '*.ds*bak*', 1)
        if ($gt2 -ne $gt) {
            $encG = if ($gBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
            [System.IO.File]::WriteAllText($gitignore, $gt2, $encG)
            Write-Host '.gitignore: *.ds*bak -> *.ds*bak*'
        } else { Write-Host 'WARN: .gitignore: строка *.ds*bak не найдена' }
    } else { Write-Host '.gitignore: *.ds*bak* уже есть' }
    $gb2 = [System.IO.File]::ReadAllBytes($gitignore)
    $gBomAfter = ($gb2.Length -ge 3 -and $gb2[0] -eq 0xEF -and $gb2[1] -eq 0xBB -and $gb2[2] -eq 0xBF)
    if ($gBomBefore -ne $gBomAfter) { throw 'BOM .gitignore не совпал (65_3)' }
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('74_10: отчёт/старт/памятка + тест + .gitignore (*.ds*bak*)')
    $msgLines.Add('')
    $msgLines.Add('- 74.Отчёт.txt: итоги 74_00..74_01d, коммиты, долги, артефакты.')
    $msgLines.Add('- 75.Старт.txt: правила в git, статус, первые шаги.')
    $msgLines.Add('- Памятка_чатов.txt: 74 ЗАКРЫТ, 75 В РАБОТЕ.')
    $msgLines.Add('- 73.Отчёт.txt: поправка формулировки (74_04).')
    $msgLines.Add('- 08_Окружение.md: пометка о тесте test_ds74_01_gui_checklist.py.')
    $msgLines.Add('- test_ds74_01_gui_checklist.py: 12 passed / 1 skipped.')
    $msgLines.Add('- .gitignore: *.ds*bak -> *.ds*bak* (ловит *.ds66bak2/5).')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM — 11' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- $relRep $relRep73 $relPam $relSt75 $relEnv $relTest $gitignore 2>&1 | Out-String | Write-Host
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
    Write-Host 'Готово: 74_10 закоммичен и запушен'
} catch {
    Write-Host 'ERROR:' $_ -ForegroundColor Red
    foreach ($p in @($envf, $gitignore)) { if (Test-Path ($p + '.ds74_10cbak')) { Copy-Item ($p + '.ds74_10cbak') $p -Force; Write-Host 'ОТКАТ: ' $p } }
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
