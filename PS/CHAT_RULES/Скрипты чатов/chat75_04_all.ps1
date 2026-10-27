Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$start75 = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\75.Старт.txt'
$relStart = 'PS/CHAT_RULES/Старт новых чатов/75.Старт.txt'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_75_04_start.log')
$msgFile = Join-Path $PSDir ($hostTag + '_75_04_msg.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $start75)) { throw 'Нет файла: ' + $start75 }
    $sb = [System.IO.File]::ReadAllBytes($start75)
    $sBomBefore = ($sb.Length -ge 3 -and $sb[0] -eq 0xEF -and $sb[1] -eq 0xBB -and $sb[2] -eq 0xBF)
    Copy-Item $start75 ($start75 + '.ds75_04bak') -Force
    $st = [System.IO.File]::ReadAllText($start75, [System.Text.Encoding]::UTF8)
    $st = [regex]::Replace($st, 'HEAD = 7d64b18 \(до коммита 74_10c\)', 'HEAD = c023108')
    $st = [regex]::Replace($st, 'HEAD = 7d64b18', 'HEAD = c023108')
    $st = [regex]::Replace($st, 'Действуют: 64_11, 64_12, 64_13, 64_14, 64_15, ДВОБ\.', 'Действуют: 64_11, 64_12, 64_13, 64_14, 64_15, 64_16, ДВОБ.')
    if ($st -notmatch '(?m)^## Коммиты 74/75') {
        $c = "`r`n## Коммиты 74/75`r`n"
        $c += "- f5b79e2 — CHAT_RULES в git + 64_11 + ДВОБ`r`n"
        $c += "- dc37ca2 — 64_12 без exit + 64_13 генерация PS-кодом`r`n"
        $c += "- eb5fc8a — .gitignore *.ds*bak / *.ds*_prev / *.bak_*`r`n"
        $c += "- 7d64b18 — 64_14 + 64_15 + 08_Окружение.md`r`n"
        $c += "- bd3cdaf — 74_10: отчёт/старт/памятка + тест + .gitignore (*.ds*bak*)`r`n"
        $c += "- b27f0c1 — 75_00: история CHAT_RULES в git`r`n"
        $c += "- cd1c134 — 75_01: чистка артефактов из git`r`n"
        $c += "- bcb815c — 75_02: .gitignore — долг 1`r`n"
        $c += "- c023108 — 75_03: скрипты чата 75`r`n"
        $c += "- <newhash> — 75_04: 75.Старт.txt — актуальный HEAD`r`n"
        $st = $st.TrimEnd() + $c
    }
    $encS = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($start75, $st, $encS)
    $sb2 = [System.IO.File]::ReadAllBytes($start75)
    $sBomAfter = ($sb2.Length -ge 3 -and $sb2[0] -eq 0xEF -and $sb2[1] -eq 0xBB -and $sb2[2] -eq 0xBF)
    if ($sBomBefore -ne $sBomAfter) { throw 'BOM 75.Старт.txt не совпал (65_3)' }
    if ($sb2.Length -ge 3 -and $sb2[0] -eq 0xEF -and $sb2[1] -eq 0xBB -and $sb2[2] -eq 0xBF) { throw '75.Старт.txt с BOM — 64_4' }
    $sf = [System.IO.File]::ReadAllText($start75, [System.Text.Encoding]::UTF8)
    if ($sf -notmatch 'HEAD = c023108') { throw 'HEAD не заменён' }
    if ($sf -notmatch '64_16') { throw '64_16 не добавлен' }
    if ($sf -notmatch '(?m)^## Коммиты 74/75') { throw 'раздел Коммиты 74/75 не добавлен' }
    Write-Host '75.Старт.txt обновлён:' $sb2.Length 'B, no-BOM, HEAD=c023108, 64_16, коммиты'
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('75_04: 75.Старт.txt — актуальный HEAD')
    $msgLines.Add('')
    $msgLines.Add('- HEAD = c023108 (вместо 7d64b18).')
    $msgLines.Add('- Действуют 64_11..64_16, ДВОБ.')
    $msgLines.Add('- Раздел Коммиты 74/75: f5b79e2..c023108 + <newhash>.')
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- $relStart 2>&1 | Out-String | Write-Host
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
        $st2 = & git -C $root status -sb 2>&1
        $st2 | Out-String | Write-Host
        if ($st2 -match '\[ahead \d+\]') { throw 'После push осталось [ahead N]' }
        & git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host
    } finally { $ErrorActionPreference = $oldEAP }
    Write-Host 'Готово: 75_04 закоммичен и запушен'
} catch {
    Write-Host 'ERROR:' $_ -ForegroundColor Red
    if (Test-Path ($start75 + '.ds75_04bak')) { Copy-Item ($start75 + '.ds75_04bak') $start75 -Force; Write-Host 'ОТКАТ: 75.Старт.txt восстановлен' }
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
