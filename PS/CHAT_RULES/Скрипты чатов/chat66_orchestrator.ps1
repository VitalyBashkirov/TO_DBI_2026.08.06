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
$log = Join-Path $PSDir "LG_66_06_orchestrator_v3.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

$TestScript = 'F:\TO_DBI\test_all_models.ps1'
$Lms7B = 'models/local-bank/deepseek-r1-distill-qwen-7b-q4_k_m.gguf'
$LmsModels = @(
  'models/local-bank/deepseek-r1-distill-qwen-7b-q4_k_m.gguf',
  'models/local-bank/meta-llama-3.1-8b-instruct-q4_k_m.gguf',
  'models/local-bank/gemma-3-it-4b-q4_k_m.gguf',
  'local-bank@q3_k_m',
  'models/local-bank/llama-3.2-1b-instruct-q4_k_m.gguf'
)
$OllamaModels = @('qwen2.5-coder:3b','qwen2.5-coder:7b','gemma3:1b','gemma3:4b','qwen3:8b','deepseek-r1:8b')
$OllamaSkip = 'gpt-oss:20b'

function Get-FreeRAM_MB {
  $os = Get-CimInstance Win32_OperatingSystem
  return [math]::Round($os.FreePhysicalMemory / 1024, 0)
}

function Wait-LmsServerReady {
  param([int]$TimeoutSec = 20)
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try {
      $r = Invoke-RestMethod -Uri "http://localhost:1234/v1/models" -Method Get -TimeoutSec 2
      if ($null -ne $r) { return $true }
    } catch { }
    Start-Sleep -Seconds 1
  }
  return $false
}

function Get-LmsEstimateGB {
  param([string]$Model)
  $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try {
    $out = & lms load --estimate-only $Model --gpu=max --context-length=4096 2>&1 | Out-String
    $m = [regex]::Match($out, 'Estimated Total Memory:\s*([\d.]+)\s*GB')
    if ($m.Success) { return [double]$m.Groups[1].Value }
    $out2 = & lms load --estimate-only $Model 2>&1 | Out-String
    $m2 = [regex]::Match($out2, 'Estimated Total Memory:\s*([\d.]+)\s*GB')
    if ($m2.Success) { return [double]$m2.Groups[1].Value }
    return -1
  } finally { $ErrorActionPreference = $oldEAP }
}

function Stop-AllOllama {
  $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try {
    $ps = & ollama ps 2>&1
    foreach ($line in $ps) {
      if ($line -match '^(\S+)\s+') {
        $n = $Matches[1]
        if ($n -and $n -ne 'NAME') { & ollama stop $n 2>&1 | Out-Null }
      }
    }
  } finally { $ErrorActionPreference = $oldEAP }
}

