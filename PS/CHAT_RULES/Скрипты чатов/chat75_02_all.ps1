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
$log = Join-Path $PSDir ($hostTag + '_75_02_ignore.log')
$msgFile = Join-Path $PSDir ($hostTag + '_75_02_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $gitignore)) { throw 'Нет .gitignore: ' + $gitignore }
    $gb = [System.IO.File]::ReadAllBytes($gitignore)
    $gBomBefore = ($gb.Length -ge 3 -and $gb[0] -eq 0xEF -and $gb[1] -eq 0xBB -and $gb[2] -eq 0xBF)
    Copy-Item $gitignore ($gitignore + '.ds75_02bak') -Force
    $gt = [System.IO.File]::ReadAllText($gitignore, [System.Text.Encoding]::UTF8)
    if ($gt -notmatch '(?m)^EXCHANGE/' -or $gt -notmatch '(?m)^\*\.bat' -or $gt -notmatch '(?m)^\*\.lnk' -or $gt -notmatch 'SRC/settings\.json' -or $gt -notmatch 'test_all_models\.ps1' -or $gt -notmatch 'free_memory\.ps1' -or $gt -notmatch 'free_memory_profiles\.txt') {
        $add = "`r`n# 75_02: долг 1 — не коммитить`r`nEXCHANGE/`r`n*.bat`r`n*.lnk`r`nSRC/settings.json`r`ntest_all_models.ps1`r`nfree_memory.ps1`r`nfree_memory_profiles.txt`r`n"
        $gt = $gt.TrimEnd() + $add
        $encG = if ($gBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($gitignore, $gt, $encG)
        Write-Host '75_02: .gitignore дополнен (долг 1)'
    } else { Write-Host '75_02: .gitignore уже содержит блок' }
    $gb2 = [System.IO.File]::ReadAllBytes($gitignore)
    $gBomAfter = ($gb2.Length -ge 3 -and $gb2[0] -eq 0xEF -and $gb2[1] -eq 0xBB -and $gb2[2] -eq 0xBF)
    if ($gBomBefore -ne $gBomAfter) { throw 'BOM .gitignore не совпал (65_3)' }
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('75_02: .gitignore — долг 1 (EXCHANGE, *.bat, *.lnk, settings.json, test_all_models.ps1, free_memory.*)')
    $msgLines.Add('')
    $msgLines.Add('- EXCHANGE/ — фоновые (bot.log и т.п.).')
    $msgLines.Add('- *.bat — Ollama и LM Studio.bat и др.')
    $msgLines.Add('- *.lnk — ярлыки.')
    $msgLines.Add('- SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt — не коммитить.')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- .gitignore 2>&1 | Out-String | Write-Host
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
    Write-Host 'Готово: 75_02 закоммичен и запушен'
} catch {
    Write-Host 'ERROR:' $_ -ForegroundColor Red
    if (Test-Path ($gitignore + '.ds75_02bak')) { Copy-Item ($gitignore + '.ds75_02bak') $gitignore -Force; Write-Host 'ОТКАТ: .gitignore восстановлен' }
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
