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
$log = Join-Path $PSDir "LG_66_13_final_fix.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

$testScript = 'F:\TO_DBI\test_all_models.ps1'
$orchScript = Join-Path $PSDir 'CHAT_RULES\Скрипты чатов\chat66_orchestrator.ps1'

# === 1. Восстановление test_all_models.ps1 из бэкапа (с ollama stop, без фильтра) ===
$testBak = "$testScript.ds66bak2"
if (-not (Test-Path $testBak)) { throw "Нет бэкапа test_all_models.ps1: $testBak" }
Copy-Item $testBak $testScript -Force
Write-Host "test_all_models.ps1 восстановлен из бэкапа $testBak"

# === 2. Патч оркестратора ===
$orchBak = "$orchScript.ds66bak_final"
Copy-Item $orchScript $orchBak -Force
Write-Host "BAK: $orchBak"

$txt = [System.IO.File]::ReadAllText($orchScript, [System.Text.Encoding]::UTF8)

# Заменяем цикл foreach на прямой вызов с таймаутом 10800 (3 часа)
$pattern = '(?s)foreach\s*\(\$model in \$OllamaModels\)\s*\{.*?\n\}'
$replacement = @'
Write-Host ""
Write-Host "--- Ollama: Запуск всех моделей за один раз (таймаут 3 часа) ---" -ForegroundColor Yellow
$rc = Run-TestScriptWithTimeout -Backend 'ollama' -TimeoutSec 10800
Write-Host "proc rc=$rc"
if ($rc -eq 0) { $ollamaResults++ }
Stop-AllOllama
Write-Host "Все Ollama-модели выгружены"
@'

if ($txt -match $pattern) {
  $txt = [regex]::Replace($txt, $pattern, $replacement, 1)
  Write-Host "PATCH: Цикл Ollama заменен на одиночный вызов с таймаутом 3 часа"
} else {
  throw "ОШИБКА: Не найден цикл foreach ($model in $OllamaModels)"
}

[System.IO.File]::WriteAllText($orchScript, $txt, (New-Object System.Text.UTF8Encoding($true)))

# === 3. Проверка синтаксиса ===
$err = $null
[System.Management.Automation.Language.Parser]::ParseFile($orchScript, [ref]$null, [ref]$err) | Out-Null
if ($err.Count -gt 0) {
  Write-Host "СИНТАКСИЧЕСКАЯ ОШИБКА В ОРКЕСТРАТОРЕ:" -ForegroundColor Red
  $err | ForEach-Object { Write-Host $_.Message }
  throw "Скрипт содержит ошибки!"
} else {
  Write-Host "Синтаксис chat66_orchestrator.ps1 в порядке." -ForegroundColor Green
}

Write-Host "=== КОРРЕКТИРОВКА ЗАВЕРШЕНА ===" -ForegroundColor Green
Write-Host "Теперь можно запускать: & powershell -NoProfile -ExecutionPolicy Bypass -File $orchScript"

Stop-Transcript
Write-Host "LOG: $log" -ForegroundColor Green
