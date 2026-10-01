# ============================================
# test_all_models.ps1
# Obshchiy test modeley Ollama i LMS dlya chata
# ============================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$OllamaUrl = "http://localhost:11434"
$LmsUrl = "http://localhost:1234"
$NumCtx = 4096
$TimeoutSec = 600
$ResultDir = "F:\TO_DBI\temp\model_tests"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultFile = Join-Path $ResultDir "test_$Timestamp.csv"
$MdFile = Join-Path $ResultDir "test_$Timestamp.md"

New-Item -ItemType Directory -Force -Path $ResultDir | Out-Null

Add-Type -AssemblyName System.Net.Http

# ============================================
# TESTOVYE VOPROSY (Cyrillic)
# ============================================
$tests = @(
    @{ id = 1; name = "greeting"; prompt = [char]0x041F + [char]0x0440 + [char]0x0438 + [char]0x0432 + [char]0x0435 + [char]0x0442 + "! " + [char]0x041A + [char]0x0430 + [char]0x043A + " " + [char]0x0434 + [char]0x0435 + [char]0x043B + [char]0x0430 + "?" }
)

# Uproshchennyy nabor - perevedem cherez peremennuyu
$q1 = -join ([char]0x041F,[char]0x0440,[char]0x0438,[char]0x0432,[char]0x0435,[char]0x0442,"!"," ",[char]0x041A,[char]0x0430,[char]0x043A," ",[char]0x0434,[char]0x0435,[char]0x043B,[char]0x0430,"?")
$q2 = -join ([char]0x0420,[char]0x0430,[char]0x0441,[char]0x0441,[char]0x043A,[char]0x0430,[char]0x0436,[char]0x0438," ",[char]0x043F,[char]0x0440,[char]0x043E," PL/SQL ",[char]0x0432," 3 ",[char]0x043F,[char]0x0440,[char]0x0435,[char]0x0434,[char]0x043B,[char]0x043E,[char]0x0436,[char]0x0435,[char]0x043D,[char]0x0438,[char]0x044F,[char]0x0445,".")
$q3 = -join ([char]0x041A,[char]0x0430,[char]0x043A," PL/SQL ",[char]0x043E,[char]0x0431,[char]0x044A,[char]0x044F,[char]0x0432,[char]0x0438,[char]0x0442,[char]0x044C," VARCHAR2?")
$q4 = -join ("17 x 24 = ?")
$q5 = -join ([char]0x041E,[char]0x0442,[char]0x0432,[char]0x0435,[char]0x0442,[char]0x044C," ",[char]0x043E,[char]0x0434,[char]0x043D,[char]0x0438,[char]0x043C," ",[char]0x0441,[char]0x043B,[char]0x043E,[char]0x0432,[char]0x043E,[char]0x043C,": ",[char]0x0441,[char]0x0442,[char]0x043E,[char]0x043B,[char]0x0438,[char]0x0446,[char]0x0430," ",[char]0x0424,[char]0x0440,[char]0x0430,[char]0x043D,[char]0x0446,[char]0x0438,[char]0x0438,"?")

$tests = @(
    @{ id = 1; name = "greeting"; prompt = $q1 },
    @{ id = 2; name = "plsql";    prompt = $q2 },
    @{ id = 3; name = "code";     prompt = $q3 },
    @{ id = 4; name = "math";     prompt = $q4 },
    @{ id = 5; name = "one-word"; prompt = $q5 }
)

# ============================================
# FUNKCII
# ============================================

function Get-OllamaModels {
    try {
        $r = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 5
        return $r.models | ForEach-Object {
            [PSCustomObject]@{ Backend = "Ollama"; Name = $_.name; Size = [math]::Round($_.size / 1GB, 2) }
        }
    } catch { Write-Host "[WARN] Ollama nedostupna" -ForegroundColor Yellow; return @() }
}

function Get-LmsModels {
    try {
        $r = Invoke-RestMethod -Uri "$LmsUrl/v1/models" -Method Get -TimeoutSec 5
        return $r.data | ForEach-Object {
            [PSCustomObject]@{ Backend = "LMS"; Name = $_.id; Size = 0 }
        }
    } catch { Write-Host "[WARN] LMS nedostupna" -ForegroundColor Yellow; return @() }
}

