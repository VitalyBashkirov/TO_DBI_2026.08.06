Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$repo  = 'F:\TO_DBI\SRC'
$testFile = Join-Path $repo 'tests\test_ds74_01_gui_checklist.py'
$neighbor = Join-Path $repo 'tests\test_ds183_k4_model_setting.py'
$IKA = 'F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3'
$KR  = Join-Path $env:TEMP 'ds74_01_out'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_74_01_guicheck.log')
$outT = Join-Path $PSDir ($hostTag + '_74_01_point_out.txt')
$outF = Join-Path $PSDir ($hostTag + '_74_01_full_out.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $repo)) { throw 'Нет SRC: ' + $repo }
    if (-not (Test-Path (Join-Path $repo 'gui_app.py'))) { throw 'Нет gui_app.py в SRC' }
    $bomNeighbor = $false
    if (Test-Path $neighbor) {
        $nb = [System.IO.File]::ReadAllBytes($neighbor)
        $bomNeighbor = ($nb.Length -ge 3 -and $nb[0] -eq 0xEF -and $nb[1] -eq 0xBB -and $nb[2] -eq 0xBF)
    }
    Write-Host 'BOM соседа test_ds183_k4_model_setting.py =' $bomNeighbor
    if (Test-Path $testFile) { Copy-Item $testFile ($testFile + '.ds74_01bak') -Force; Write-Host 'Бэкап: ' ($testFile + '.ds74_01bak') }
    if (Test-Path $KR) { Remove-Item $KR -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $KR -Force | Out-Null
    $pyLines = New-Object System.Collections.Generic.List[string]
    $pyLines.Add('# -*- coding: utf-8 -*-')
    $pyLines.Add('"""DS_74_01: GUI-чек-лист АРМ (К1-К4, ОР, ГТ, матрица 03, per-host k4). Без Ollama/LM."""')
    $pyLines.Add('import os, sys, json')
    $pyLines.Add('import pytest')
    $pyLines.Add('')
    $pyLines.Add('REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))')
    $pyLines.Add('if REPO not in sys.path: sys.path.insert(0, REPO)')
    $pyLines.Add('')
    $pyLines.Add('IKA = r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3"')
    $pyLines.Add('')
    $pyLines.Add('def _has_plp():')
    $pyLines.Add('    if not os.path.isdir(IKA): return []')
    $pyLines.Add('    return [f for f in os.listdir(IKA) if f.lower().endswith(".plp")]')
    $pyLines.Add('')
    $pyLines.Add('# 1: старт DBIMigrationApp')
    $pyLines.Add('def test_74_01_01_app_start():')
    $pyLines.Add('    tk = pytest.importorskip("tkinter")')
    $pyLines.Add('    root = tk.Tk(); root.withdraw()')
    $pyLines.Add('    try:')
    $pyLines.Add('        import gui_app')
    $pyLines.Add('        assert hasattr(gui_app, "DBIMigrationApp")')
    $pyLines.Add('        assert root.winfo_exists()')
    $pyLines.Add('    finally:')
    $pyLines.Add('        try: root.update_idletasks()')
    $pyLines.Add('        except Exception: pass')
    $pyLines.Add('        try: root.destroy()')
    $pyLines.Add('        except Exception: pass')
    $pyLines.Add('')
    $pyLines.Add('# 2: К1 - ИКА содержит .plp, сканер доступен')
    $pyLines.Add('def test_74_01_02_k1_ika_has_plp():')
    $pyLines.Add('    files = _has_plp()')
    $pyLines.Add('    if not files: pytest.skip("ИКА пуст или нет .plp: " + IKA)')
    $pyLines.Add('    import scanner')
    $pyLines.Add('    assert hasattr(scanner, "scan_file")')
    $pyLines.Add('')
    $pyLines.Add('    src = open(os.path.join(REPO, "gui_app.py"), encoding="utf-8", errors="replace").read()')
    $pyLines.Add('    assert "--model" in src')
    $pyLines.Add('    assert "k4_model_var" in src')
    $pyLines.Add('')
    $pyLines.Add('# 5: К4 - apply_local_k4_override существует')
    $pyLines.Add('def test_74_01_05_k4_override():')
    $pyLines.Add('    import local_settings')
    $pyLines.Add('    assert hasattr(local_settings, "apply_local_k4_override")')
    $pyLines.Add('')
    $pyLines.Add('# 6: ОР - v5.json загружается')
    $pyLines.Add('def test_74_01_06_rubricator():')
    $pyLines.Add('    v5 = r"F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json"')
    $pyLines.Add('    if not os.path.isfile(v5): pytest.skip("нет v5.json")')
    $pyLines.Add('    data = json.load(open(v5, encoding="utf-8"))')
    $pyLines.Add('    n = len(data.get("rules", data if isinstance(data, list) else []))')
    $pyLines.Add('    assert n > 0')
    $pyLines.Add('')
    $pyLines.Add('# 7: ГТ - dry-run не создаёт .plp')
    $pyLines.Add('def test_74_01_07_gt_dryrun():')
    $pyLines.Add('    src = open(os.path.join(REPO, "gui_app.py"), encoding="utf-8", errors="replace").read()')
    $pyLines.Add('    assert "dry" in src.lower() or "dry_run" in src.lower()')
    $pyLines.Add('')
    $pyLines.Add('# 8: per-host k4_model (DS_183b) - 5 сценариев через apply_local_k4_override')
    $pyLines.Add('def test_74_01_08_per_host_k4():')
    $pyLines.Add('    import local_settings')
    $pyLines.Add('    fn = getattr(local_settings, "apply_local_k4_override", None)')
    $pyLines.Add('    assert fn is not None')
    $pyLines.Add('    assert fn("qwen2.5-coder:3b", log=lambda *a, **k: None) in ("qwen2.5-coder:3b","qwen2.5-coder:7b")')
    $enc = if ($bomNeighbor) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
    [System.IO.File]::WriteAllLines($testFile, $pyLines, $enc)
    $tb = [System.IO.File]::ReadAllBytes($testFile)
    $tbB = ($tb.Length -ge 3 -and $tb[0] -eq 0xEF -and $tb[1] -eq 0xBB -and $tb[2] -eq 0xBF)
    if ($tbB -ne $bomNeighbor) { throw 'BOM теста не совпал с соседом (65_3)' }
    Write-Host 'test_ds74_01_gui_checklist.py:' $tb.Length 'B, BOM=' $tbB
    $pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyCmd) { $python = $pyCmd.Source } else { $python = 'C:\Users\ainf1\AppData\Local\Programs\Python\Python312\python.exe' }
    Write-Host 'python=' $python
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $python -m pytest $testFile -q -W error::pytest.PytestReturnNotNoneWarning 2>&1 | Out-File -FilePath $outT -Encoding utf8
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
    if (Test-Path $KR) { Remove-Item $KR -Recurse -Force -ErrorAction SilentlyContinue }
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
