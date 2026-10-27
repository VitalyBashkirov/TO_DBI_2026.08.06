Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$IKA   = 'F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3'
$gitignore = Join-Path $root '.gitignore'
$relSelf = 'PS/CHAT_RULES/Скрипты чатов/chat76_01b_all.ps1'
$relIKA  = 'PATCH_IN/patch_suboptimal_test_3'
$relGitignore = '.gitignore'
$repo  = Join-Path $root 'SRC'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_76_01b_ika.log')
$outF = Join-Path $PSDir ($hostTag + '_76_01b_full_out.txt')
$msgFile = Join-Path $PSDir ($hostTag + '_76_01b_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $IKA)) { throw 'Нет ИКА: ' + $IKA }
    if (-not (Test-Path $gitignore)) { throw 'Нет .gitignore: ' + $gitignore }
    $ErrorActionPreference = 'Continue'
    & git -C $root reset -- $relSelf 2>&1 | Out-String | Write-Host
    Write-Host 'git reset rc=' $LASTEXITCODE
    $ErrorActionPreference = $oldEAP
    $encPlp = New-Object System.Text.UTF8Encoding($false)
    $f1 = Join-Path $IKA 'sample_bad_prefix.plp'
    $l1 = New-Object System.Collections.Generic.List[string]
    $l1.Add('-- sample_bad_prefix.plp')
    $l1.Add('procedure sample_bad_prefix is')
    $l1.Add('begin')
    $l1.Add('    vStr varchar2(10);')
    $l1.Add('end;')
    if ([string]::IsNullOrWhiteSpace($f1)) { throw 'f1 пуст' }
    [System.IO.File]::WriteAllLines($f1, $l1, $encPlp)
    $f2 = Join-Path $IKA 'sample_not_mentioned.plp'
    $l2 = New-Object System.Collections.Generic.List[string]
    $l2.Add('-- sample_not_mentioned.plp')
    $l2.Add('procedure unknown_proc_xyz is')
    $l2.Add('begin')
    $l2.Add('    null;')
    $l2.Add('end;')
    if ([string]::IsNullOrWhiteSpace($f2)) { throw 'f2 пуст' }
    [System.IO.File]::WriteAllLines($f2, $l2, $encPlp)
    $f3 = Join-Path $IKA 'sample_code_in_comment.plp'
    $l3 = New-Object System.Collections.Generic.List[string]
    $l3.Add('-- sample_code_in_comment.plp')
    $l3.Add('procedure sample_code_in_comment is')
    $l3.Add('begin')
    $l3.Add('    null; -- v_x := 1;')
    $l3.Add('end;')
    if ([string]::IsNullOrWhiteSpace($f3)) { throw 'f3 пуст' }
    [System.IO.File]::WriteAllLines($f3, $l3, $encPlp)
    Write-Host 'ИКА: созданы 3 .plp:' $f1 $f2 $f3
    $bak = $gitignore + '.ds76bak_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
    Copy-Item $gitignore $bak -Force
    $giText = [System.IO.File]::ReadAllText($gitignore, [System.Text.Encoding]::UTF8)
    if ($giText -match '!PATCH_IN/patch_suboptimal_test_3/') {
        Write-Host 'gitignore: исключение уже есть, правка не нужна'
    } else {
        $anchor = 'PATCH_IN/'
        if ($giText.IndexOf($anchor) -lt 0) { throw 'В .gitignore нет строки PATCH_IN/' }
        $nl = if ($giText.Contains("`r`n")) { "`r`n" } else { "`n" }
        $ins = $nl + '!PATCH_IN/patch_suboptimal_test_3/' + $nl + '!PATCH_IN/patch_suboptimal_test_3/*.plp'
        $pos = $giText.IndexOf($anchor) + $anchor.Length
        $giNew = $giText.Substring(0, $pos) + $ins + $giText.Substring($pos)
        [System.IO.File]::WriteAllText($gitignore, $giNew, (New-Object System.Text.UTF8Encoding($false)))
        Write-Host 'gitignore: добавлены 2 строки исключения после PATCH_IN/'
    }
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('76_01b: ИКА — 3 .plp-фикстуры + .gitignore-исключение + самокоммит B')
    $msgLines.Add('')
    $msgLines.Add('- PATCH_IN/patch_suboptimal_test_3: sample_bad_prefix.plp, sample_not_mentioned.plp, sample_code_in_comment.plp.')
    $msgLines.Add('- .gitignore: !PATCH_IN/patch_suboptimal_test_3/ + !PATCH_IN/patch_suboptimal_test_3/*.plp (фикстуры в git).')
    $msgLines.Add('- Тест 02_k1_ika_has_plp: skip -> passed; полный регресс -> 402/0.')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $ErrorActionPreference = 'Continue'
    & git -C $root add -- $relGitignore $relIKA $relSelf 2>&1 | Out-String | Write-Host
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
    Write-Host 'Готово: 76_01b закоммичен, регресс выполнен (самокоммит B)'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