function Invoke-OllamaChat {
    param([string]$Model, [string]$Prompt, [int]$NumCtx, [int]$TimeoutSec)
    $client = New-Object System.Net.Http.HttpClient
    $client.Timeout = [TimeSpan]::FromSeconds($TimeoutSec)
    $jsonBody = ConvertTo-Json -Depth 10 -Compress @{
        model = $Model
        messages = @(@{ role = "user"; content = $Prompt })
        stream = $false
        options = @{ num_ctx = $NumCtx }
        keep_alive = "600s"
    }
    $content = New-Object System.Net.Http.StringContent($jsonBody, [System.Text.Encoding]::UTF8, "application/json")
    $sw = [Diagnostics.Stopwatch]::StartNew()
    try {
        $response = $client.PostAsync("$OllamaUrl/api/chat", $content).Result
        $responseBytes = $response.Content.ReadAsByteArrayAsync().Result
        $jsonString = [System.Text.Encoding]::UTF8.GetString($responseBytes)
        $json = ConvertFrom-Json $jsonString
        $sw.Stop()
        return @{ Answer = $json.message.content; Time = [math]::Round($sw.Elapsed.TotalSeconds, 1); Success = $true; Error = "" }
    } catch {
        $sw.Stop()
        return @{ Answer = ""; Time = [math]::Round($sw.Elapsed.TotalSeconds, 1); Success = $false; Error = $_.Exception.Message }
    } finally { $client.Dispose() }
}

function Invoke-LmsChat {
    param([string]$Model, [string]$Prompt, [int]$TimeoutSec)
    $client = New-Object System.Net.Http.HttpClient
    $client.Timeout = [TimeSpan]::FromSeconds($TimeoutSec)
    $jsonBody = ConvertTo-Json -Depth 10 -Compress @{
        model = $Model
        messages = @(@{ role = "user"; content = $Prompt })
        temperature = 0.6
        max_tokens = 1000
    }
    $content = New-Object System.Net.Http.StringContent($jsonBody, [System.Text.Encoding]::UTF8, "application/json")
    $sw = [Diagnostics.Stopwatch]::StartNew()
    try {
        $response = $client.PostAsync("$LmsUrl/v1/chat/completions", $content).Result
        $responseBytes = $response.Content.ReadAsByteArrayAsync().Result
        $jsonString = [System.Text.Encoding]::UTF8.GetString($responseBytes)
        $json = ConvertFrom-Json $jsonString
        $sw.Stop()
        return @{ Answer = $json.choices[0].message.content; Time = [math]::Round($sw.Elapsed.TotalSeconds, 1); Success = $true; Error = "" }
    } catch {
        $sw.Stop()
        return @{ Answer = ""; Time = [math]::Round($sw.Elapsed.TotalSeconds, 1); Success = $false; Error = $_.Exception.Message }
    } finally { $client.Dispose() }
}

function Analyze-Answer {
    param([string]$Answer)
    if ([string]::IsNullOrWhiteSpace($Answer)) {
        return @{ HasQuestion = $false; HasCyrillic = $false; Length = 0; Preview = "" }
    }
    $hasQuestion = $Answer.Contains("?")
    $hasCyr = $false
    foreach ($ch in $Answer.ToCharArray()) {
        $code = [int]$ch
        if (($code -ge 0x0410 -and $code -le 0x044F) -or $code -eq 0x0401 -or $code -eq 0x0451) {
            $hasCyr = $true
            break
        }
    }
    $preview = $Answer.Substring(0, [Math]::Min(100, $Answer.Length)) -replace "`r?`n", " "
    return @{ HasQuestion = $hasQuestion; HasCyrillic = $hasCyr; Length = $Answer.Length; Preview = $preview }
}

# ============================================
# SBOR MODELEY
# ============================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  OBSHCHIY TEST MODELEY OLLAMA I LM STUDIO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Sbor modeley..." -ForegroundColor Yellow
$ollamaModels = Get-OllamaModels
$lmsModels = Get-LmsModels

