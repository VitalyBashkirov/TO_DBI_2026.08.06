Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$relRules = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/01_Правила_PS.md'
$relTempl = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/07_Шаблон_PS.md'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw "Неизвестный хост: $hostName" }
$log = Join-Path $PSDir "${hostTag}_74_08_commit64_12_13.log"
$msgFile = Join-Path $PSDir "${hostTag}_74_08_msg.txt"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag root=$root"
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path (Join-Path $root $relRules))) { throw "Нет файла: $relRules" }
    if (-not (Test-Path (Join-Path $root $relTempl))) { throw "Нет файла: $relTempl" }
    Write-Host "--- git status -sb (до) ---"
    & git -C $root status -sb 2>&1 | Out-String | Write-Host
    Write-Host "--- check-ignore без -v: наши .md (молчит = НЕ игнорируются) ---"
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $ci = & git -C $root check-ignore -- $relRules $relTempl 2>&1
        if ($ci) { throw "Наши .md всё ещё игнорируются: $ci" }
        Write-Host "OK: наши .md не игнорируются"
    } finally { $ErrorActionPreference = $oldEAP }
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('74: 64_12 без exit + 64_13 генерация PS-кодом')
    $msgLines.Add('')
    $msgLines.Add('- 01_Правила_PS.md: 64_12 — без exit $rc в конце .ps1; finally + LOG: (64_11).')
    $msgLines.Add('- 01_Правила_PS.md: 64_13 — единственный способ .ps1/.py — генерация PS-кодом (WriteAllLines), без VS Code/Блокнота.')
    $msgLines.Add('- 07_Шаблон_PS.md: блоки "Генерация .ps1 — только PS-кодом (64_13)" и "Финал без exit (64_12)".')
    $encNoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encNoBom)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    $msgBom = ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF)
    if ($msgBom) { throw "msgfile с BOM — 11" }
    Write-Host "msgfile: $msgFile ($($mb.Length) B, no-BOM OK)"
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- $relRules $relTempl 2>&1 | Out-String | Write-Host
        $addRc = $LASTEXITCODE
        Write-Host "git add rc=$addRc"
        if ($addRc -ne 0) { throw "git add rc=$addRc" }
        & git -C $root commit -F $msgFile 2>&1 | Out-String | Write-Host
        $commitRc = $LASTEXITCODE
        Write-Host "git commit rc=$commitRc"
        if ($commitRc -ne 0) { throw "git commit rc=$commitRc" }
        & git -C $root push origin feature/dockerization 2>&1 | Out-String | Write-Host
        $pushRc = $LASTEXITCODE
        Write-Host "git push rc=$pushRc"
        if ($pushRc -ne 0) { throw "git push rc=$pushRc" }
        $sb = & git -C $root status -sb 2>&1
        $sb | Out-String | Write-Host
        if ($sb -match '\[ahead \d+\]') { throw "После push осталось [ahead N]" }
        & git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host
    } finally { $ErrorActionPreference = $oldEAP }
    Write-Host "Готово: 64_12 + 64_13 закоммичены и запушены"
} catch { Write-Host "ERROR: $_" -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
