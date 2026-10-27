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
$root  = 'F:\TO_DBI'
$repo  = 'F:\TO_DBI\SRC'
$log   = Join-Path $PSDir "${hostTag}_73_02b_patch.log"
$pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pyCmd) { $python = $pyCmd.Source } else {
    $cands = @("$env:LOCALAPPDATA\Programs\Python\Python312\python.exe", "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe")
    $python = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $python) { throw "python.exe не найден" }
}
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName python=$python root=$root"

$scanner    = Join-Path $repo "analyzer\scanner.py"
$test       = Join-Path $repo "tests\test_ds71_not_mentioned_real.py"
$bakScanner = "$scanner.ds73_02bak"
$bakTest    = "$test.ds73_02bak"
$msgFile    = Join-Path $PSDir "chat73_msg.txt"
$targetRepo = @("SRC/analyzer/scanner.py", "SRC/tests/test_ds71_not_mentioned_real.py")
$targetRel  = @("SRC/analyzer/scanner.py", "SRC/tests/test_ds71_not_mentioned_real.py")

$ok = $false
try {
    if (-not (Test-Path $scanner)) { throw "Нет scanner.py: $scanner" }
    if (-not (Test-Path $test))    { throw "Нет теста: $test" }

    # --- Бэкапы ДО правок (64_2) ---
    Copy-Item -LiteralPath $scanner -Destination $bakScanner -Force
    Copy-Item -LiteralPath $test    -Destination $bakTest    -Force
    Write-Host "BAK: $bakScanner ($((Get-Item $bakScanner).Length) B)")
    Write-Host "BAK: $bakTest ($((Get-Item $bakTest).Length) B)")

    # --- Патч scanner.py: точная замена одной строки ---
    $scOld = [System.IO.File]::ReadAllText($scanner, [System.Text.Encoding]::UTF8)
    $scNeedle = "                elif type_str.lower() == 'in':"
    $tRepl   = "    assert `"r_ref`" in names`r`n`r`n    # in [TYPE] должен нормализоваться до 'in'`r`n    for d in decls:`r`n        if d[1] in (`"v_unused_in`", `"r_ref`"):`r`n            assert d[2] == 'in', f`"{d[1]}: type_str={d[2]!r} — in [TYPE] не нормализован до 'in'`"`r`n`r`n    # базовые типы не должны превращаться в in"
    if (-not $tOld.Contains($tNeedle)) { throw "Не найден якорь в тесте" }
    $tNew = $tOld.Replace($tNeedle, $tRepl)
    if ($tNew -eq $tOld) { throw "Замена теста не изменила текст" }
    [System.IO.File]::WriteAllText($test, $tNew, (New-Object System.Text.UTF8Encoding($true)))
    Write-Host "WROTE test: $((Get-Item $test).Length) B")

    # --- AST-проверка .py (64_4: .py с кириллицей -> BOM; AST через utf-8-sig) ---
    & $python -c "import ast,sys; ast.parse(open(sys.argv[1],encoding='utf-8-sig').read()); print('AST_OK:', sys.argv[1])" $scanner
    if ($LASTEXITCODE -ne 0) { throw "AST fail scanner.py" }
    & $python -c "import ast,sys; ast.parse(open(sys.argv[1],encoding='utf-8-sig').read()); print('AST_OK:', sys.argv[1])" $test
    if ($LASTEXITCODE -ne 0) { throw "AST fail test" }

    # --- Точечный тест (05: EAP=Continue) ---
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        $out1 = Join-Path $PSDir "pytest_73_02b_target.txt"
        & $python -m pytest $test -q -W error::pytest.PytestReturnNotNoneWarning 2>&1 | Out-File -FilePath $out1 -Encoding utf8
        $rc1 = $LASTEXITCODE
        Get-Content $out1 | Out-String | Write-Host
        Write-Host "TARGET_RC: $rc1"
    } finally { $ErrorActionPreference = $oldEAP }
    if ($rc1 -ne 0) { throw "Точечный тест упал: rc=$rc1" }

    # --- Полный регресс ---
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        $out2 = Join-Path $PSDir "pytest_73_02b_full.txt"
        & $python -m pytest (Join-Path $repo "tests") -q 2>&1 | Out-File -FilePath $out2 -Encoding utf8
        $rc2 = $LASTEXITCODE
        Get-Content $out2 | Out-String | Write-Host
        Write-Host "FULL_RC: $rc2"
    } finally { $ErrorActionPreference = $oldEAP }
    if ($rc2 -ne 0) { throw "Полный регресс упал: rc=$rc2" }

    # --- msgfile no-BOM (06) ---
    $msgLines = @(
        "DS_73: type_str для NAME in [TYPE] -> 'in'",
        "",
        "- scanner.py: в _plp_iter_declarations нормализация in [TYPE] к 'in' (re.match ^in\s*\[).",
        "- test_ds71_not_mentioned_real.py: усилен test_iter_declarations_in_type — v_unused_in и r_ref дают type_str == 'in'.",
        "- Точечный + полный регресс зелёные."
    )
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encMsg)

    # --- git add/commit/push (06) ---
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        foreach ($rel in $targetRel) { & git -C $root add -- $rel 2>&1 | ForEach-Object { Write-Host $_ } }
        & git -C $root status -sb 2>&1 | ForEach-Object { Write-Host $_ }
        & git -C $root commit -F $msgFile 2>&1 | ForEach-Object { Write-Host $_ }
        $commitRc = $LASTEXITCODE
        Write-Host "COMMIT_RC: $commitRc"
        if ($commitRc -ne 0) { throw "git commit rc=$commitRc" }
        & git -C $root push origin feature/dockerization 2>&1 | ForEach-Object { Write-Host $_ }
        $pushRc = $LASTEXITCODE
        Write-Host "PUSH_RC: $pushRc"
        if ($pushRc -ne 0) {
            Write-Host "PUSH FAIL -> git reset --soft HEAD~1" -ForegroundColor Yellow
            & git -C $root reset --soft HEAD~1 2>&1 | ForEach-Object { Write-Host $_ }
            throw "push не удался, выполнен reset --soft HEAD~1"
        }
        & git -C $root status -sb 2>&1 | ForEach-Object { Write-Host $_ }
        & git -C $root log -1 --oneline 2>&1 | ForEach-Object { Write-Host $_ }
    } finally { $ErrorActionPreference = $oldEAP }

    $ok = $true
    Write-Host "OK: 73_02b завершён"
}
catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    # --- Откат из бэкапов (если файлы уже перезаписаны) ---
    try {
        if (Test-Path $bakScanner) { Copy-Item -LiteralPath $bakScanner -Destination $scanner -Force; Write-Host "ROLLBACK scanner.py: OK" }
        if (Test-Path $bakTest)    { Copy-Item -LiteralPath $bakTest    -Destination $test    -Force; Write-Host "ROLLBACK test: OK" }
    } catch { Write-Host "ROLLBACK ERROR: $($_.Exception.Message)" }
    throw
}
finally {
    Stop-Transcript -ErrorAction SilentlyContinue
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
