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
$log = Join-Path $PSDir "LG_66_08_fix.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

$testScript = 'F:\TO_DBI\test_all_models.ps1'
$orchScript = Join-Path $PSDir 'CHAT_RULES\Скрипты чатов\chat66_orchestrator.ps1'

# === Бэкапы ===
foreach ($f in @($testScript, $orchScript)) {
  if (-not (Test-Path $f)) { throw "Нет файла: $f" }
  $bak = "$f.ds66bak2"
  Copy-Item $f $bak -Force
  Write-Host "BAK: $bak"
}

$encBom = New-Object System.Text.UTF8Encoding($true)

# === Патч 1: test_all_models.ps1 -> -Model и фильтр ===
$txt = [System.IO.File]::ReadAllText($testScript, [System.Text.Encoding]::UTF8)

# 1a. Добавить [string]$Model = "" в param
if ($txt -notmatch '\[string\]\$Model\s*=') {
  $paramAnchor = '[ValidateSet("all","ollama","lms")]'
  if (-not $txt.Contains($paramAnchor)) { throw "Не найден якорь param [ValidateSet]" }
  $paramInsert = '[string]$Model = "",' + [Environment]::NewLine + '    ' + $paramAnchor
  $txt = $txt.Replace($paramAnchor, $paramInsert)
  Write-Host "PATCH1a: -Model добавлен в param"
} else { Write-Host "PATCH1a: -Model уже есть" }

# 1b. Добавить фильтр после сбора моделей
if ($txt -notmatch 'if \(\$Model\) \{ \$allModels') {
  $filterAnchor = '$allModels = @(); $allModels += $ollamaModels; $allModels += $lmsModels'
  if (-not $txt.Contains($filterAnchor)) { throw "Не найден якорь сбора allModels" }
  $filterInsert = $filterAnchor + [Environment]::NewLine + 'if ($Model) { $allModels = @($allModels | Where-Object { $_.Name -eq $Model }) }'
  $txt = $txt.Replace($filterAnchor, $filterInsert)
  Write-Host "PATCH1b: фильтр по -Model добавлен"
} else { Write-Host "PATCH1b: фильтр уже есть" }

[System.IO.File]::WriteAllText($testScript, $txt, $encBom)
Write-Host "test_all_models.ps1 пропатчен"

# === Патч 2: orchestrator -> цикл с -Model ===
$txt2 = [System.IO.File]::ReadAllText($orchScript, [System.Text.Encoding]::UTF8)

# Заменяем блок "foreach ($model in $OllamaModels) { ... }"
$oldBlock = @"
foreach ($model in $OllamaModels) {
  Write-Host ""
  Write-Host "--- Ollama model: $model ---" -ForegroundColor Yellow
  $rc = Run-TestScriptWithTimeout -Backend 'ollama' -TimeoutSec 1800
  Write-Host "proc rc=$rc"
  if ($rc -eq 0) { $ollamaResults++ }
  $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try { & ollama stop $model 2>&1 | Out-Null } finally { $ErrorActionPreference = $oldEAP }
}
"@

$newBlock = @"
foreach ($model in $OllamaModels) {
  Write-Host ""
  Write-Host "--- Ollama model: $model ---" -ForegroundColor Yellow
  $rc = Run-TestScriptWithTimeout -Backend 'ollama' -ModelParam $model -TimeoutSec 1800
  Write-Host "proc rc=$rc"
  if ($rc -eq 0) { $ollamaResults++ }
  $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try { & ollama stop $model 2>&1 | Out-Null } finally { $ErrorActionPreference = $oldEAP }
}
"@

if ($txt2.Contains($oldBlock)) {
  $txt2 = $txt2.Replace($oldBlock, $newBlock)
  Write-Host "PATCH2: цикл обновлен на -ModelParam"
} else {
  $txt2 = [regex]::Replace($txt2, 'foreach \(\$model in \$OllamaModels\).*?\n\}', $newBlock, 'Singleline')
  Write-Host "PATCH2: цикл обновлен через regex"
}

# Патч Run-TestScriptWithTimeout
$oldFunc = @"
function Run-TestScriptWithTimeout {
  param([string]$Backend, [int]$TimeoutSec = 1800)
  $outFile = Join-Path $PSDir "test_${Backend}_out.txt"
  $errFile = Join-Path $PSDir "test_${Backend}_err.txt"
  $argList = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$TestScript,'-Backend',$Backend)
"@

$newFunc = @"
function Run-TestScriptWithTimeout {
  param([string]$Backend, [string]$ModelParam = "", [int]$TimeoutSec = 1800)
  $outFile = Join-Path $PSDir "test_${Backend}_out.txt"
  $errFile = Join-Path $PSDir "test_${Backend}_err.txt"
  $argList = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$TestScript,'-Backend',$Backend)
  if ($ModelParam) { $argList += @('-Model', $ModelParam) }
"@

if ($txt2.Contains($oldFunc)) {
  $txt2 = $txt2.Replace($oldFunc, $newFunc)
  Write-Host "PATCH2: функция Run-TestScriptWithTimeout обновлена"
} else {
  Write-Host "WARN: функция Run-TestScriptWithTimeout не найдена дословно"
}

[System.IO.File]::WriteAllText($orchScript, $txt2, $encBom)
Write-Host "chat66_orchestrator.ps1 пропатчен"

# === Запуск начисто ===
Write-Host ""
Write-Host "=== ЗАПУСК v4 (по одной модели) ===" -ForegroundColor Cyan
Write-Host ""

& powershell -NoProfile -ExecutionPolicy Bypass -File $orchScript

Stop-Transcript
Write-Host "LOG: $log" -ForegroundColor Green
