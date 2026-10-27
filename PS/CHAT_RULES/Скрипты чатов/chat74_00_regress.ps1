Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$PSDir = 'F:\TO_DBI\PS'
$repo  = 'F:\TO_DBI\SRC'
$root  = 'F:\TO_DBI'

$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }

$pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pyCmd) { $python = $pyCmd.Source }
else {
    $cands = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "C:\Users\ainf1\AppData\Local\Programs\Python\Python312\python.exe"
    )
    $python = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $python) { throw "python.exe не найден" }
}

$log = Join-Path $PSDir "${hostTag}_74_00_regress.log"
$out = Join-Path $PSDir "${hostTag}_74_00_pytest_out.txt"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName python=$python"
Write-Host "repo=$repo tests=$repo\tests"

$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & $python -m pytest (Join-Path $repo 'tests') -q -W error::pytest.PytestReturnNotNoneWarning 2>&1 | Out-File -FilePath $out -Encoding utf8
    $rc = $LASTEXITCODE
} finally { $ErrorActionPreference = $oldEAP }

Get-Content $out | Out-String | Write-Host
Write-Host "PYTEST_RC=$rc"

Stop-Transcript
Get-ChildItem $PSDir -File |
    Where-Object {
        $_.Length -eq 0 -and
        $_.Name -ne (Split-Path $log -Leaf) -and
        $_.LastWriteTime -lt (Get-Date).AddMinutes(-1)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "LOG: $log" -ForegroundColor Green
Write-Host "OUT: $out" -ForegroundColor Green
if ($rc -ne 0) { exit $rc }
