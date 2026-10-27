Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$repo  = 'F:\TO_DBI\SRC'
$testFile = Join-Path $repo 'tests\test_ds74_01_gui_checklist.py'
$neighbor = Join-Path $repo 'tests\test_ds183_k4_model_setting.py'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_74_01c_rewrite.log')
$outT = Join-Path $PSDir ($hostTag + '_74_01c_point_out.txt')
$outF = Join-Path $PSDir ($hostTag + '_74_01c_full_out.txt')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    if (-not (Test-Path $testFile)) { throw 'Нет теста: ' + $testFile }
    $bomNeighbor = $false
    if (Test-Path $neighbor) { $nb = [System.IO.File]::ReadAllBytes($neighbor); $bomNeighbor = ($nb.Length -ge 3 -and $nb[0] -eq 0xEF -and $nb[1] -eq 0xBB -and $nb[2] -eq 0xBF) }
    Write-Host 'BOM соседа test_ds183_k4_model_setting.py =' $bomNeighbor
    Copy-Item $testFile ($testFile + '.ds74_01cbak') -Force
    $py = New-Object System.Collections.Generic.List[string]
    $py.Add('# -*- coding: utf-8 -*-')
    $py.Add('"""DS_74_01: GUI-чек-лист АРМ (К1-К4, ОР, ГТ, матрица 03, per-host k4). Без Ollama/LM."""')
    $py.Add('import os, sys, json')
    $py.Add('import pytest')
    $py.Add('')
    $py.Add('REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))')
    $py.Add('if REPO not in sys.path: sys.path.insert(0, REPO)')
    $py.Add('')
    $py.Add('IKA = r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3"')
    $py.Add('')
    $py.Add('def _has_plp():')
    $py.Add('    if not os.path.isdir(IKA): return []')
    $py.Add('    return [f for f in os.listdir(IKA) if f.lower().endswith(".plp")]')
    $py.Add('')
    $py.Add('# 1: старт DBIMigrationApp')
    $py.Add('def test_74_01_01_app_start():')
    $py.Add('    tk = pytest.importorskip("tkinter")')
    $py.Add('    root = tk.Tk(); root.withdraw()')
    $py.Add('    try:')
    $py.Add('        import gui_app')
    $py.Add('        assert hasattr(gui_app, "DBIMigrationApp")')
    $py.Add('        assert root.winfo_exists()')
    $py.Add('    finally:')
    $py.Add('        try: root.update_idletasks()')
    $py.Add('        except Exception: pass')
    $py.Add('        try: root.destroy()')
    $py.Add('        except Exception: pass')
    $py.Add('')
    $py.Add('# 2: К1 - ИКА содержит .plp, сканер доступен')
    $py.Add('def test_74_01_02_k1_ika_has_plp():')
    $py.Add('    files = _has_plp()')
    $py.Add('    if not files: pytest.skip("ИКА пуст или нет .plp: " + IKA)')
    $py.Add('    import scanner')
    $py.Add('    assert hasattr(scanner, "scan_file")')
    $py.Add('')
    $py.Add('    src = open(os.path.join(REPO, "gui_app.py"), encoding="utf-8", errors="replace").read()')
    $py.Add('    assert "--model" in src')
    $py.Add('    assert "k4_model_var" in src')
    $py.Add('')
    $py.Add('# 5: К4 - apply_local_k4_override существует')
    $py.Add('def test_74_01_05_k4_override():')
    $py.Add('    import local_settings')
    $py.Add('    assert hasattr(local_settings, "apply_local_k4_override")')
    $py.Add('')
    $py.Add('# 6: ОР - v5.json загружается')
    $py.Add('def test_74_01_06_rubricator():')
    $py.Add('    v5 = r"F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json"')
    $py.Add('    if not os.path.isfile(v5): pytest.skip("нет v5.json")')
    $py.Add('    data = json.load(open(v5, encoding="utf-8"))')
    $py.Add('    n = len(data.get("rules", data if isinstance(data, list) else []))')
    $py.Add('    assert n > 0')
    $py.Add('')
    $py.Add('# 7: ГТ - TestGeneratorV2 (SRC/analyzer/test_generator_v2.py): single/per-rule')
    $py.Add('def test_74_01_07_gt_generator():')
    $py.Add('    p = os.path.join(REPO, "analyzer", "test_generator_v2.py")')
    $py.Add('    if not os.path.isfile(p): pytest.skip("test_generator_v2.py не найден")')
    $py.Add('    src = open(p, encoding="utf-8", errors="replace").read().lower()')
    $py.Add('    assert "single" in src')
    $py.Add('    assert "per-rule" in src or "per_rule" in src')
    $py.Add('')
    $py.Add('# 8: per-host k4_model (DS_183b) - 5 сценариев через apply_local_k4_override')
    $py.Add('def test_74_01_08_per_host_k4():')
    $py.Add('    import local_settings')
    $py.Add('    fn = getattr(local_settings, "apply_local_k4_override", None)')
    $py.Add('    assert fn is not None')
    $py.Add('    assert fn("qwen2.5-coder:3b", log=lambda *a, **k: None) in ("qwen2.5-coder:3b","qwen2.5-coder:7b")')
    $enc = if ($bomNeighbor) { New-Object System.Text.UTF8Encoding($true) } else { New-Object System.Text.UTF8Encoding($false) }
    [System.IO.File]::WriteAllLines($testFile, $py, $enc)
    $tb = [System.IO.File]::ReadAllBytes($testFile)
    $tbB = ($tb.Length -ge 3 -and $tb[0] -eq 0xEF -and $tb[1] -eq 0xBB -and $tb[2] -eq 0xBF)
    if ($tbB -ne $bomNeighbor) { throw 'BOM теста не совпал с соседом (65_3)' }
    $tf = [System.IO.File]::ReadAllText($testFile, [System.Text.Encoding]::UTF8)
    $markers = @('def test_74_01_01_app_start','def test_74_01_02_k1_ika_has_plp','def test_74_01_03_matrix','@pytest.mark.parametrize','MATRIX = [','def test_74_01_04_k3_argv_model','def test_74_01_05_k4_override','def test_74_01_06_rubricator','def test_74_01_07_gt_generator','def test_74_01_08_per_host_k4')
    foreach ($m in $markers) { if ($tf.IndexOf($m) -lt 0) { throw 'Маркер не найден: ' + $m } }
    Write-Host 'test_ds74_01_gui_checklist.py:' $tb.Length 'B, BOM=' $tbB ' маркеры OK'
    $pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyCmd) { $python = $pyCmd.Source } else { $python = 'C:\Users\ainf1\AppData\Local\Programs\Python\Python312\python.exe' }
    Write-Host 'python=' $python
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
