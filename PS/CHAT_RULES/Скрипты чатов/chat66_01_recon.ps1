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
$log = Join-Path $PSDir "LG_66_01_recon_test_models.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

Write-Host ""
Write-Host "=== 1. Точечные места ==="
$points = @(
  'F:\TO_DBI\PS',
  'F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов',
  'F:\LMStudio_Models',
  'F:\TO_DBI'
)
foreach ($p in $points) {
  Write-Host ("POINT: {0} -> {1}" -f $p, (Test-Path $p))
}

Write-Host ""
Write-Host "=== 2. Поиск test_all_models.ps1 (точечно, без рекурса) ==="
$direct = @()
foreach ($p in $points) {
  if (Test-Path $p) {
    $direct += Get-ChildItem -Path $p -Filter 'test_all_models.ps1' -File -ErrorAction SilentlyContinue
  }
}
if ($direct.Count -gt 0) {
  foreach ($f in $direct) {
    Write-Host ("DIRECT: {0}  size={1}  mtime={2}" -f $f.FullName, $f.Length, $f.LastWriteTime)
  }
} else {
  Write-Host "DIRECT: not found in points"
}

Write-Host ""
Write-Host "=== 3. Рекурс по F:\TO_DBI (с таймаутом 60s) ==="
$job = Start-Job -ScriptBlock {
  Get-ChildItem -Path 'F:\TO_DBI' -Filter 'test_all_models.ps1' -File -Recurse -ErrorAction SilentlyContinue |
    Select-Object FullName, Length, LastWriteTime
}
$done = Wait-Job -Job $job -Timeout 60
if ($done) {
  $rec = Receive-Job -Job $job
  if ($rec -and $rec.Count -gt 0) {
    foreach ($r in $rec) {
      Write-Host ("RECURSE: {0}  size={1}  mtime={2}" -f $r.FullName, $r.Length, $r.LastWriteTime)
    }
  } else {
    Write-Host "RECURSE: not found in F:\TO_DBI"
  }
} else {
  Write-Host "RECURSE: TIMEOUT (>60s), job stopped"
  Stop-Job -Job $job -ErrorAction SilentlyContinue
}
Remove-Job -Job $job -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== 4. Снимок ДО: ollama list ==="
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
  & ollama list 2>&1 | Out-String | Write-Host
} finally { $ErrorActionPreference = $oldEAP }

Write-Host ""
Write-Host "=== 5. Снимок ДО: lms ls ==="
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
  & lms ls 2>&1 | Out-String | Write-Host
} finally { $ErrorActionPreference = $oldEAP }

Stop-Transcript
Get-ChildItem $PSDir -File |
    Where-Object {
        $_.Length -eq 0 -and
        $_.Name -ne (Split-Path $log -Leaf) -and
        $_.LastWriteTime -lt (Get-Date).AddMinutes(-1)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "LOG: $log" -ForegroundColor Green
