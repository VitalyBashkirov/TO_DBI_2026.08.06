Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$repo  = Join-Path $root 'SRC'
$testFile = Join-Path $repo 'tests\test_ds74_01_gui_checklist.py'
$relSelf = 'PS/CHAT_RULES/Скрипты чатов/chat76_01f_all.ps1'
$relTest = 'SRC/tests/test_ds74_01_gui_checklist.py'
$relGitignore = '.gitignore'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_76_01f_fix02.log')
$outF = Join-Path $PSDir ($hostTag + '_76_01f_full_out.txt')
$msgFile = Join-Path $PSDir ($hostTag + '_76_01f_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $testFile)) { throw 'Нет теста: ' + $testFile }
    $b0 = [System.IO.File]::ReadAllBytes($testFile)
    if ($b0.Length -lt 1) { throw 'Тест пуст: ' + $testFile }
    $bomBefore = ($b0.Length -ge 3 -and $b0[0] -eq 0xEF -and $b0[1] -eq 0xBB -and $b0[2] -eq 0xBF)
    Write-Host 'test BOM before=' $bomBefore 'len=' $b0.Length
    $lines = [System.IO.File]::ReadAllLines($testFile, [System.Text.Encoding]::UTF8)
    $defIdx = -1
    for ($i = 0; $i -lt $lines.Length; $i++) { if ($lines[$i] -match '^\s*def test_74_01_02_k1_ika_has_plp\s*\(') { $defIdx = $i; break } }
    if ($defIdx -lt 0) { throw 'Не найдена def test_74_01_02_k1_ika_has_plp' }
    Write-Host 'defIdx=' $defIdx
    $endIdx = $lines.Length
    for ($j = $defIdx + 1; $j -lt $lines.Length; $j++) { if ($lines[$j] -match '^\S' -or $lines[$j] -match '^\s*#\s') { $endIdx = $j; break } }
    Write-Host 'endIdx=' $endIdx
    $hitIdx = -1
    for ($k = $defIdx + 1; $k -lt $endIdx; $k++) { $trim = $lines[$k].TrimStart(); if ($trim.StartsWith('import scanner')) { $hitIdx = $k; break } }
    if ($hitIdx -lt 0) {
        for ($k = $defIdx; $k -lt [Math]::Min($defIdx + 8, $lines.Length); $k++) { Write-Host ('DBG {0}: [{1}]' -f ($k + 1), $lines[$k]) }
        throw 'В теле test_74_01_02 не найден import scanner' 
    }
    Write-Host 'hitIdx=' $hitIdx 'line=' ($lines[$hitIdx])
    $lead = $lines[$hitIdx].Substring(0, $lines[$hitIdx].Length - $lines[$hitIdx].TrimStart().Length)
    $lines[$hitIdx] = $lead + 'from analyzer import scanner'
    $bak = $testFile + '.ds76bak_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
    Copy-Item $testFile $bak -Force
    $enc = New-Object System.Text.UTF8Encoding($bomBefore)
    [System.IO.File]::WriteAllLines($testFile, $lines, $enc)
    $b1 = [System.IO.File]::ReadAllBytes($testFile)
    $bomAfter = ($b1.Length -ge 3 -and $b1[0] -eq 0xEF -and $b1[1] -eq 0xBB -and $b1[2] -eq 0xBF)
    Write-Host 'test BOM after=' $bomAfter 'len=' $b1.Length
    if ($bomBefore -ne $bomAfter) { throw 'BOM изменился' }
    Write-Host 'тест: строка ' ($hitIdx + 1) ' -> from analyzer import scanner'
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('76_01f: fix test 02 (from analyzer import scanner) + .gitignore PATCH_IN/*')
    $msgLines.Add('')
    $msgLines.Add('- SRC/tests/test_ds74_01_gui_checklist.py: import scanner to from analyzer import scanner.')
    $msgLines.Add('- .gitignore: PATCH_IN/ -> PATCH_IN/* and exceptions.')
    $msgLines.Add('- Expected: 402 passed / 0 skipped.')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $ErrorActionPreference = 'Continue'
    & git -C $root add -- $relGitignore $relTest $relSelf 2>&1 | Out-String | Write-Host
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
    if ($sb -match '\[ahead \d+\]') { throw 'ahead N' }
    & git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host
    $c01c = Join-Path $PSDir 'CHAT_RULES\Скрипты чатов\chat76_01c_all.ps1'
    if (Test-Path $c01c) { Remove-Item $c01c -Force; Write-Host 'removed 01c' } else { Write-Host '01c absent' }
    $ErrorActionPreference = $oldEAP
    $pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyCmd) { $python = $pyCmd.Source } else { $python = 'C:\Users\ainf1\AppData\Local\Programs\Python\Python312\python.exe' }
    Write-Host 'python=' $python
    $ErrorActionPreference = 'Continue'
    & $python -m pytest (Join-Path $repo 'tests') -q 2>&1 | Out-File -FilePath $outF -Encoding utf8
    $rcF = $LASTEXITCODE
    $ErrorActionPreference = $oldEAP
    Get-Content $outF | Out-String | Write-Host
    Write-Host 'FULL_RC=' $rcF
    Write-Host 'Done: 76_01f committed, regress done'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
