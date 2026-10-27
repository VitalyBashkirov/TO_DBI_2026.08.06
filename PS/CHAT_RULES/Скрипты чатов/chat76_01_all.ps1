Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$IKA   = 'F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3'
$relSelf = 'PS/CHAT_RULES/Скрипты чатов/chat76_01_all.ps1'
$relIKA  = 'PATCH_IN/patch_suboptimal_test_3'
$repo  = Join-Path $root 'SRC'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_76_01_ika.log')
$outF = Join-Path $PSDir ($hostTag + '_76_01_full_out.txt')
$msgFile = Join-Path $PSDir ($hostTag + '_76_01_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $IKA)) { throw 'Нет ИКА: ' + $IKA }
    $encPlp = New-Object System.Text.UTF8Encoding($false)
    $f1 = Join-Path $IKA 'sample_bad_prefix.plp'
    $l1 = New-Object System.Collections.Generic.List[string]
    $l1.Add('-- sample_bad_prefix.plp')
    $l1.Add('procedure sample_bad_prefix is')
    $l1.Add('begin')
    $l1.Add('    vStr varchar2(10);')
    $l1.Add('end;')
    if ([string]::IsNullOrWhiteSpace($f1)) { throw 'f1 пуст (Join-Path не сработал)' }
    [System.IO.File]::WriteAllLines($f1, $l1, $encPlp)
    $f2 = Join-Path $IKA 'sample_not_mentioned.plp'
    $l2 = New-Object System.Collections.Generic.List[string]
    $l2.Add('-- sample_not_mentioned.plp')
    $l2.Add('procedure unknown_proc_xyz is')
    $l2.Add('begin')
    $l2.Add('    null;')
    $l2.Add('end;')
    if ([string]::IsNullOrWhiteSpace($f2)) { throw 'f2 пуст (Join-Path не сработал)' }
    [System.IO.File]::WriteAllLines($f2, $l2, $encPlp)
    $f3 = Join-Path $IKA 'sample_code_in_comment.plp'
    $l3 = New-Object System.Collections.Generic.List[string]
    $l3.Add('-- sample_code_in_comment.plp')
    $l3.Add('procedure sample_code_in_comment is')
    $l3.Add('begin')
    $l3.Add('    null; -- v_x := 1;')
    $l3.Add('end;')
    if ([string]::IsNullOrWhiteSpace($f3)) { throw 'f3 пуст (Join-Path не сработал)' }
    [System.IO.File]::WriteAllLines($f3, $l3, $encPlp)
    Write-Host 'ИКА: созданы 3 .plp:' $f1 $f2 $f3
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('76_01: ИКА — 3 .plp-фикстуры + самокоммит B')
    $msgLines.Add('')
    $msgLines.Add('- PATCH_IN/patch_suboptimal_test_3: sample_bad_prefix.plp, sample_not_mentioned.plp, sample_code_in_comment.plp.')
    $msgLines.Add('- Тест 02_k1_ika_has_plp: skip -> passed; полный регресс -> 402/0.')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- $relIKA $relSelf 2>&1 | Out-String | Write-Host
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
    $pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyCmd) { $python = $pyCmd.Source } else { $python = 'C:\Users\ainf1\AppData\Local\Programs\Python\Python312\python.exe' }
    Write-Host 'python=' $python
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $python -m pytest (Join-Path $repo 'tests') -q 2>&1 | Out-File -FilePath $outF -Encoding utf8
        $rcF = $LASTEXITCODE
    } finally { $ErrorActionPreference = $oldEAP }
    Get-Content $outF | Out-String | Write-Host
    Write-Host 'FULL_RC=' $rcF
    Write-Host 'Готово: 76_01 закоммичен, регресс выполнен (самокоммит B)'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
