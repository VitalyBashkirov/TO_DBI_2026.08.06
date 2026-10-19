"""DS_152-a: CLI-генератор gen_test_plp.py -- флаг --rules (фильтр по правилам).

Главная задача чата 43: тест "Генерация тестовых .plp" в зависимости от
выбора рубрикаторов/правил. Аудит показал: rules_arg = 0 покрытия в тестах,
хотя --rules -- прямой фильтр по правилам.

Покрываем:
- _parse_csv: "", "a", "a,b", "a, b, ,c" (пустые отбрасываются);
- --rules <csv>: rules_total == len(csv), в логе ровно эти коды;
- --rules с несуществующим кодом: WARN + codes не попадают в selected;
- --rules "" (пустая строка): rules_arg = None, все правила источника.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "tools" / "gen_test_plp.py"
RUBRICATOR = ROOT / "DATA" / "Рубрикатор v5"


# ---------------------------------------------------------------------------
# Вспомогательные
# ---------------------------------------------------------------------------

def _run_gen(out_dir: Path, source: str, extra: list[str]) -> subprocess.CompletedProcess:
    """Запустить gen_test_plp.py с dry-run и вернуть CompletedProcess."""
    cmd = [
        sys.executable, str(GEN),
        "-s", source,
        "-o", str(out_dir),
        "--dry-run",
    ] + extra
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), timeout=60,
    )


def _find_log(out_dir: Path) -> Path:
    """Найти последний gen_*.log в out_dir."""
    logs = sorted(out_dir.glob("gen_*.log"))
    assert logs, f"Не найдено gen_*.log в {out_dir}"
    return logs[-1]


# ---------------------------------------------------------------------------
# Тест 1: _parse_csv (AST + прямое поведение)
# ---------------------------------------------------------------------------

def test_ds152a_parse_csv_behavior():
    """_parse_csv: пусто -> None, 'a' -> [a], 'a,b' -> [a,b], пустые отброшены."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_test_plp", str(GEN))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert mod._parse_csv(None) is None
    assert mod._parse_csv("") is None
    assert mod._parse_csv("   ") is None
    assert mod._parse_csv("a") == ["a"]
    assert mod._parse_csv("a,b") == ["a", "b"]
    assert mod._parse_csv(" a , b , , c ") == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# Тест 2: --rules с двумя кодами -- ровно 2 в selected
# ---------------------------------------------------------------------------

def test_ds152a_rules_two_codes(tmp_path):
    """--rules 'plpcheck.BAD_PREFIX,plpcheck.NOT_MENTIONED' -> rules_total=2."""
    out = tmp_path / "out"
    r = _run_gen(out, "PlpCheck", [
        "--rules", "plpcheck.BAD_PREFIX,plpcheck.NOT_MENTIONED",
    ])
    assert r.returncode == 0, f"gen упал: rc={r.returncode}, stderr={r.stderr}"

    log = _find_log(out)
    text = log.read_text(encoding="utf-8")
    assert "rules_arg   : ['plpcheck.BAD_PREFIX', 'plpcheck.NOT_MENTIONED']" in text
    assert "rules_total : 2" in text
    # в списке selected именно эти два
    assert "  [  1] plpcheck.BAD_PREFIX" in text
    assert "  [  2] plpcheck.NOT_MENTIONED" in text
    # других кодов нет
    assert "  [  3]" not in text


# ---------------------------------------------------------------------------
# Тест 3: --rules с несуществующим кодом -- WARN + отфильтрован
# ---------------------------------------------------------------------------

def test_ds152a_rules_missing_code_warn(tmp_path):
    """--rules '<valid>,<nonexistent>' -> rules_total=1 + WARN о missing."""
    out = tmp_path / "out"
    r = _run_gen(out, "PlpCheck", [
        "--rules", "plpcheck.BAD_PREFIX,plpcheck.DOES_NOT_EXIST_XYZ",
    ])
    assert r.returncode == 0, f"gen упал: rc={r.returncode}, stderr={r.stderr}"

    log = _find_log(out)
    text = log.read_text(encoding="utf-8")
    assert "rules_total : 1" in text
    assert "plpcheck.DOES_NOT_EXIST_XYZ" in text
    assert "[WARN] В v5.json нет правил (пропущено): 1" in text


# ---------------------------------------------------------------------------
# Тест 4: --rules "" (пусто) -- все правила источника
# ---------------------------------------------------------------------------

def test_ds152a_rules_empty_means_all(tmp_path):
    """--rules '' (пусто) -> rules_arg None, rules_total = все правила PlpCheck."""
    out = tmp_path / "out"
    r = _run_gen(out, "PlpCheck", ["--rules", ""])
    assert r.returncode == 0, f"gen упал: rc={r.returncode}, stderr={r.stderr}"

    log = _find_log(out)
    text = log.read_text(encoding="utf-8")
    assert "rules_arg   : None" in text
    # PlpCheck: 152 правила (факт из аудита DS_144d-a: source plpcheck=152)
    assert "rules_total : 152" in text