Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }

$PSDir   = 'F:\TO_DBI\PS'
$CRDir   = 'F:\TO_DBI\PS\CHAT_RULES'
$ScrDir  = Join-Path $CRDir 'Скрипты чатов'
$ResDir  = Join-Path $ScrDir 'chat67_03c_results'
$CleanDir= Join-Path $ScrDir 'chat67_03c_clean'
$IKA     = 'F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3'
$Ollama  = 'http://localhost:11434'
$Model   = 'qwen2.5-coder:3b'

foreach ($d in @($ScrDir, $ResDir, $CleanDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}
if (-not (Test-Path $IKA)) { throw "Нет ИКА: $IKA" }

$log = Join-Path $PSDir "${hostTag}_67_03c_qwen3b_check.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"
Write-Host "IKA=$IKA"
Write-Host "Ollama=$Ollama Model=$Model"

# --- Проверка Ollama API ---
try {
    $tags = Invoke-RestMethod -Uri "$Ollama/api/tags" -TimeoutSec 5
} catch {
    throw "Ollama не отвечает на $Ollama/api/tags : $($_.Exception.Message)"
}
$hasModel = @($tags.models | Where-Object { $_.name -eq $Model -or $_.model -eq $Model }).Count -gt 0
Write-Host ("Ollama OK. model {0}: {1}" -f $Model, $hasModel)
if (-not $hasModel) { throw "Модель $Model не найдена в Ollama" }

# --- M0: инвентаризация ИКА ---
$files = Get-ChildItem -LiteralPath $IKA -File -Recurse |
    Where-Object { $_.Extension -in '.plp', '.sql', '.pls', '.pkb', '.pks', '.prc', '.fnc', '.trg', '.vw' } |
    Sort-Object FullName
if ($files.Count -eq 0) { throw "ИКА пуст (нет PL/SQL-файлов): $IKA" }
Write-Host ("M0: files={0}" -f $files.Count)

# --- Промпт ---
$promptTmpl = @'
Ты — PL/SQL-ревьюер. На входе — файл PL/SQL.
Верни ТОЛЬКО JSON без markdown-обёртки и без пояснений:
{"fixes":[{"rule":"<код правила>","line":<номер строки>,"comment":"<кратко>"}],"clean":<true|false>}
Если правок нет — {"fixes":[],"clean":true}.
Никакого текста до/после JSON.

Файл:
<<<FILE>>>
'@

function Invoke-Ollama([string]$body) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
    try {
        $webResp = Invoke-WebRequest -Uri "$Ollama/api/generate" -Method Post `
            -ContentType 'application/json; charset=utf-8' `
            -Body $bytes -TimeoutSec 120 -UseBasicParsing
        $sw.Stop()
        $str = [System.Text.Encoding]::UTF8.GetString($webResp.RawContentStream.ToArray())
        return [pscustomobject]@{ resp = ($str | ConvertFrom-Json); ms = [int]$sw.ElapsedMilliseconds }
    } catch {
        $sw.Stop()
        throw "Ollama call failed (${($sw.ElapsedMilliseconds)}ms): $($_.Exception.Message)"
    }
}

function Test-JsonValid([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return $false }
    $t = $s.Trim()
    if ($t -match '^```') { return $false }
    if (-not ($t.StartsWith('{') -and $t.EndsWith('}'))) { return $false }
    try { $null = $t | ConvertFrom-Json; return $true } catch { return $false }
}

$results = @()
$latencies = @()

foreach ($f in $files) {
    $code = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    if ([string]::IsNullOrWhiteSpace($code)) { Write-Host ("SKIP empty: {0}" -f $f.Name); continue }

    $truncated = $false
    if ($code.Length -gt 3000) {
        $code = $code.Substring(0, 3000)
        $truncated = $true
        Write-Host ("TRUNC: {0} (обрезано до 3000)" -f $f.Name)
    }
    
    $prompt = $promptTmpl.Replace('<<<FILE>>>', $code)
    $bodyObj = @{
        model   = $Model
        prompt  = $prompt
        stream  = $false
        options = @{ temperature = 0; num_predict = 256; num_ctx = 8192 }
    }
    $body = $bodyObj | ConvertTo-Json -Depth 6 -Compress
    Write-Host ("CALL: {0} (prompt len={1})" -f $f.Name, $prompt.Length)
    
    try {
        $r = Invoke-Ollama $body
    } catch {
        Write-Host ("ERR: {0}: {1}" -f $f.Name, $_.Exception.Message)
        $results += [pscustomobject]@{ name=$f.Name; ok=$false; error=$_.Exception.Message }
        continue
    }
    
    $text = [string]$r.resp.response
    $valid = Test-JsonValid $text
    $parsed = $null
    if ($valid) { $parsed = $text.Trim() | ConvertFrom-Json }
    $nFix = 0
    if ($parsed) { $nFix = @($parsed.fixes).Count }
    $latencies += $r.ms
    
    $results += [pscustomobject]@{
        name = $f.Name
        ok = $true
        valid = $valid
        n_fixes = $nFix
        clean = if ($parsed) { [bool]$parsed.clean } else { $null }
        ms = $r.ms
        prompt_eval_count = $r.resp.prompt_eval_count
        eval_count = $r.resp.eval_count
        total_duration_ns = $r.resp.total_duration
        truncated = $truncated
        raw = $text
    }
    
    $outJson = Join-Path $ResDir ($f.Name + '.json')
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($outJson, $text, $enc)
    Write-Host ("OK: {0} valid={1} fixes={2} ms={3}" -f $f.Name, $valid, $nFix, $r.ms)
}

# --- M1/M2'/M4: сводка ---
$nTotal = @($results | Where-Object { $_.ok }).Count
$nValid = @($results | Where-Object { $_.ok -and $_.valid }).Count
$nNonEmpty = @($results | Where-Object { $_.ok -and $_.valid -and $_.n_fixes -gt 0 }).Count
$latSorted = @($latencies | Sort-Object)
function Pctl($arr, $p) {
    if ($arr.Count -eq 0) { return 0 }
    $idx = [int][math]::Ceiling(($p/100.0) * $arr.Count) - 1
    if ($idx -lt 0) { $idx = 0 }
    if ($idx -ge $arr.Count) { $idx = $arr.Count - 1 }
    return $arr[$idx]
}
$p50 = Pctl $latSorted 50
$p95 = Pctl $latSorted 95
Write-Host "--- M1: valid $nValid / $nTotal ---"
Write-Host "--- M2': non-empty fixes $nNonEmpty / $nTotal ---"
Write-Host "--- M4: p50=${p50}ms p95=${p95}ms ---"

Write-Host '=== SUMMARY ==='
Write-Host ("files={0} valid={1} non_empty={2} p50={3}ms p95={4}ms" -f `
    $nTotal, $nValid, $nNonEmpty, $p50, $p95)

Stop-Transcript
Get-ChildItem $PSDir -File |
    Where-Object {
        $_.Length -eq 0 -and
        $_.Name -ne (Split-Path $log -Leaf) -and
        $_.LastWriteTime -lt (Get-Date).AddMinutes(-1)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "LOG: $log" -ForegroundColor Green
