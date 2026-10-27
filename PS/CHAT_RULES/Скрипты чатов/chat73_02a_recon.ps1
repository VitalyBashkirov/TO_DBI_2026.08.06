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
$root  = 'F:\TO_DBI'
$repo  = 'F:\TO_DBI\SRC'
$log   = Join-Path $PSDir "${hostTag}_73_02a_recon.log"

Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName root=$root repo=$repo"

try {
    $scanner = Join-Path $repo 'scanner.py'
    $test    = Join-Path $repo 'tests\test_ds71_not_mentioned_real.py'
    $fix     = Join-Path $repo 'tests\fixtures\ds71_in_type.plp'

    Write-Host "--- FILES ---"
    if (Test-Path $scanner) { Write-Host ("scanner.py: " + (Get-Item $scanner).Length + " B") } else { Write-Host "scanner.py: MISSING" }
    if (Test-Path $test)    { Write-Host ("test: " + (Get-Item $test).Length + " B") } else { Write-Host "test: MISSING" }
    if (Test-Path $fix)     { Write-Host ("fixture: " + (Get-Item $fix).Length + " B") } else { Write-Host "fixture: MISSING" }

    Write-Host "--- GIT ---"
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        & git -C $root status -sb 2>&1 | ForEach-Object { Write-Host $_ }
        & git -C $root log -1 --oneline 2>&1 | ForEach-Object { Write-Host $_ }
    } finally { $ErrorActionPreference = $oldEAP }

    if (Test-Path $scanner) {
        Write-Host "--- SCANNER: строки с type_str ---"
        $lines = [System.IO.File]::ReadAllLines($scanner, [System.Text.Encoding]::UTF8)
        Write-Host ("TOTAL_LINES: " + $lines.Length)
        for ($i = 0; $i -lt $lines.Length; $i++) {
            if ($lines[$i] -match 'type_str') {
                $from = [Math]::Max(0, $i - 2); $to = [Math]::Min($lines.Length - 1, $i + 2)
                Write-Host ("--- line " + ($i+1) + " ---")
                for ($j = $from; $j -le $to; $j++) { Write-Host ((("{0,4}: " -f ($j+1)) + $lines[$j])) }
            }
        }
        Write-Host "--- SCANNER: строки с \" in [\" ---"
        for ($i = 0; $i -lt $lines.Length; $i++) {
            if ($lines[$i] -match '\bin\s*\[|\bnot\s+in\s*\[|NAME.*\[TYPE\]') {
                Write-Host ((("{0,4}: " -f ($i+1)) + $lines[$i]))
            }
        }
        Write-Host "--- SCANNER: строки с NAME в контексте in ---"
        for ($i = 0; $i -lt $lines.Length; $i++) {
            if ($lines[$i] -match 'NAME' -and $lines[$i] -match '\bin\b') {
                Write-Host ((("{0,4}: " -f ($i+1)) + $lines[$i]))
            }
        }
    }

    if (Test-Path $test) {
        Write-Host "--- TEST: заголовок и кейсы in ---"
        $tl = [System.IO.File]::ReadAllLines($test, [System.Text.Encoding]::UTF8)
        Write-Host ("TEST_LINES: " + $tl.Length)
        for ($i = 0; $i -lt $tl.Length; $i++) {
            if ($tl[$i] -match '\bin\b|in_type|in\s*\[') {
                Write-Host ((("{0,4}: " -f ($i+1)) + $tl[$i]))
            }
        }
    }

    if (Test-Path $fix) {
        Write-Host "--- FIXTURE: ds71_in_type.plp ---"
        $fl = [System.IO.File]::ReadAllLines($fix, [System.Text.Encoding]::UTF8)
        Write-Host ("FIX_LINES: " + $fl.Length)
        for ($i = 0; $i -lt $fl.Length; $i++) { Write-Host ((("{0,4}: " -f ($i+1)) + $fl[$i])) }
    }

    Write-Host "OK: 73_02a recon завершён"
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
