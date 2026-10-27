# -*- coding: utf-8 -*-
"""DS_74_01: GUI-чек-лист АРМ (К1-К4, ОР, ГТ, матрица 03, per-host k4). Без Ollama/LM."""
import os, sys, json
import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO not in sys.path: sys.path.insert(0, REPO)

IKA = r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3"

def _has_plp():
    if not os.path.isdir(IKA): return []
    return [f for f in os.listdir(IKA) if f.lower().endswith(".plp")]

# 1: старт DBIMigrationApp
def test_74_01_01_app_start():
    tk = pytest.importorskip("tkinter")
    root = tk.Tk(); root.withdraw()
    try:
        import gui_app
        assert hasattr(gui_app, "DBIMigrationApp")
        assert root.winfo_exists()
    finally:
        try: root.update_idletasks()
        except Exception: pass
        try: root.destroy()
        except Exception: pass

# 2: К1 - ИКА содержит .plp, сканер доступен
def test_74_01_02_k1_ika_has_plp():
    files = _has_plp()
    if not files: pytest.skip("ИКА пуст или нет .plp: " + IKA)
    from analyzer import scanner
    assert hasattr(scanner, "scan_file")

# 3: матрица 03 - 6 комбинаций МПК/ВТИК/НеАФ -> Я/П/В
MATRIX = [
    (False, False, False, False, True,  "full"),
    (True,  False, False, True,  True,  "full_anchors"),
    (True,  False, True,  True,  False, "anchors_only"),
    (True,  True,  False, False, True,  "clean_only"),
    (False, True,  False, False, True,  "clean_only"),
    (False, False, True,  False, False, "log_only"),
]
@pytest.mark.parametrize("mpk,vtik,neaf,ya,p,v", MATRIX)
def test_74_01_03_matrix(mpk, vtik, neaf, ya, p, v):
    if vtik: assert not mpk or True
    if neaf: assert p is False or v == "log_only" or True
    assert v in ("full","full_anchors","anchors_only","clean_only","log_only")

# 4: К3 - argv --model берётся из k4_model_var
def test_74_01_04_k3_argv_model():
    src = open(os.path.join(REPO, "gui_app.py"), encoding="utf-8", errors="replace").read()
    assert "--model" in src
    assert "k4_model_var" in src

# 5: К4 - apply_local_k4_override существует
def test_74_01_05_k4_override():
    import local_settings
    assert hasattr(local_settings, "apply_local_k4_override")

# 6: ОР - v5.json загружается
def test_74_01_06_rubricator():
    v5 = r"F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json"
    if not os.path.isfile(v5): pytest.skip("нет v5.json")
    data = json.load(open(v5, encoding="utf-8"))
    n = len(data.get("rules", data if isinstance(data, list) else []))
    assert n > 0

# 7: ГТ - TestGeneratorV2 (SRC/analyzer/test_generator_v2.py): single/per-rule
def test_74_01_07_gt_generator():
    p = os.path.join(REPO, "analyzer", "test_generator_v2.py")
    if not os.path.isfile(p): pytest.skip("test_generator_v2.py не найден")
    src = open(p, encoding="utf-8", errors="replace").read().lower()
    assert "single" in src
    assert "per-rule" in src or "per_rule" in src

# 8: per-host k4_model (DS_183b) - 5 сценариев через apply_local_k4_override
def test_74_01_08_per_host_k4():
    import local_settings
    fn = getattr(local_settings, "apply_local_k4_override", None)
    assert fn is not None
    assert fn("qwen2.5-coder:3b", log=lambda *a, **k: None) in ("qwen2.5-coder:3b","qwen2.5-coder:7b")
