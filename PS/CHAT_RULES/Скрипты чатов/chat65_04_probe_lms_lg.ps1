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
if (-not (Test-Path $PSDir)) { $PSDir = Join-Path $env:TEMP 'TO_DBI_PS_fallback'; New-Item -ItemType Directory -Path $PSDir -Force | Out-Null }
$resultFile = Join-Path $PSDir 'chat65_04_lms_lg.txt'

try { Stop-Transcript -ErrorAction Stop | Out-Null } catch { }

$log = Join-Path $PSDir "${hostTag}_65_04_probe_lms.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName"

$encNoBom = New-Object System.Text.UTF8Encoding($false)
$out = New-Object System.Collections.Generic.List[string]
$out.Add("=== 65_04 probe LMS on $hostTag ===")
$out.Add("host=$hostName hostTag=$hostTag")
$out.Add("date=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
$out.Add("")

$out.Add("[1] OLLAMA")
$out.Add("  OLLAMA_MODELS env = '$($env:OLLAMA_MODELS)'")
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
$has7bOllama = $false
if ($ollamaCmd) {
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $tmpO = Join-Path $PSDir 'chat65_04_ollama_list_lg.txt'
    & ollama list 2>&1 | Out-File -FilePath $tmpO -Encoding utf8
    $ErrorActionPreference = $oldEAP
    $out.Add("  ollama list -> $tmpO")
    if (Test-Path $tmpO) {
        $lines = [System.IO.File]::ReadAllLines($tmpO, [System.Text.Encoding]::UTF8)
        $has7bOllama = ($lines -join "`n") -match '(?i)qwen2\.5-coder:7b'
        $out.Add("  qwen2.5-coder:7b in ollama list: $has7bOllama")
    }
} else {
    $out.Add("  ollama: NOT FOUND in PATH")
}
$out.Add("")

$out.Add("[2] LM STUDIO")
$lmsCmd = Get-Command lms -ErrorAction SilentlyContinue
if ($lmsCmd) {
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $tmpL = Join-Path $PSDir 'chat65_04_lms_ls_lg.txt'
    & lms ls 2>&1 | Out-File -FilePath $tmpL -Encoding utf8
    $ErrorActionPreference = $oldEAP
    $out.Add("  lms ls -> $tmpL")
} else {
    $out.Add("  lms: NOT FOUND in PATH")
}
$out.Add("")

$out.Add("[3] CANDIDATE DIRS (F:)")
$lmCandidates = @('F:\LMStudio_Models\models\local-bank','F:\LMStudio_Models\models','F:\LMStudio_Models','F:\.lmstudio\models','F:\LM Studio','F:\Models','F:\models')
$foundLmDirs = @()
foreach ($c in $lmCandidates) {
    $ex = Test-Path -LiteralPath $c
    $out.Add("  $c -> exists=$ex")
    if ($ex) { $foundLmDirs += $c }
}
$out.Add("")

$out.Add("[4] GGUF scan (targeted)")
$allGguf = @()
foreach ($d in $foundLmDirs) {
    $out.Add("  scanning: $d")
    $found = Get-ChildItem -Path $d -Filter *.gguf -File -Recurse -ErrorAction SilentlyContinue
    foreach ($f in $found) { $allGguf += $f }
}
$out.Add("  gguf_total=$($allGguf.Count)")
$allGguf | Sort-Object Length -Descending | ForEach-Object { $out.Add(("    {0,6} GB  {1}" -f [math]::Round($_.Length/1GB,2), $_.FullName)) }
$out.Add("")

$target = 'F:\LMStudio_Models\models\local-bank\DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf'
$out.Add("[5] TARGET FILE")
$out.Add("  target = $target")
$out.Add("  target exists (should be False before copy) = $(Test-Path -LiteralPath $target)")

$out.Add("")
$out.Add("=== SUMMARY ===")
$out.Add("ollama_7b_on_LG=$has7bOllama")
$out.Add("lms_ls_file_created=$(Test-Path (Join-Path $PSDir 'chat65_04_lms_ls_lg.txt'))")
$out.Add("found_lm_dirs=$($foundLmDirs.Count)")
$out.Add("gguf_total=$($allGguf.Count)")
if ($allGguf.Count -eq 0) { $out.Add("RESULT: NO_GGUF_IN_KNOWN_LM_DIRS") }
else { $out.Add("RESULT: GGUF_FOUND") }

[System.IO.File]::WriteAllText($resultFile, ($out -join "`r`n"), $encNoBom)
Write-Host ""
Write-Host "=== RESULT FILE: $resultFile ==="
Get-Content $resultFile -Encoding UTF8 | Out-String | Write-Host
Write-Host ""

Stop-Transcript
Get-ChildItem $PSDir -File |
    Where-Object {
        $_.Length -eq 0 -and
        $_.Name -ne (Split-Path $log -Leaf) -and
        $_.LastWriteTime -lt (Get-Date).AddMinutes(-1)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "LOG: $log" -ForegroundColor Green
