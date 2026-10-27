# chat64_06_fix_t3t4.ps1 (chat 64)
# Запускает chat64_06_patch.py, AST-check, pytest t3/t4, full regress, git commit/push.
# Без Python-кода внутри. BOM (.ps1 с кириллицей, 64_4).

Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }

$pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pyCmd) { $python = $pyCmd.Source } else {
    $cands = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "C:\Users\ainf1\AppData\Local\Programs\Python\Python312\python.exe"
    )
    $python = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $python) { throw "python.exe не найден" }
}

$PSDir      = 'F:\TO_DBI\PS'
$ScriptsDir = Join-Path $PSDir 'CHAT_RULES\Скрипты чатов'
$root       = 'F:\TO_DBI'
$repo       = 'F:\TO_DBI\SRC'
$targetRel  = 'SRC/tests/test_ds183_k4_model_setting.py'
$patchPy    = Join-Path $ScriptsDir 'chat64_06_patch.py'

$log = Join-Path $PSDir "${hostTag}_64_06_run.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName python=$python"

# 1) патч
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & $python $patchPy 2>&1 | Out-String | Write-Host
    $rcPatch = $LASTEXITCODE
} finally { $ErrorActionPreference = $oldEAP }
Write-Host "patch_exitcode=$rcPatch"
if ($rcPatch -ne 0) { throw "patch failed: $rcPatch" }

# 2) AST
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & $python -c "import ast,io; ast.parse(io.open(r'F:\TO_DBI\SRC\tests\test_ds183_k4_model_setting.py',encoding='utf-8-sig').read()); print('AST OK')" 2>&1 | Out-String | Write-Host
    $rcAst = $LASTEXITCODE
} finally { $ErrorActionPreference = $oldEAP }
if ($rcAst -ne 0) { throw "AST failed: $rcAst" }

# 3) pytest t3/t4
$out1 = Join-Path $PSDir "${hostTag}_64_06_pytest_t3t4.txt"
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & $python -m pytest (Join-Path $repo 'tests\test_ds183_k4_model_setting.py') -q -W error::pytest.PytestReturnNotNoneWarning 2>&1 | Out-File -FilePath $out1 -Encoding utf8
    $rc1 = $LASTEXITCODE
} finally { $ErrorActionPreference = $oldEAP }
Get-Content $out1 | Out-String | Write-Host
Write-Host "pytest_t3t4_exitcode=$rc1"
if ($rc1 -ne 0) { throw "pytest t3/t4 failed: $rc1 (see $out1)" }

# 4) full regress
$out2 = Join-Path $PSDir "${hostTag}_64_06_pytest_full.txt"
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & $python -m pytest (Join-Path $repo 'tests') -q 2>&1 | Out-File -FilePath $out2 -Encoding utf8
    $rc2 = $LASTEXITCODE
} finally { $ErrorActionPreference = $oldEAP }
Get-Content $out2 | Select-Object -Last 25 | Out-String | Write-Host
Write-Host "pytest_full_exitcode=$rc2"
if ($rc2 -ne 0) { throw "full regress failed: $rc2 (see $out2)" }

# 5) git commit/push
$msgFile = Join-Path $PSDir "${hostTag}_64_06_msgfile.txt"
$msgLines = @(
    "DS_186/t3/t4: garantirovannyj otkat settings.json (try/finally)"
    ""
    "- t3/t4 finally: ne brosaem RuntimeError, tolko WARN + restore + remove backup"
    "- pytest: t3t4 + full regress zelenye (05)"
)
$encNoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encNoBom)

$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & git -C $root add -- $targetRel 2>&1 | Out-String | Write-Host
    & git -C $root status -sb 2>&1 | Out-String | Write-Host
    & git -C $root commit -F $msgFile 2>&1 | Out-String | Write-Host
    $rcCommit = $LASTEXITCODE
    if ($rcCommit -eq 0) {
        & git -C $root push origin feature/dockerization 2>&1 | Out-String | Write-Host
        Write-Host "push_exitcode=$LASTEXITCODE"
    } else {
        Write-Host "commit_exitcode=$rcCommit"
    }
} finally { $ErrorActionPreference = $oldEAP }

& git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host

Stop-Transcript
Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 } | Remove-Item -Force
Write-Host "LOG: $log" -ForegroundColor Green
