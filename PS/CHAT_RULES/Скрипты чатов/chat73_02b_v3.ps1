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
$log   = Join-Path $PSDir "${hostTag}_73_02b_v3.log"
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
$targetRel  = @("SRC/analyzer/scanner.py", "SRC/tests/test_ds71_not_mentioned_real.py")

$oldLineB64 = "ICAgICAgICAgICAgICAgIGVsaWYgdHlwZV9zdHIubG93ZXIoKSA9PSAnaW4nOg=="
$newLineB64 = "ICAgICAgICAgICAgICAgIGVsaWYgcmUubWF0Y2gocideaW5ccypcWycsIHR5cGVfc3RyLCByZS5JR05PUkVDQVNFKTo="
$oldLine = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($oldLineB64))
$newLine = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($newLineB64))

$testAnchorB64 = "ICAgIGFzc2VydCAiciByZWYiIGluIG5hbWVz"
$testInsertB64 = "ICAgIGFzc2VydCAiciByZWYiIGluIG5hbWVzDQogICAgZm9yIGQgaW4gZGVjbHM6DQogICAgICAgIGlmIGRbMV0gaW4gKCJ2X3VudXNlZF9pbiIsICJyX3JlZiIpOg0KICAgICAgICAgICAgYXNzZXJ0IGRbMl0gPT0gImluIiwgZiJ7ZFsxXX06IHR5cGVfc3RyPXtkWzJdIXJ9Ig=="
$testAnchor = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($testAnchorB64))
$testInsert = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($testInsertB64))

try {
    if (-not (Test-Path $scanner)) { throw "Нет scanner.py" }
    if (-not (Test-Path $test))    { throw "Нет теста" }

    Write-Host "=== ПРОВЕРКА СОСТОЯНИЯ ==="
    Write-Host ("SCANNER_BAK: " + (Test-Path $bakScanner))
    Write-Host ("TEST_BAK:    " + (Test-Path $bakTest))
    $scNow = [System.IO.File]::ReadAllText($scanner, [System.Text.Encoding]::UTF8)
    $tNow  = [System.IO.File]::ReadAllText($test,    [System.Text.Encoding]::UTF8)
    $hasNew = $scNow.Contains($newLine)
    $hasOld = $scNow.Contains($oldLine)
    $hasTst = $tNow.Contains($testInsert)
    Write-Host ("SCANNER_HAS_NEW: " + $hasNew)
    Write-Host ("SCANNER_HAS_OLD: " + $hasOld)
    Write-Host ("TEST_HAS_INSERT: " + $hasTst)
    $needScanner = $true
    $needTest    = $true
    if ($hasNew -and -not $hasOld) { $needScanner = $false }
    if ($hasTst) { $needTest = $false }
    Write-Host ("NEED_SCANNER: " + $needScanner)
    Write-Host ("NEED_TEST:    " + $needTest)

    if ($needScanner -and -not (Test-Path $bakScanner)) { Copy-Item -LiteralPath $scanner -Destination $bakScanner -Force; Write-Host "BAK scanner.py: OK" }
    if ($needTest    -and -not (Test-Path $bakTest))    { Copy-Item -LiteralPath $test    -Destination $bakTest    -Force; Write-Host "BAK test: OK" }

    if ($needScanner) {
        if (-not $hasOld) { throw "Нет старой строки в scanner.py" }
        $patched = $scNow.Replace($oldLine, $newLine)
        [System.IO.File]::WriteAllText($scanner, $patched, (New-Object System.Text.UTF8Encoding($true)))
        Write-Host "WROTE scanner.py: OK"
    } else { Write-Host "SKIP scanner.py" }

    if ($needTest) {
        if (-not $tNow.Contains($testAnchor)) { throw "Нет якоря в тесте" }
        $patchedT = $tNow.Replace($testAnchor, $testInsert)
        [System.IO.File]::WriteAllText($test, $patchedT, (New-Object System.Text.UTF8Encoding($true)))
        Write-Host "WROTE test: OK"
    } else { Write-Host "SKIP test" }

    Write-Host "=== AST ==="
    & $python -c "import ast,sys; ast.parse(open(sys.argv[1],encoding='utf-8-sig').read()); print('AST_OK', sys.argv[1])" $scanner
    if ($LASTEXITCODE -ne 0) { throw "AST fail scanner.py" }
    & $python -c "import ast,sys; ast.parse(open(sys.argv[1],encoding='utf-8-sig').read()); print('AST_OK', sys.argv[1])" $test
    if ($LASTEXITCODE -ne 0) { throw "AST fail test" }

    Write-Host "=== ТОЧЕЧНЫЙ ==="
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        $out1 = Join-Path $PSDir "pytest_73_02b_v3_target.txt"
        & $python -m pytest $test -q -W error::pytest.PytestReturnNotNoneWarning 2>&1 | Out-File -FilePath $out1 -Encoding utf8
        $rc1 = $LASTEXITCODE
        Get-Content $out1 | Out-String | Write-Host
        Write-Host "TARGET_RC: $rc1"
    } finally { $ErrorActionPreference = $oldEAP }
    if ($rc1 -ne 0) { throw "Точечный упал: rc=$rc1" }

    Write-Host "=== ПОЛНЫЙ ==="
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        $out2 = Join-Path $PSDir "pytest_73_02b_v3_full.txt"
        & $python -m pytest (Join-Path $repo "tests") -q 2>&1 | Out-File -FilePath $out2 -Encoding utf8
        $rc2 = $LASTEXITCODE
        Get-Content $out2 | Out-String | Write-Host
        Write-Host "FULL_RC: $rc2"
    } finally { $ErrorActionPreference = $oldEAP }
    if ($rc2 -ne 0) { throw "Полный упал: rc=$rc2" }

    Write-Host "=== MSGFILE ==="
    $msgLines = @(
        "DS_73: type_str для NAME in [TYPE] -> in"
        ""
        "- scanner.py: _plp_iter_declarations нормализует in [TYPE] к in."
        "- test_ds71_not_mentioned_real.py: усилен test_iter_declarations_in_type."
        "- Точечный + полный регресс зелёные."
    )
    $encMsg = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join [Environment]::NewLine), $encMsg)

    Write-Host "=== GIT ==="
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
            & git -C $root reset --soft HEAD~1 2>&1 | ForEach-Object { Write-Host $_ }
            throw "push fail, reset --soft HEAD~1"
        }
        & git -C $root status -sb 2>&1 | ForEach-Object { Write-Host $_ }
        & git -C $root log -1 --oneline 2>&1 | ForEach-Object { Write-Host $_ }
    } finally { $ErrorActionPreference = $oldEAP }

    Write-Host "OK: 73_02b_v3 завершён"
}
catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
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