function Run-TestScriptWithTimeout {
  param([string]$Backend, [string]$ModelParam = "", [int]$TimeoutSec = 1800)
  $outFile = Join-Path $PSDir "test_${Backend}_out.txt"
  $errFile = Join-Path $PSDir "test_${Backend}_err.txt"
  $argList = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$TestScript,'-Backend',$Backend)
  if ($ModelParam) { $argList += @('-Model', $ModelParam) }
  $p = Start-Process -FilePath 'powershell.exe' -ArgumentList $argList -NoNewWindow -PassThru `
                     -RedirectStandardOutput $outFile -RedirectStandardError $errFile
  $finished = $p.WaitForExit($TimeoutSec * 1000)
  if (-not $finished) {
    Write-Host "PROC_TIMEOUT: $Backend ($TimeoutSec s) -> Stop-Process" -ForegroundColor Red
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    return 1
  }
  $rc = $p.ExitCode
  Write-Host "--- STDOUT ($Backend) ---"
  if (Test-Path $outFile) { Get-Content $outFile -Raw | Write-Host }
  Write-Host "--- STDERR ($Backend) ---"
  if (Test-Path $errFile) { Get-Content $errFile -Raw | Write-Host }
  Write-Host "rc=$rc"
  Remove-Item $outFile, $errFile -Force -ErrorAction SilentlyContinue
  return $rc
}

# === 0. СНИМОК ===
Write-Host ""
Write-Host "=== 0. СНИМОК ===" -ForegroundColor Cyan
$free = Get-FreeRAM_MB
Write-Host "FreeRAM=${free}MB"
$oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
try {
  Write-Host "--- ollama ps ---"; & ollama ps 2>&1 | Out-String | Write-Host
  Write-Host "--- lms ps ---"; & lms ps 2>&1 | Out-String | Write-Host
  Write-Host "--- lms server status ---"; & lms server status 2>&1 | Out-String | Write-Host
} finally { $ErrorActionPreference = $oldEAP }

# === 1. LMS-ПРОГОН ===
Write-Host ""
Write-Host "=== 1. LMS-ПРОГОН ===" -ForegroundColor Cyan
$lmsResults = 0
$lmsSkip = $false
$oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
try {
  $st = & lms server status 2>&1 | Out-String
  if ($st -notmatch 'running') {
    Write-Host "LMS server не запущен -> start"
    & lms server start 2>&1 | Out-Null
  }
  if (-not (Wait-LmsServerReady -TimeoutSec 20)) {
    Write-Host "LMS_SERVER_FAIL: порт 1234 не отвечает за 20s -> пропуск LMS-прогона" -ForegroundColor Red
    $lmsSkip = $true
  }
} finally { $ErrorActionPreference = $oldEAP }

if (-not $lmsSkip) {
  foreach ($model in $LmsModels) {
    Write-Host ""
    Write-Host "--- LMS model: $model ---" -ForegroundColor Yellow
    $free = Get-FreeRAM_MB
    $needGB = Get-LmsEstimateGB -Model $model
    if ($needGB -lt 0) { Write-Host "SKIP_OOM: estimate unparsed for $model"; continue }
    $needMB = $needGB * 1024
    Write-Host ("estimate: need={0}GB free={1}MB" -f $needGB, $free)
    if ($needMB -gt ($free - 1024)) { Write-Host "SKIP_OOM: $model (need ${needMB}MB > free-1GB)"; continue }

    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
      & lms load $model --gpu=max -y 2>&1 | Out-Null
      if ($LASTEXITCODE -ne 0) { Write-Host "LOAD_FAIL: $model"; continue }
      $rc = Run-TestScriptWithTimeout -Backend 'lms'
      Write-Host "test rc=$rc"
      if ($rc -eq 0) { $lmsResults++ }
      & lms unload --all 2>&1 | Out-Null
    } finally { $ErrorActionPreference = $oldEAP }
  }
  $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try { & lms server stop 2>&1 | Out-Null } finally { $ErrorActionPreference = $oldEAP }
}

# === 2. OLLAMA-ПРОГОН ===
Write-Host ""
Write-Host "=== 2. OLLAMA-ПРОГОН ===" -ForegroundColor Cyan
Stop-AllOllama
Write-Host "SKIP_OOM (pre): $OllamaSkip — 13GB > free ${free}MB"
$ollamaResults = 0
Write-Host ""
Write-Host "--- Ollama: Запуск всех моделей за один раз (таймаут 3 часа) ---" -ForegroundColor Yellow
$rc = Run-TestScriptWithTimeout -Backend 'ollama' -TimeoutSec 10800
Write-Host "proc rc=$rc"
if ($rc -eq 0) { $ollamaResults++ }
Stop-AllOllama
Write-Host "Все Ollama-модели выгружены"

# === 3. FALLBACK LMS ===
if ($lmsSkip -or $lmsResults -eq 0) {
  Write-Host ""
  Write-Host "=== 3. FALLBACK LMS (retry) ===" -ForegroundColor Yellow
  $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try {
    & lms server start 2>&1 | Out-Null
    if (Wait-LmsServerReady -TimeoutSec 20) {
      foreach ($model in $LmsModels) {
        $free = Get-FreeRAM_MB
        $needGB = Get-LmsEstimateGB -Model $model
        if ($needGB -lt 0) { continue }
        if (($needGB * 1024) -gt ($free - 1024)) { continue }
        & lms load $model --gpu=max -y 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
          $rc = Run-TestScriptWithTimeout -Backend 'lms'
          if ($rc -eq 0) { $lmsResults++ }
        }
        & lms unload --all 2>&1 | Out-Null
      }
    }
    & lms server stop 2>&1 | Out-Null
  } finally { $ErrorActionPreference = $oldEAP }
} else {
  Write-Host "LMS results=$lmsResults -> fallback не нужен"
}

# === 4. GPU-ТЕСТ ===
Write-Host ""
Write-Host "=== 4. GPU-ТЕСТ (7B, все 11) ===" -ForegroundColor Cyan
$gpuAvg = -1; $cpuAvg = -1
$oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
try {
  & lms server start 2>&1 | Out-Null
  if (Wait-LmsServerReady -TimeoutSec 20) {
    Write-Host "--- GPU=max ---"
    & lms load $Lms7B --gpu=max -y 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
      Run-TestScriptWithTimeout -Backend 'lms' | Out-Null
      $csv = Get-ChildItem 'F:\TO_DBI\temp\model_tests\test_*.csv' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
      if ($csv) {
        $rows = Import-Csv $csv.FullName
        $t = @($rows | Where-Object { $_.Success -eq 'True' } | ForEach-Object { [double]($_.Time -replace ',','.') })
        if ($t.Count -gt 0) { $gpuAvg = [math]::Round(($t | Measure-Object -Average).Average, 1) }
      }
    }
    & lms unload --all 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    Write-Host "--- GPU=off ---"
    & lms load $Lms7B --gpu=off -y 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
      Run-TestScriptWithTimeout -Backend 'lms' | Out-Null
      $csv2 = Get-ChildItem 'F:\TO_DBI\temp\model_tests\test_*.csv' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
      if ($csv2) {
        $rows2 = Import-Csv $csv2.FullName
        $t2 = @($rows2 | Where-Object { $_.Success -eq 'True' } | ForEach-Object { [double]($_.Time -replace ',','.') })
        if ($t2.Count -gt 0) { $cpuAvg = [math]::Round(($t2 | Measure-Object -Average).Average, 1) }
      }
    }
    & lms unload --all 2>&1 | Out-Null
  }
  & lms server stop 2>&1 | Out-Null
} finally { $ErrorActionPreference = $oldEAP }

$gpuVerdict = 'INCONCLUSIVE'
if ($gpuAvg -gt 0 -and $cpuAvg -gt 0) {
  if ($gpuAvg -lt ($cpuAvg * 0.8)) { $gpuVerdict = 'GPU_BETTER' }
  elseif ($cpuAvg -lt ($gpuAvg * 0.8)) { $gpuVerdict = 'CPU_BETTER' }
}

# === 5. ОТЧЁТ ===
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  ОРКЕСТРАТОР v3 ЗАВЕРШЁН" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "LMS results: $lmsResults (skip=$lmsSkip)"
Write-Host "Ollama results: $ollamaResults"
Write-Host "GPU test: GPU_avg=${gpuAvg}s CPU_avg=${cpuAvg}s -> $gpuVerdict"
Write-Host "SKIP_OOM: $OllamaSkip"
Write-Host "Log: $log"

Stop-Transcript
Get-ChildItem $PSDir -File |
    Where-Object {
        $_.Length -eq 0 -and
        $_.Name -ne (Split-Path $log -Leaf) -and
        $_.LastWriteTime -lt (Get-Date).AddMinutes(-1)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
& ollama run qwen2.5-coder:7b --keepalive 30m "test" 2>&1 | Out-Null
Write-Host "Оставлена qwen2.5-coder:7b в памяти (keepalive 30m)"
Write-Host "LOG: $log" -ForegroundColor Green
