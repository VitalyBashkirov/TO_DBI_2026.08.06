"""DS_152-c: К3/К4 — тесты AI-контура (инвариант + _ai_rubricators).

Главная задача чата 43: тест К1-К4 и генерации .plp в зависимости от выбора
рубрикаторов/правил. Этот файл покрывает К3 (send_to_ai) и К4 (receive_from_ai):

- AST-инвариант: К3/К4 НЕ фильтруют напрямую по self.selected_rules.
  Фильтрация правил происходит на этапе К1 (скан), а К3 работает
  с уже отфильтрованными scan_results['issues'].
- Функциональный: _ai_rubricators() возвращает список активных кодов
  рубрикаторов (для шапки AI_REQUEST).
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
    assert GUI.exists(), f"Нет файла: {GUI}"
    return ast.parse(GUI.read_text(encoding="utf-8"))


def _find_func(tree, name):
    """Найти FunctionDef по имени в дереве."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _attr_chain(node):
    """Вернуть 'a.b.c' для Attribute-цепочки, иначе None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _iter_attr_chains(root):
    """Все attr-цепочки в поддереве."""
    for node in ast.walk(root):
        if isinstance(node, ast.Attribute):
            chain = _attr_chain(node)
            if chain:
                yield chain


# ---------------------------------------------------------------------------
# Тест 1: К3 (send_to_ai) — нет прямого self.selected_rules
# ---------------------------------------------------------------------------

def test_ds152c_k3_no_direct_selected_rules_ast():
    """send_to_ai не содержит self.selected_rules напрямую.

    Правила фильтруются на этапе К1 (скан), а не в send_to_ai.
    Активные рубрикаторы передаются через _ai_rubricators() -> write_request(rubs=...).
    """
    tree = _parse_gui()
    func = _find_func(tree, "send_to_ai")
    assert func is not None, "send_to_ai не найден"

    direct_refs = [c for c in _iter_attr_chains(func) if c == "self.selected_rules"]
    assert not direct_refs, (
        "send_to_ai содержит прямое обращение к self.selected_rules: "
        f"{direct_refs}. Фильтрация правил должна быть только в К1 (скан)."
    )


# ---------------------------------------------------------------------------
# Тест 2: К4 (receive_from_ai) — нет прямого self.selected_rules
# ---------------------------------------------------------------------------

def test_ds152c_k4_no_direct_selected_rules_ast():
    """receive_from_ai не содержит self.selected_rules.

    К4 применяет AI_RESPONSE через ai_exchange.process_all_responses(),
    независимо от выбора рубрикаторов. Это инвариант: фиксы применяются
    по line_no + rule_code из ответа, а не по выбранным правилам.
    """
    tree = _parse_gui()
    func = _find_func(tree, "receive_from_ai")
    assert func is not None, "receive_from_ai не найден"

    direct_refs = [c for c in _iter_attr_chains(func) if c == "self.selected_rules"]
    assert not direct_refs, (
        "receive_from_ai содержит прямое обращение к self.selected_rules: "
        f"{direct_refs}. К4 не должен фильтровать по выбранным правилам."
    )


# ---------------------------------------------------------------------------
# Тест 3: _ai_rubricators возвращает только активные коды
# ---------------------------------------------------------------------------

def _make_app_with_rules(rules_dict):
    """Создать DBIMigrationApp без __init__ (без Tk) и задать selected_rules."""
    from gui_app import DBIMigrationApp
    app = object.__new__(DBIMigrationApp)
    app.selected_rules = rules_dict
    return app


def test_ds152c_ai_rubricators_returns_selected():
    """_ai_rubricators() возвращает только коды с var.get() == True."""
    rules = {
        "v53": Mock(get=Mock(return_value=True)),
        "tds20240828": Mock(get=Mock(return_value=False)),
        "plpcheck": Mock(get=Mock(return_value=True)),
        "тклоик20240828": Mock(get=Mock(return_value=False)),
    }
    app = _make_app_with_rules(rules)
    result = app._ai_rubricators()
    assert result == ["v53", "plpcheck"], (
        f"Ожидалось ['v53', 'plpcheck'], получено {result!r}"
    )


# ---------------------------------------------------------------------------
# Тест 4: _ai_rubricators пустой, если ничего не выбрано
# ---------------------------------------------------------------------------

def test_ds152c_ai_rubricators_empty_when_none_selected():
    """_ai_rubricators() возвращает [] если все var.get() == False."""
    rules = {
        "v53": Mock(get=Mock(return_value=False)),
        "tds20240828": Mock(get=Mock(return_value=False)),
        "plpcheck": Mock(get=Mock(return_value=False)),
        "тклоик20240828": Mock(get=Mock(return_value=False)),
    }
    app = _make_app_with_rules(rules)
    result = app._ai_rubricators()
    assert result == [], f"Ожидалось [], получено {result!r}"