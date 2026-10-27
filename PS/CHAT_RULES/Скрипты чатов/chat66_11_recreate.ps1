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
$log = Join-Path $PSDir "LG_66_10_patch_v4.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

$orchScript = Join-Path $PSDir 'CHAT_RULES\Скрипты чатов\chat66_orchestrator.ps1'
$bak = "$orchScript.ds66bak3"
Copy-Item $orchScript $bak -Force
Write-Host "BAK: $bak"

$encBom = New-Object System.Text.UTF8Encoding($true)
$txt = [System.IO.File]::ReadAllText($orchScript, [System.Text.Encoding]::UTF8)

# === ПАТЧ 1: Сигнатура функции Run-TestScriptWithTimeout ===
$pattern1 = '(?s)function Run-TestScriptWithTimeout\s*\{\s*param\s*\([^\)]+\)'
$replacement1 = "function Run-TestScriptWithTimeout {`r`n  param([string]`$Backend, [string]`$ModelParam = `"`", [int]`$TimeoutSec = 1800)"
if ($txt -match $pattern1) {
  $txt = [regex]::Replace($txt, $pattern1, $replacement1, 1)
  Write-Host "PATCH1: сигнатура функции обновлена"
} else { throw "ОШИБКА: Не найдена функция Run-TestScriptWithTimeout" }

# === ПАТЧ 2: argList внутри функции ===
$pattern2 = '(?s)(\$argList = @\('-NoProfile',\s*'-ExecutionPolicy',\s*'Bypass',\s*'-File',\s*\$TestScript,\s*'-Backend',\s*\$Backend\))'
$replacement2 = '$1' + [Environment]::NewLine + '  if ($ModelParam) { $argList += @('-Model', $ModelParam) }'
if ($txt -match $pattern2) {
  $txt = [regex]::Replace($txt, $pattern2, $replacement2, 1)
  Write-Host "PATCH2: argList в функции обновлен"
} else { throw "ОШИБКА: Не найден массив argList в функции" }

# === ПАТЧ 3: Вызов внутри цикла ===
$pattern3 = '\$rc = Run-TestScriptWithTimeout -Backend ''ollama'' -TimeoutSec 1800'
$replacement3 = '$rc = Run-TestScriptWithTimeout -Backend ''ollama'' -ModelParam $model -TimeoutSec 1800'
if ($txt -match [regex]::Escape($pattern3)) {
  $txt = $txt.Replace($pattern3, $replacement3)
  Write-Host "PATCH3: вызов теста для одной модели обновлен"
} else { throw "ОШИБКА: Не найден вызов Run-TestScriptWithTimeout в цикле" }

[System.IO.File]::WriteAllText($orchScript, $txt, $encBom)
Write-Host "chat66_orchestrator.ps1 успешно пропатчен"

# === ПРОВЕРКА СИНТАКСИСА (защита от поломки) ===
$err = $null
[System.Management.Automation.Language.Parser]::ParseFile($orchScript, [ref]$null, [ref]$err) | Out-Null
if ($err.Count -gt 0) {
  Write-Host "СИНТАКСИЧЕСКАЯ ОШИБКА:" -ForegroundColor Red
  $err | ForEach-Object { Write-Host $_.Message }
  throw "Скрипт содержит ошибки после патча! Запуск отменен."
} else {
  Write-Host "Синтаксис chat66_orchestrator.ps1 в порядке." -ForegroundColor Green
}

# === ЗАПУСК ===
Write-Host ""
Write-Host "=== ЗАПУСК v4 (по одной модели) ===" -ForegroundColor Cyan
& powershell -NoProfile -ExecutionPolicy Bypass -File $orchScript

Stop-Transcript
Write-Host "LOG: $log" -ForegroundColor Green
