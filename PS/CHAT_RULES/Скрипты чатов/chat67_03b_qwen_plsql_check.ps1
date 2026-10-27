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
$ResDir  = Join-Path $ScrDir 'chat67_03b_results'
$CleanDir= Join-Path $ScrDir 'chat67_03b_clean'
$IKA     = 'F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3'
$Ollama  = 'http://localhost:11434'
$Model   = 'qwen2.5-coder:7b'

foreach ($d in @($ScrDir, $ResDir, $CleanDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}
if (-not (Test-Path $IKA)) { throw "Нет ИКА: $IKA" }

$log = Join-Path $PSDir "${hostTag}_67_03b_qwen_plsql_check.log"
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
$inv = @()
foreach ($f in $files) {
    $sha = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
    $lines = (Get-Content -LiteralPath $f.FullName | Measure-Object -Line).Lines
    Write-Host ("M0: {0} | {1} b | {2} lines | sha={3}" -f $f.Name, $f.Length, $lines, $sha.Substring(0,12))
    $inv += [pscustomobject]@{ name=$f.Name; path=$f.FullName; bytes=$f.Length; lines=$lines; sha256=$sha }
}

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
    $client = New-Object System.Net.Http.HttpClient
    $client.Timeout = [TimeSpan]::FromSeconds(240)
    try {
        $content = New-Object System.Net.Http.StringContent($body, [System.Text.Encoding]::UTF8, 'application/json')
        $resp = $client.PostAsync("$Ollama/api/generate", $content).Result
        if (-not $resp.IsSuccessStatusCode) { throw "HTTP $($resp.StatusCode)" }
        $respStr = $resp.Content.ReadAsStringAsync().Result
        return [pscustomobject]@{ resp = ($respStr | ConvertFrom-Json); ms = 0 }
    } catch {
        throw "Ollama call failed: $($_.Exception.Message)"
    } finally {
        $client.Dispose()
    }
}

function Test-JsonValid([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return $false }
    $t = $s.Trim()
    if ($t -match '^```') { return $false }
    if (-not ($t.StartsWith('{') -and $t.EndsWith('}'))) { return $false }
    try { $null = $t | ConvertFrom-Json; return $true } catch { return $false }
}

function Get-FinniganFlags([string]$s) {
    $hits = @()
    if ($s -match 'DBMS_CRYPTO') {
        if ($s -match '(?i)\bAES256\b' -and $s -notmatch '(?i)ENCRYPT_AES256') { $hits += 'AES256_without_ENCRYPT_' }
        if ($s -match '(?i)\bRAW_TO_STRING\b') { $hits += 'RAW_TO_STRING' }
        if ($s -match '(?i)BASE64_ENCODE\s*\([^)]*,[^)]*\)') { $hits += 'BASE64_ENCODE_multiarg' }
    }
    return $hits
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
        options = @{ temperature = 0; num_predict = 512; num_ctx = 8192 }
    }
    $body = $bodyObj | ConvertTo-Json -Depth 6 -Compress
    Write-Host ("CALL: {0} (prompt len={1})" -f $f.Name, $prompt.Length)
    
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $r = Invoke-Ollama $body
        $sw.Stop()
        $r.ms = [int]$sw.ElapsedMilliseconds
    } catch {
        $sw.Stop()
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
    $ff = Get-FinniganFlags $text
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
        finnigan = ($ff -join ',')
        truncated = $truncated
        raw = $text
    }
    
    $outJson = Join-Path $ResDir ($f.Name + '.json')
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($outJson, $text, $enc)
    Write-Host ("OK: {0} valid={1} fixes={2} ms={3} finnigan=[{4}]" -f $f.Name, $valid, $nFix, $r.ms, ($ff -join ','))
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

