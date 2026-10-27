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
$log = Join-Path $PSDir "LG_66_07_patch.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

$testScript = 'F:\TO_DBI\test_all_models.ps1'
$orchScript = Join-Path $PSDir 'CHAT_RULES\Скрипты чатов\chat66_orchestrator.ps1'

# === Бэкапы (64_2) ===
foreach ($f in @($testScript, $orchScript)) {
  if (-not (Test-Path $f)) { throw "Нет файла: $f" }
  $fi = Get-Item $f
  if ($fi.Length -eq 0) { throw "Пустой файл: $f" }
  $bak = "$f.ds66bak"
  Copy-Item $f $bak -Force
  Write-Host "BAK: $bak ($($fi.Length) bytes)"
}

# === Патч 1: test_all_models.ps1 -> $RemovedModels + ollama stop ===
$encBom = New-Object System.Text.UTF8Encoding($true)
$txt = [System.IO.File]::ReadAllText($testScript, [System.Text.Encoding]::UTF8)

# 1a. добавить gpt-oss:20b в RemovedModels, если ещё нет
if ($txt -notmatch '"gpt-oss:20b"') {
  $pattern = '(\$RemovedModels\s*=\s*@\([^)]*?)'
  $replacement = '$1    "gpt-oss:20b"' + "`r`n"
  $txt2 = [regex]::Replace($txt, $pattern, $replacement, 'Singleline')
  if ($txt2 -eq $txt) { throw "Не удалось вставить gpt-oss:20b в RemovedModels" }
  $txt = $txt2
  Write-Host "PATCH1a: gpt-oss:20b добавлен в RemovedModels"
} else {
  Write-Host "PATCH1a: gpt-oss:20b уже в RemovedModels"
}

# 1b. добавить ollama stop после цикла по тестам
if ($txt -notmatch 'ollama stop \$model\.Name') {
  $anchor = '        Start-Sleep -Seconds 1' + "`r`n" + '    }'
  $insert = '        Start-Sleep -Seconds 1' + "`r`n" + '    }' + "`r`n" + '    if ($model.Backend -eq "Ollama") { & ollama stop $model.Name 2>&1 | Out-Null }'
  if ($txt -notmatch [regex]::Escape($anchor)) { throw "Не найден якорь Start-Sleep/} для вставки ollama stop" }
  $txt = $txt.Replace($anchor, $insert)
  Write-Host "PATCH1b: ollama stop после каждой модели добавлен"
} else {
  Write-Host "PATCH1b: ollama stop уже есть"
}

[System.IO.File]::WriteAllText($testScript, $txt, $encBom)
$b = [System.IO.File]::ReadAllBytes($testScript)
$isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
if (-not $isBom) { throw "BOM не записан в test_all_models.ps1 — 64_4" }
Write-Host "test_all_models.ps1: $($b.Length) bytes, BOM=$isBom"

# === Патч 2: orchestrator -> ollama run 7b в конце ===
$txt2 = [System.IO.File]::ReadAllText($orchScript, [System.Text.Encoding]::UTF8)
if ($txt2 -notmatch 'qwen2\.5-coder:7b --keepalive') {
  $anchor2 = 'Write-Host "LOG: $log" -ForegroundColor Green'
  $insert2 = '& ollama run qwen2.5-coder:7b --keepalive 30m "test" 2>&1 | Out-Null' + "`r`n" + 'Write-Host "Оставлена qwen2.5-coder:7b в памяти (keepalive 30m)"' + "`r`n" + $anchor2
  if ($txt2 -notmatch [regex]::Escape($anchor2)) { throw "Не найден якорь LOG для вставки ollama run" }
  $txt2 = $txt2.Replace($anchor2, $insert2)
  Write-Host "PATCH2: ollama run 7b в конце добавлен"
} else {
  Write-Host "PATCH2: ollama run 7b уже есть"
}
[System.IO.File]::WriteAllText($orchScript, $txt2, $encBom)
$b2 = [System.IO.File]::ReadAllBytes($orchScript)
$isBom2 = ($b2.Length -ge 3 -and $b2[0] -eq 0xEF -and $b2[1] -eq 0xBB -and $b2[2] -eq 0xBF)
if (-not $isBom2) { throw "BOM не записан в orchestrator — 64_4" }
Write-Host "chat66_orchestrator.ps1: $($b2.Length) bytes, BOM=$isBom2"

# === Проверка ===
Write-Host ""
Write-Host "=== Проверка test_all_models.ps1 ==="
Get-Content $testScript -Encoding UTF8 | Select-String 'gpt-oss:20b|ollama stop \$model' | Select-Object -First 5 | Out-String | Write-Host
Write-Host "=== Проверка orchestrator ==="
Get-Content $orchScript -Encoding UTF8 | Select-String 'keepalive' | Out-String | Write-Host

Stop-Transcript
Get-ChildItem $PSDir -File |
    Where-Object {
        $_.Length -eq 0 -and
        $_.Name -ne (Split-Path $log -Leaf) -and
        $_.LastWriteTime -lt (Get-Date).AddMinutes(-1)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "LOG: $log" -ForegroundColor Green
