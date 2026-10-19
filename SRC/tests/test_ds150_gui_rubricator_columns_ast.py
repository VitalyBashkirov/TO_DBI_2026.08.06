"""DS_150: AST-проверка колонок в таблице "2. Рубрикатор. Выбор корректировок"."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI = ROOT / "SRC" / "gui_app.py"


def _find_call_nodes(tree, method_name):
    """Найти все вызовы метода `self.rules_tree.<method_name>(...)`."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == method_name:
                # Проверяем, что вызывается именно self.rules_tree
                if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "rules_tree":
                    results.append(node)
    return results


def test_ds150_gui_ast_parses():
    """gui_app.py должен успешно парситься."""
    src = GUI.read_text(encoding="utf-8")
    ast.parse(src)


def test_ds150_rubricator_column_width_126():
    """Колонка '#0' (Рубрикатор) имеет width=126, minwidth=126."""
    tree = ast.parse(GUI.read_text(encoding="utf-8"))
    cols = _find_call_nodes(tree, "column")
    for call in cols:
        if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == "#0":
            kwargs = {kw.arg: kw.value for kw in call.keywords}
            assert "width" in kwargs and isinstance(kwargs["width"], ast.Constant)
            assert kwargs["width"].value == 126, f"Ожидалось width=126, получено {kwargs['width'].value}"
            assert "minwidth" in kwargs and isinstance(kwargs["minwidth"], ast.Constant)
            assert kwargs["minwidth"].value == 126, f"Ожидалось minwidth=126, получено {kwargs['minwidth'].value}"
            return
    assert False, "Не найдена колонка '#0' с правильными параметрами"


def test_ds150_code_column_width_164():
    """Колонка 'code' (Код файла) имеет width=164, minwidth=164."""
    tree = ast.parse(GUI.read_text(encoding="utf-8"))
    cols = _find_call_nodes(tree, "column")
    for call in cols:
        if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == "code":
            kwargs = {kw.arg: kw.value for kw in call.keywords}
            assert "width" in kwargs and isinstance(kwargs["width"], ast.Constant)
            assert kwargs["width"].value == 164, f"Ожидалось width=164, получено {kwargs['width'].value}"
            assert "minwidth" in kwargs and isinstance(kwargs["minwidth"], ast.Constant)
            assert kwargs["minwidth"].value == 164, f"Ожидалось minwidth=164, получено {kwargs['minwidth'].value}"
            return
    assert False, "Не найдена колонка 'code' с правильными параметрами"


def test_ds150_code_heading_renamed():
    """Заголовок колонки 'code' — 'Код файла/правила'."""
    tree = ast.parse(GUI.read_text(encoding="utf-8"))
    headings = _find_call_nodes(tree, "heading")
    for call in headings:
        if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == "code":
            kwargs = {kw.arg: kw.value for kw in call.keywords}
            assert "text" in kwargs and isinstance(kwargs["text"], ast.Constant)
            assert kwargs["text"].value == "Код файла/правила", \
                f"Ожидалось text='Код файла/правила', получено '{kwargs['text'].value}'"
            return
    assert False, "Не найден heading('code', ...) с правильными параметрами"