Write-Host "  Ollama: $($ollamaModels.Count) modeley" -ForegroundColor Green
$ollamaModels | ForEach-Object { Write-Host "    - $($_.Name) ($($_.Size) GB)" }
Write-Host "  LM Studio: $($lmsModels.Count) modeley" -ForegroundColor Green
$lmsModels | ForEach-Object { Write-Host "    - $($_.Name)" }

$allModels = @()
$allModels += $ollamaModels
$allModels += $lmsModels

if ($allModels.Count -eq 0) {
    Write-Host "[ERROR] Net modeley." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Testirovanie $($allModels.Count) modeley x $($tests.Count) voprosov = $($allModels.Count * $tests.Count) zaprosov" -ForegroundColor Yellow
Write-Host ""

# ============================================
# TESTIROVANIE
# ============================================

$results = @()

foreach ($model in $allModels) {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Model: $($model.Backend) / $($model.Name)" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    
    foreach ($test in $tests) {
        Write-Host "  [$($test.id)/$($tests.Count)] $($test.name): " -NoNewline
        
        $r = $null
        if ($model.Backend -eq "Ollama") {
            $r = Invoke-OllamaChat -Model $model.Name -Prompt $test.prompt -NumCtx $NumCtx -TimeoutSec $TimeoutSec
        } else {
            $r = Invoke-LmsChat -Model $model.Name -Prompt $test.prompt -TimeoutSec $TimeoutSec
        }
        
        $analysis = Analyze-Answer -Answer $r.Answer
        
        $status = if ($r.Success) { "OK" } else { "FAIL" }
        $cyr = if ($analysis.HasCyrillic) { "Cyr" } else { "noCyr" }
        
        Write-Host "[$status] $($r.Time) sec | $($analysis.Length) simv | $cyr" -ForegroundColor $(if ($r.Success) { "Green" } else { "Red" })
        
        $results += [PSCustomObject]@{
            Backend = $model.Backend
            Model = $model.Name
            TestID = $test.id
            TestName = $test.name
            Time = $r.Time
            Length = $analysis.Length
            HasCyr = $analysis.HasCyrillic
            HasQuestion = $analysis.HasQuestion
            Success = $r.Success
            Error = $r.Error
            Answer = $r.Answer
            Preview = $analysis.Preview
        }
        
        Start-Sleep -Seconds 1
    }
    Write-Host ""
}

# ============================================
# SOKHRANENIE
# ============================================

Write-Host "[3/3] Sokhranenie rezultatov..." -ForegroundColor Yellow

$results | Select-Object Backend, Model, TestID, TestName, Time, Length, HasCyr, HasQuestion, Success, Preview |
    Export-Csv -Path $ResultFile -NoTypeInformation -Encoding UTF8

$md = "# Rezultaty testa modeley`n`n"
$md += "**Data:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
$md += "**Modeley:** $($allModels.Count) | **Voprosov:** $($tests.Count) | **Zaprosov:** $($results.Count)`n`n"
$md += "## Svodka`n`n"
$md += "| Model | Backend | Avg time | OK | Cyr |`n"
$md += "|---|---|---|---|---|`n"

foreach ($model in $allModels) {
    $mResults = $results | Where-Object { $_.Model -eq $model.Name -and $_.Backend -eq $model.Backend }
    $avgTime = ($mResults | Measure-Object -Property Time -Average).Average
    $okCount = ($mResults | Where-Object { $_.Success }).Count
    $cyrCount = ($mResults | Where-Object { $_.HasCyr }).Count
    $md += "| $($model.Name) | $($model.Backend) | $([math]::Round($avgTime,1)) sec | $okCount/$($mResults.Count) | $cyrCount/$($mResults.Count) |`n"
}

$md | Out-File -FilePath $MdFile -Encoding UTF8

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  TEST ZAVERSHEN" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "  CSV:      $ResultFile"
Write-Host "  Markdown: $MdFile"
Write-Host ""
Write-Host "Otkryt Markdown:" -ForegroundColor Yellow
Write-Host "  notepad $MdFile"