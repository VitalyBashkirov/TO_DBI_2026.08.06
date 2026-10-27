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
$log   = Join-Path $PSDir "${hostTag}_73_02a_fix_recon.log"

Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName repo=$repo"

try {
    $scanner = Join-Path $repo 'analyzer\scanner.py'
    if (-not (Test-Path $scanner)) { throw "Нет scanner.py: $scanner" }
    Write-Host ("scanner.py: " + (Get-Item $scanner).Length + " B")
    $lines = [System.IO.File]::ReadAllLines($scanner, [System.Text.Encoding]::UTF8)
    Write-Host ("TOTAL_LINES: " + $lines.Length)

    Write-Host "--- TYPE_STR (±3) ---"
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match 'type_str') {
            $from = [Math]::Max(0, $i - 3); $to = [Math]::Min($lines.Length - 1, $i + 3)
            Write-Host ("--- line " + ($i+1) + " ---")
            for ($j = $from; $j -le $to; $j++) { Write-Host ((("{0,4}: " -f ($j+1)) + $lines[$j])) }
        }
    }

    Write-Host "--- IN [ (±2) ---"
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match '\bin\s*\[|\bnot\s+in\s*\[') {
            $from = [Math]::Max(0, $i - 2); $to = [Math]::Min($lines.Length - 1, $i + 2)
            Write-Host ("--- line " + ($i+1) + " ---")
            for ($j = $from; $j -le $to; $j++) { Write-Host ((("{0,4}: " -f ($j+1)) + $lines[$j])) }
        }
    }

    Write-Host "--- ITER_DECLARATIONS / NAME ---"
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match '_plp_iter_declarations|iter_declaration|NAME' ) {
            Write-Host ((("{0,4}: " -f ($i+1)) + $lines[$i]))
        }
    }

    Write-Host "OK: 73_02a_fix recon завершён"
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
