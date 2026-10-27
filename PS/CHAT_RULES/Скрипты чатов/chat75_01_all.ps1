Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$gitignore = Join-Path $root '.gitignore'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_75_01_clean.log')
$msgFile = Join-Path $PSDir ($hostTag + '_75_01_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $gitignore)) { throw 'Нет .gitignore: ' + $gitignore }
    & git -C $root rev-parse --show-toplevel 2>&1 | Out-String | Write-Host
    $gb = [System.IO.File]::ReadAllBytes($gitignore)
    $gBomBefore = ($gb.Length -ge 3 -and $gb[0] -eq 0xEF -and $gb[1] -eq 0xBB -and $gb[2] -eq 0xBF)
    Copy-Item $gitignore ($gitignore + '.ds75_01bak') -Force
    $gt = [System.IO.File]::ReadAllText($gitignore, [System.Text.Encoding]::UTF8)
    if ($gt -notmatch '(?m)^__pycache__/' -or $gt -notmatch '(?m)^\*\.pyc' -or $gt -notmatch '(?m)^\*\.bad_' -or $gt -notmatch '(?m)^\*\.bak' -or $gt -notmatch 'chat67_03b_results/' -or $gt -notmatch 'chat67_03c_results/' -or $gt -notmatch '_w\.py' -or $gt -notmatch 'analysis_results\.json') {
        $add = "`r`n# 75_01: не коммитить артефакты`r`n__pycache__/`r`n*.pyc`r`n*.bad_*`r`n*.bak`r`nPS/CHAT_RULES/Скрипты чатов/_w.py`r`nPS/CHAT_RULES/Скрипты чатов/analysis_results.json`r`nPS/CHAT_RULES/Скрипты чатов/chat67_03b_results/`r`nPS/CHAT_RULES/Скрипты чатов/chat67_03c_results/`r`n"
        $gt = $gt.TrimEnd() + $add
        $encG = if ($gBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($gitignore, $gt, $encG)
        Write-Host '75_01: .gitignore дополнен'
    } else { Write-Host '75_01: .gitignore уже содержит блок' }
    $gb2 = [System.IO.File]::ReadAllBytes($gitignore)
    $gBomAfter = ($gb2.Length -ge 3 -and $gb2[0] -eq 0xEF -and $gb2[1] -eq 0xBB -and $gb2[2] -eq 0xBF)
    if ($gBomBefore -ne $gBomAfter) { throw 'BOM .gitignore не совпал (65_3)' }
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root rm --cached -r --ignore-unmatch -- 'PS/CHAT_RULES/Скрипты чатов/__pycache__' 2>&1 | Out-String | Write-Host
        & git -C $root rm --cached -r --ignore-unmatch -- 'PS/CHAT_RULES/Скрипты чатов/chat67_03b_results' 2>&1 | Out-String | Write-Host
        & git -C $root rm --cached -r --ignore-unmatch -- 'PS/CHAT_RULES/Скрипты чатов/chat67_03c_results' 2>&1 | Out-String | Write-Host
        & git -C $root rm --cached --ignore-unmatch -- 'PS/CHAT_RULES/Отчеты/49.Отчёт.txt.chat59.bak' 2>&1 | Out-String | Write-Host
        & git -C $root rm --cached --ignore-unmatch -- 'PS/CHAT_RULES/Скрипты чатов/analysis_results.json' 2>&1 | Out-String | Write-Host
        & git -C $root rm --cached --ignore-unmatch -- 'PS/CHAT_RULES/Скрипты чатов/_w.py' 2>&1 | Out-String | Write-Host
        & git -C $root ls-files -- 'PS/CHAT_RULES/Скрипты чатов/backup_68' 2>&1 | ForEach-Object { if ($_ -match '\.bad_') { & git -C $root rm --cached --ignore-unmatch -- $_ 2>&1 | Out-String | Write-Host } }
        Write-Host '--- git status --porcelain (для контроля) ---'
        & git -C $root status --porcelain 2>&1 | Out-String | Write-Host
        $msgLines = New-Object System.Collections.Generic.List[string]
        $msgLines.Add('75_01: чистка артефактов из git')
        $msgLines.Add('')
        $msgLines.Add('- .gitignore: __pycache__/, *.pyc, *.bad_*, *.bak, chat67_03b_results/, chat67_03c_results/, _w.py, analysis_results.json.')
        $msgLines.Add('- git rm --cached для уже закоммиченных артефактов (b27f0c1): файлы остаются на диске, но вне git.')
        $msgLines.Add('- Оставляем в git: chatNN_*.ps1, Отчеты/*.txt, Старт новых чатов/*.txt, 01_08/00_INDEX.md, 03..06_Регламент_*.md, Modelfile_llama_4k.txt, 63_1_ru.txt.')
        $encMsg = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
        $mb = [System.IO.File]::ReadAllBytes($msgFile)
        if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
        Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
        & git -C $root add -- .gitignore 2>&1 | Out-String | Write-Host
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
    Write-Host 'Готово: 75_01 закоммичен и запушен'
} catch {
    Write-Host 'ERROR:' $_ -ForegroundColor Red
    if (Test-Path ($gitignore + '.ds75_01bak')) { Copy-Item ($gitignore + '.ds75_01bak') $gitignore -Force; Write-Host 'ОТКАТ: .gitignore восстановлен' }
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
