Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }
$PSDir = 'F:\TO_DBI\PS'
$pam   = Join-Path $PSDir 'CHAT_RULES\Отчеты\Памятка_чатов.txt'
$log   = Join-Path $PSDir "${hostTag}_73_04_pam74.log"

$encNoBom = New-Object System.Text.UTF8Encoding($false)
$nl = [Environment]::NewLine
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName pam=$pam"

try {
    if (-not (Test-Path $pam)) { throw "Нет Памятки: $pam" }
    $old = [System.IO.File]::ReadAllText($pam, [System.Text.Encoding]::UTF8)
    Write-Host "OLD_LEN: $($old.Length)"
    $has74 = $old -match "=== Чат 74"
    Write-Host ("HAS_74: " + $has74)
    if (-not $has74) {
        $bak = "$pam.ds73_04bak"
        if (-not (Test-Path $bak)) { Copy-Item -LiteralPath $pam -Destination $bak -Force }
        $B = New-Object System.Collections.Generic.List[string]
        $B.Add("")
        $B.Add("=== Чат 74 (2026-10-27, LG) — ОЖИДАЕТ ===")
        $B.Add("План: 74_00 (Памятка/старт) -> 74_01 (долг 3/4: дисциплина вставки / BOM-ловушки) -> 74_02 (новая задача).")
        $B.Add("Старт: F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\74.Старт.txt")
        $B.Add("Отчёт 73: F:\TO_DBI\PS\CHAT_RULES\Отчеты\73.Отчёт.txt")
        $add = ($B -join $nl)
        $new = $old.TrimEnd() + $nl + $add + $nl
        [System.IO.File]::WriteAllText($pam, $new, $encNoBom)
        Write-Host "WROTE Памятка: раздел 74 OK"
    } else { Write-Host "SKIP: раздел 74 уже есть" }
    $chk = [System.IO.File]::ReadAllText($pam, [System.Text.Encoding]::UTF8)
    Write-Host ("NEW_LEN: " + $chk.Length)
    if ($chk -notmatch '=== Чат 74') { throw 'Раздел 74 не записан' }
    $b = [System.IO.File]::ReadAllBytes($pam)
    $isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
    Write-Host ("PAM_BOM: " + $isBom + " (ожидается False)")
    if ($isBom) { throw "Памятка с BOM — 64_4" }
    $tail = ($chk -split "`r?`n" | Select-Object -Last 8) -join $nl
    Write-Host "--- TAIL ---"
    Write-Host $tail
    Write-Host "--- /TAIL ---"
    Write-Host "OK: 73_04 завершён"
}
catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    throw
}
finally {
    Stop-Transcript -ErrorAction SilentlyContinue
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
