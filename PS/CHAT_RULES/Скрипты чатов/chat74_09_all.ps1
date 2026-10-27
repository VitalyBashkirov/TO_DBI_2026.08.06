Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$gitignore = Join-Path $root '.gitignore'
$relRules = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/01_Правила_PS.md'
$relTempl = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/07_Шаблон_PS.md'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw "Неизвестный хост: $hostName" }
$log = Join-Path $PSDir "${hostTag}_74_09_gitignore_dsbak.log"
$msgFile = Join-Path $PSDir "${hostTag}_74_09_msg.txt"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag root=$root"
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $gitignore)) { throw "Нет .gitignore: $gitignore" }
    if (-not (Test-Path (Join-Path $root $relRules))) { throw "Нет файла: $relRules" }
    if (-not (Test-Path (Join-Path $root $relTempl))) { throw "Нет файла: $relTempl" }
    $gb = [System.IO.File]::ReadAllBytes($gitignore)
    $gitBomBefore = ($gb.Length -ge 3 -and $gb[0] -eq 0xEF -and $gb[1] -eq 0xBB -and $gb[2] -eq 0xBF)
    Write-Host "BOM .gitignore до: $gitBomBefore"
    Copy-Item $gitignore ($gitignore + '.ds74_09bak') -Force
    Write-Host "Бэкап: $gitignore.ds74_09bak"
    $gt = [System.IO.File]::ReadAllText($gitignore, [System.Text.Encoding]::UTF8)
    if ($gt -notmatch '(?m)^\*\.ds\*bak') {
        $anchor = '(?m)^!PS/CHAT_RULES/\*\*\s*$'
        if (-not [regex]::IsMatch($gt, $anchor)) { throw "Не найден якорь !PS/CHAT_RULES/** в .gitignore" }
        $insert = "# DS: бэкапы и промежуточные (*.ds*bak, *.ds*_prev, *.bak_*)`r`n*.ds*bak`r`n*.ds*_prev`r`n*.bak_*"
        $gt2 = [regex]::Replace($gt, $anchor, "!PS/CHAT_RULES/**`r`n" + $insert, 1)
        $encG = if ($gitBomBefore) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
        [System.IO.File]::WriteAllText($gitignore, $gt2, $encG)
        Write-Host ".gitignore: блок *.ds*bak добавлен"
    } else { Write-Host ".gitignore: блок *.ds*bak уже есть" }
    $gb2 = [System.IO.File]::ReadAllBytes($gitignore)
    $gitBomAfter = ($gb2.Length -ge 3 -and $gb2[0] -eq 0xEF -and $gb2[1] -eq 0xBB -and $gb2[2] -eq 0xBF)
    Write-Host "BOM .gitignore после: $gitBomAfter"
    if ($gitBomBefore -ne $gitBomAfter) { throw "BOM .gitignore не совпал (65_3)" }
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        Write-Host "=== check-ignore -v: любой *.ds*bak (должен совпасть) ==="
        & git -C $root check-ignore -v -- 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/01_Правила_PS.md.ds74_07bak' 2>&1 | Out-String | Write-Host
        Write-Host "=== check-ignore без -v: наши .md (молчит = НЕ игнорируются) ==="
        $ci = & git -C $root check-ignore -- $relRules $relTempl 2>&1
        if ($ci) { throw "Наши .md всё ещё игнорируются: $ci" }
        Write-Host "OK: наши .md не игнорируются"
        Write-Host "=== git diff -- .gitignore ==="
        & git -C $root diff -- .gitignore 2>&1 | Out-String | Write-Host
    } finally { $ErrorActionPreference = $oldEAP }
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('74_09: .gitignore — *.ds*bak / *.ds*_prev / *.bak_*')
    $msgLines.Add('')
    $msgLines.Add('- Долг 2 (бэкапы *.ds*bak) закрыт: не коммитятся, не шумят в git status.')
    $msgLines.Add('- PS/*.log вне git (DS_129), CHAT_RULES в git — без изменений.')
    $encNoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encNoBom)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    $msgBom = ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF)
    if ($msgBom) { throw "msgfile с BOM — 11" }
    Write-Host "msgfile: $msgFile ($($mb.Length) B, no-BOM OK)"
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- .gitignore 2>&1 | Out-String | Write-Host
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
    Write-Host "Готово: 74_09 закоммичен и запушен"
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    if (Test-Path ($gitignore + '.ds74_09bak')) { Copy-Item ($gitignore + '.ds74_09bak') $gitignore -Force; Write-Host "ОТКАТ: .gitignore восстановлен" }
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
