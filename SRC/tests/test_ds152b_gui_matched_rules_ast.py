"""DS_152-b: matched_rules — фильтр правил в GUI (К1/К2/Генерация).

Главная задача чата 43: тест К1-К4 и генерации .plp в зависимости от
выбора рубрикаторов/правил. Аудит показал: matched_rules = 0 в тестах.

Покрываем _get_rules_for_selected_files (К1/К2/Генерация):
- маппинг file_code -> префиксы правил (v53/v50, PlpCheck, тдс, тклоик);
- фильтрация all_rules по выбранным файлам;
- объединение по нескольким файлам (sorted set);
- fallback без рубрикатора (возврат кодов файлов).

AST: _run_test_generation использует matched_rules (или sorted_rules).
"""
import ast
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUI = ROOT / "SRC" / "gui_app.py"


# ---------------------------------------------------------------------------
# Вспомогательные
# ---------------------------------------------------------------------------

def _parse_gui():
    return ast.parse(GUI.read_text(encoding="utf-8"))


def _find_func(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _make_app(rules, rubricator_prompts=None):
    """DBIMigrationApp без __init__, с selected_rules и rubricator_prompts."""
    from gui_app import DBIMigrationApp
    app = object.__new__(DBIMigrationApp)
    app.selected_rules = rules
    app.rubricator_prompts = rubricator_prompts
    return app


def _mock_rubricator(all_rules):
    """Mock rubricator_prompts: loaded=True, get_all_rules() -> all_rules."""
    m = Mock()
    m.loaded = True
    m.get_all_rules = Mock(return_value=all_rules)
    return m


# ---------------------------------------------------------------------------
# Тест 1: AST — file_prefixes содержит 5 ключей с правильными префиксами
# ---------------------------------------------------------------------------

def test_ds152b_file_prefixes_mapping_ast():
    """_get_rules_for_selected_files: file_prefixes с 5 ключами и префиксами."""
    tree = _parse_gui()
    func = _find_func(tree, "_get_rules_for_selected_files")
    assert func is not None, "Не найден _get_rules_for_selected_files"

    # Найти Assign с file_prefixes = {...}
    found = False
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "file_prefixes":
                    assert isinstance(node.value, ast.Dict), "file_prefixes должен быть dict"
                    keys = []
                    for k in node.value.keys:
                        if isinstance(k, ast.Constant):
                            keys.append(k.value)
                    assert set(keys) == {"v53", "v50", "PlpCheck",
                                         "тдс20240828", "тклоик20240828"}, \
                        f"Неверные ключи file_prefixes: {keys}"
                    found = True
    assert found, "Не найден file_prefixes в _get_rules_for_selected_files"


# ---------------------------------------------------------------------------
# Тест 2: функциональный — PlpCheck -> только plpcheck.*
# ---------------------------------------------------------------------------

ALL_RULES_5 = [
    {"code": "plpcheck.A"},
    {"code": "plpcheck.B"},
    {"code": "v53.X"},
    {"code": "тдс20240828.Y"},
    {"code": "тклоик20240828.Z"},
]


def test_ds152b_plpcheck_filter():
    """selected_files=['PlpCheck'] -> только plpcheck.*."""
    app = _make_app(
        rules={"PlpCheck": Mock(get=Mock(return_value=True))},
        rubricator_prompts=_mock_rubricator(ALL_RULES_5),
    )
    result = app._get_rules_for_selected_files(["PlpCheck"])
    assert result == ["plpcheck.A", "plpcheck.B"], f"Получено: {result}"


# ---------------------------------------------------------------------------
# Тест 3: функциональный — несколько файлов (объединение)
# ---------------------------------------------------------------------------

def test_ds152b_multiple_files_union():
    """['v53', 'PlpCheck'] -> v53.* + plpcheck.* (sorted)."""
    app = _make_app(rules={}, rubricator_prompts=_mock_rubricator(ALL_RULES_5))
    result = app._get_rules_for_selected_files(["v53", "PlpCheck"])
    assert result == ["plpcheck.A", "plpcheck.B", "v53.X"], f"Получено: {result}"


# ---------------------------------------------------------------------------
# Тест 4: AST — _run_test_generation использует matched_rules
# ---------------------------------------------------------------------------

def test_ds152b_run_test_generation_matched_rules_ast():
    """_run_test_generation содержит переменную matched_rules."""
    tree = _parse_gui()
    func = _find_func(tree, "_run_test_generation")
    assert func is not None, "Не найден _run_test_generation"

    # Найти Assign, где target — matched_rules
    has_matched = False
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "matched_rules":
                    has_matched = True
    assert has_matched, "_run_test_generation не содержит matched_rules"


# ---------------------------------------------------------------------------
# Тест 5: функциональный — fallback без рубрикатора
# ---------------------------------------------------------------------------

def test_ds152b_fallback_no_rubricator():
    """Без рубрикатора метод возвращает коды файлов (не правила)."""
    app = _make_app(rules={}, rubricator_prompts=None)
    result = app._get_rules_for_selected_files(["v53", "PlpCheck"])
    assert result == ["v53", "PlpCheck"], f"Получено: {result}"