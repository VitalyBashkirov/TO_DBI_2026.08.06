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
$repo  = 'F:\TO_DBI\SRC'
$log   = Join-Path $PSDir "${hostTag}_73_02a_v3_recon.log"

Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName repo=$repo"

try {
    $scanner = Join-Path $repo 'analyzer\scanner.py'
    $test    = Join-Path $repo 'tests\test_ds71_not_mentioned_real.py'
    if (-not (Test-Path $scanner)) { throw "Нет scanner.py: $scanner" }
    if (-not (Test-Path $test))    { throw "Нет теста: $test" }
    $sl = [System.IO.File]::ReadAllLines($scanner, [System.Text.Encoding]::UTF8)
    $tl = [System.IO.File]::ReadAllLines($test,    [System.Text.Encoding]::UTF8)

    Write-Host "--- decl_re: все строки (±2) ---"
    for ($i = 0; $i -lt $sl.Length; $i++) {
        if ($sl[$i] -match 'decl_re') {
            $from = [Math]::Max(0, $i - 2); $to = [Math]::Min($sl.Length - 1, $i + 2)
            Write-Host ("--- line " + ($i+1) + " ---")
            for ($j = $from; $j -le $to; $j++) { Write-Host ((("{0,4}: " -f ($j+1)) + $sl[$j])) }
        }
    }

    Write-Host "--- _plp_iter_declarations: 925..975 ---"
    $from = 925; $to = [Math]::Min(975, $sl.Length - 1)
    for ($j = $from; $j -le $to; $j++) { Write-Host ((("{0,4}: " -f ($j+1)) + $sl[$j])) }

    Write-Host "--- TEST: 40..60 ---"
    $from = 40; $to = [Math]::Min(60, $tl.Length - 1)
    for ($j = $from; $j -le $to; $j++) { Write-Host ((("{0,4}: " -f ($j+1)) + $tl[$j])) }

    Write-Host "--- TEST: 1..20 (импорты/пути) ---"
    $from = 0; $to = [Math]::Min(20, $tl.Length - 1)
    for ($j = $from; $j -le $to; $j++) { Write-Host ((("{0,4}: " -f ($j+1)) + $tl[$j])) }

    Write-Host "OK: 73_02a_v3 recon завершён"
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
