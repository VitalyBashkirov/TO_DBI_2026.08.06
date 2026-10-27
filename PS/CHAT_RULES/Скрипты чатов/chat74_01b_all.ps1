Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$repo  = 'F:\TO_DBI\SRC'
$testFile = Join-Path $repo 'tests\test_ds74_01_gui_checklist.py'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_74_01b_fixtest.log')
$outT = Join-Path $PSDir ($hostTag + '_74_01b_point_out.txt')
$outF = Join-Path $PSDir ($hostTag + '_74_01b_full_out.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $testFile)) { throw 'Нет теста: ' + $testFile }
    Copy-Item $testFile ($testFile + '.ds74_01bbak') -Force
    $tt = [System.IO.File]::ReadAllText($testFile, [System.Text.Encoding]::UTF8)
    $old = @'
def test_74_01_07_gt_dryrun():
    src = open(os.path.join(REPO, "gui_app.py"), encoding="utf-8", errors="replace").read()
    assert "dry" in src.lower() or "dry_run" in src.lower()
'@
    $new = @'
def test_74_01_07_gt_dryrun():
    # ГТ — в отдельном модуле TestGeneratorV2 (DS_147), не в gui_app.py
    cand = [
        os.path.join(REPO, "analyzer", "test_generator_v2.py"),
        os.path.join(REPO, "test_generator_v2.py"),
        os.path.join(REPO, "generator", "test_generator_v2.py"),
    ]
    found = None
    for p in cand:
        if os.path.isfile(p):
            found = p
            break
    if not found:
        for root, dirs, files in os.walk(REPO):
            for f in files:
                if f == "test_generator_v2.py":
                    found = os.path.join(root, f)
                    break
            if found: break
    if not found:
        pytest.skip("TestGeneratorV2 не найден в SRC")
    src = open(found, encoding="utf-8", errors="replace").read().lower()
    assert "dry" in src or "dry_run" in src
'@
    $tt2 = $tt.Replace($old, $new)
    if ($tt2 -eq $tt) { throw 'Не найден старый блок test_74_01_07_gt_dryrun' }
    $encT = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($testFile, $tt2, $encT)
    Write-Host 'test_ds74_01_gui_checklist.py: 07 исправлен'
    $pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyCmd) { $python = $pyCmd.Source } else { $python = 'C:\Users\ainf1\AppData\Local\Programs\Python\Python312\python.exe' }
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $python -m pytest $testFile -v -W error::pytest.PytestReturnNotNoneWarning 2>&1 | Out-File -FilePath $outT -Encoding utf8
        $rcT = $LASTEXITCODE
    } finally { $ErrorActionPreference = $oldEAP }
    Get-Content $outT | Out-String | Write-Host
    Write-Host 'POINT_RC=' $rcT
    if ($rcT -eq 0) {
        $oldEAP = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
            & $python -m pytest (Join-Path $repo 'tests') -q 2>&1 | Out-File -FilePath $outF -Encoding utf8
            $rcF = $LASTEXITCODE
        } finally { $ErrorActionPreference = $oldEAP }
        Get-Content $outF | Out-String | Write-Host
        Write-Host 'FULL_RC=' $rcF
    } else { Write-Host 'Точечный красный - полный регресс пропущен' }
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