# --- M3: чистый файл ---
$m3 = $null
if ($files.Count -gt 0) {
    $cleanSrc = $files | Select-Object -First 1
    $cleanFile = Join-Path $CleanDir ($cleanSrc.BaseName + '_clean' + $cleanSrc.Extension)
    $cleanCode = [System.IO.File]::ReadAllText($cleanSrc.FullName, [System.Text.Encoding]::UTF8)
    $cleanCode2 = [regex]::Replace($cleanCode, '(?m)^\s*--\s*\d{4}\.\d{2}\.\d{2}.*$', '')
    [System.IO.File]::WriteAllText($cleanFile, $cleanCode2, (New-Object System.Text.UTF8Encoding($false)))
    $bodyClean = (@{
        model=$Model; prompt=$promptTmpl.Replace('<<<FILE>>>', $cleanCode2); stream=$false;
        options=@{temperature=0; num_predict=512; num_ctx=8192}
    } | ConvertTo-Json -Depth 6 -Compress)
    Write-Host ("M3: clean test on {0}" -f (Split-Path $cleanFile -Leaf))
    try {
        $rc = Invoke-Ollama $bodyClean
        $tc = [string]$rc.resp.response
        $vc = Test-JsonValid $tc
        $m3 = [pscustomobject]@{ file=$cleanFile; valid=$vc; text=$tc; ms=$rc.ms }
        $m3clean = $null; $m3n = $null
        if ($vc) { $pc = $tc.Trim() | ConvertFrom-Json; $m3clean=[bool]$pc.clean; $m3n=@($pc.fixes).Count }
        Write-Host ("M3: valid={0} clean={1} fixes={2}" -f $vc, $m3clean, $m3n)
        $m3 | Add-Member -NotePropertyName clean -NotePropertyValue $m3clean -Force
        $m3 | Add-Member -NotePropertyName n_fixes -NotePropertyValue $m3n -Force
    } catch {
        Write-Host ("M3 ERR: {0}" -f $_.Exception.Message)
    }
}

# --- M5: повторяемость T=0 на первом успешном файле ---
$m5ok = $null
$firstOk = $results | Where-Object { $_.ok -eq $true -and $_.valid -eq $true } | Select-Object -First 1
if ($firstOk) {
    $f0 = $files | Where-Object { $_.Name -eq $firstOk.name } | Select-Object -First 1
    $code0 = [System.IO.File]::ReadAllText($f0.FullName, [System.Text.Encoding]::UTF8)
    if ($code0.Length -gt 3000) { $code0 = $code0.Substring(0, 3000) }
    $body0 = (@{ model=$Model; prompt=$promptTmpl.Replace('<<<FILE>>>', $code0); stream=$false; options=@{temperature=0; num_predict=512; num_ctx=8192} } | ConvertTo-Json -Depth 6 -Compress)
    Write-Host ("M5: repeat test on {0}" -f $f0.Name)
    try {
        $r1 = Invoke-Ollama $body0
        Start-Sleep -Seconds 1
        $r2 = Invoke-Ollama $body0
        $t1 = [string]$r1.resp.response; $t2 = [string]$r2.resp.response
        $p1 = if (Test-JsonValid $t1) { $t1.Trim() | ConvertFrom-Json } else { $null }
        $p2 = if (Test-JsonValid $t2) { $t2.Trim() | ConvertFrom-Json } else { $null }
        function FixKey($x) { if ($null -eq $x) { return '' } ; $x.fixes | ForEach-Object { '{0}|{1}' -f $_.rule, $_.line } | Sort-Object | Out-String }
        $k1 = FixKey $p1; $k2 = FixKey $p2
        $m5ok = ($k1 -eq $k2)
        Write-Host ("M5: repeatable={0}" -f $m5ok)
    } catch {
        Write-Host ("M5 ERR: {0}" -f $_.Exception.Message)
    }
}

# --- Итоговый отчёт в лог ---
Write-Host '=== SUMMARY ==='
Write-Host ("files={0} valid={1} non_empty={2} p50={3}ms p95={4}ms M3_clean={5} M5_repeat={6}" -f `
    $nTotal, $nValid, $nNonEmpty, $p50, $p95, ($m3.clean), $m5ok)
$finniganAll = @($results | Where-Object { $_.ok -and $_.finnigan -ne '' })
if ($finniganAll.Count -gt 0) {
    Write-Host ("finnigan_flags: {0}" -f (($finniganAll | ForEach-Object { $_.name + ':' + $_.finnigan }) -join '; '))
} else {
    Write-Host 'finnigan_flags: none'
}

$summary = [pscustomobject]@{
    chat='67_03b'; host=$hostTag; ika=$IKA; model=$Model
    files=$nTotal; valid=$nValid; non_empty=$nNonEmpty
    p50_ms=$p50; p95_ms=$p95
    m3_clean=if ($m3) { $m3.clean } else { $null }
    m5_repeatable=$m5ok
    finnigan=@($finniganAll | ForEach-Object { $_.name + ':' + $_.finnigan })
    results=$results
}
$enc = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $ResDir '_summary.json'), ($summary | ConvertTo-Json -Depth 8), $enc)

Stop-Transcript
Get-ChildItem $PSDir -File |
    Where-Object {
        $_.Length -eq 0 -and
        $_.Name -ne (Split-Path $log -Leaf) -and
        $_.LastWriteTime -lt (Get-Date).AddMinutes(-1)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "LOG: $log" -ForegroundColor Green
