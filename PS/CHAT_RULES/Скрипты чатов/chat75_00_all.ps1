Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$relO = 'PS/CHAT_RULES/Отчеты'
$relS = 'PS/CHAT_RULES/Старт новых чатов'
$relC = 'PS/CHAT_RULES/Скрипты чатов'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_75_00_history.log')
$msgFile = Join-Path $PSDir ($hostTag + '_75_00_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    foreach ($p in @($relO, $relS, $relC)) { if (-not (Test-Path (Join-Path $root $p))) { throw 'Нет каталога: ' + $p } }
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('75_00: история CHAT_RULES в git')
    $msgLines.Add('')
    $msgLines.Add('- PS/CHAT_RULES/Отчеты: 49..74.Отчёт.txt, Памятка_чатов.txt.')
    $msgLines.Add('- PS/CHAT_RULES/Старт новых чатов: 21..75.Старт.txt, 01_08/00_INDEX.md, 03..06_Регламент_*.md.')
    $msgLines.Add('- PS/CHAT_RULES/Скрипты чатов: chatNN_*.ps1.')
    $msgLines.Add('- Не коммитим: *.lnk, free_memory.*, EXCHANGE/*, *.bat, test_all_models.ps1, SRC/settings.json, *.ds*bak*.')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM — 11' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- $relO $relS $relC 2>&1 | Out-String | Write-Host
        $addRc = $LASTEXITCODE
        Write-Host 'git add rc=' $addRc
        if ($addRc -ne 0) { throw 'git add rc=' + $addRc }
        & git -C $root reset -- 'PS/CHAT_RULES/Старт новых чатов.lnk' 2>&1 | Out-String | Write-Host
        & git -C $root reset -- 'free_memory.ps1' 'free_memory_profiles.txt' 2>&1 | Out-String | Write-Host
        Write-Host '--- git status --porcelain -- PS/CHAT_RULES (для контроля) ---'
        & git -C $root status --porcelain -- $relO $relS $relC 2>&1 | Out-String | Write-Host
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
    Write-Host 'Готово: 75_00 закоммичен и запушен'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
