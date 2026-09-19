# -*- coding: utf-8 -*-
"""
DS_054 — AI-fallback: файловый обмен АРМ <-> AI.

АРМ НЕ вызывает AI напрямую. Всё общение идёт через файлы в EXCHANGE\\:

- «В AI»: АРМ формирует файл-запрос AI_REQUEST_<source>_<ts>.md в AI_IN
  с перечнем проблем (строка, код правила, уровень, текущий код, контекст).
- Пользователь/скрипт отправляет запрос в AI и кладёт файл-ответ
  AI_RESPONSE_<source>_<ts>.md в AI_OUT.
- «От AI»: АРМ читает ответ, применяет исправления по порогу confidence,
  архивирует запрос/ответ и возвращает сводку для журнала/КР.

Пороги confidence (по заданию DS_054):
  >= 0.8            — применить автоматически;
  0.5 .. < 0.8      — применить с пометкой «средняя уверенность»;
  <  0.5            — НЕ применять, needs_manual.

Модуль не зависит от tkinter — все функции можно тестировать отдельно.
"""
from __future__ import annotations

import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


# ----------------------------------------------------------------------
# Каталог обмена
# ----------------------------------------------------------------------
DIRS = ['AI_IN', 'AI_OUT', 'AI_IN_PROCESSED', 'AI_OUT_PROCESSED']

# Имена файлов: AI_REQUEST_<source>_<YYYYMMDD>_<HHMMSS>.md
REQUEST_PREFIX = 'AI_REQUEST_'
RESPONSE_PREFIX = 'AI_RESPONSE_'

# Флаги детерминированного фикса в каноническом порядке (DS_053).
FLAG_ORDER = ['regex', 'hybrid', 'ai_fallback', 'ignore', 'backup', 'other']

# Расшифровка флагов — точно как подписи чекбоксов на форме GUI.
FLAG_DESCRIPTIONS = {
    'regex': 'чистые regex-правила',
    'hybrid': 'полудетерм. с algorithmic_hint',
    'ai_fallback': 'помечать needs_ai_fix',
    'ignore': 'не автофиксить, только лог',
    'backup': 'резервные regex-правила',
    'other': 'hybrid без algorithmic_hint',
}

# Порог автоприменения и нижней границы «средней уверенности».
CONF_AUTO = 0.8
CONF_MEDIUM = 0.5

# Маркер удаления строки из ответа AI.
DELETED_MARKER = '-- (удалено)'

# Имя файла-ответа: AI_RESPONSE_<source>_<date>_<time>.(md|json)
_RE_RESPONSE = re.compile(
    r'^AI_RESPONSE_(?P<source>.+)_(?P<date>\d{8})_(?P<time>\d{6})$',
    re.IGNORECASE,
)


def base_dir() -> Path:
    """Корень EXCHANGE (родитель SRC)."""
    return Path(__file__).resolve().parent.parent / 'EXCHANGE'


def ensure_dirs(base: Optional[Path] = None) -> Dict[str, Path]:
    """Создать (если нужно) 4 каталога обмена и вернуть их пути."""
    root = Path(base) if base else base_dir()
    out: Dict[str, Path] = {}
    for name in DIRS:
        p = root / name
        p.mkdir(parents=True, exist_ok=True)
        out[name] = p
    return out


# ----------------------------------------------------------------------
# Флаги
# ----------------------------------------------------------------------
def flags_line(flags: Dict[str, bool]) -> str:
    """Строка вида: regex=V, hybrid=V, ai_fallback=x, ... (канонический порядок)."""
    parts = []
    for name in FLAG_ORDER:
        on = bool(flags.get(name, False)) if flags else False
        parts.append(f"{name}={'V' if on else 'x'}")
    return ', '.join(parts)


# ----------------------------------------------------------------------
# Формирование файла-запроса
# ----------------------------------------------------------------------
def _read_lines(path: Path) -> Tuple[List[str], str, str]:
    """Прочитать файл с автоопределением кодировки.

    Возвращает (lines_без_переводов, encoding, newline).
    """
    try:
        from analyzer.scanner import read_file_with_encoding
        text, enc = read_file_with_encoding(Path(path))
    except Exception:
        text, enc = Path(path).read_text(encoding='utf-8', errors='replace'), 'utf-8'
    newline = '\r\n' if '\r\n' in text else '\n'
    return text.splitlines(), enc, newline


def _context_block(lines: List[str], line_number: int, radius: int = 5) -> str:
    """Фрагмент кода: radius строк до/после line_number (1-based)."""
    idx = line_number - 1
    start = max(0, idx - radius)
    end = min(len(lines), idx + radius + 1)
    out = []
    for i in range(start, end):
        marker = '>' if i == idx else ' '
        out.append(f"{marker} {i + 1:5d} | {lines[i]}")
    return '\n'.join(out)


def build_request_text(source_path: Path, issues: List, flags: Dict[str, bool],
                       rubricators: Optional[List[str]] = None,
                       severity_fn: Optional[Callable[[str], str]] = None) -> str:
    """Сформировать текст файла-запроса (Markdown + блок с форматом ответа).

    issues — объекты с атрибутами line_number, issue_type, description,
    original_code (или dict с теми же ключами).
    """
    source_path = Path(source_path)
    lines, _enc, _nl = _read_lines(source_path)

    def _attr(it, name, default=''):
        if isinstance(it, dict):
            return it.get(name, default)
        return getattr(it, name, default)

    def _level(issue_type: str) -> str:
        if severity_fn:
            try:
                sev = severity_fn(issue_type)
                return 'ERROR' if 'ERROR' in str(sev).upper() else 'WARNING'
            except Exception:
                return 'WARNING'
        return 'WARNING'

    rubs = ', '.join(rubricators) if rubricators else '—'
    now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    out: List[str] = []
    out.append(f"# AI-запрос: {source_path.stem}")
    out.append("")
    out.append("## Метаданные")
    out.append(f"- Источник: {source_path}")
    out.append(f"- Дата: {now}")
    out.append(f"- Рубрикаторы: {rubs}")
    out.append(f"- Флаги: {flags_line(flags)}")
    out.append("")
    out.append("## Проблемы для AI")
    out.append("")

    for i, it in enumerate(issues, 1):
        ln = int(_attr(it, 'line_number', 0) or 0)
        rule = _attr(it, 'issue_type', '')
        desc = _attr(it, 'description', '')
        code = _attr(it, 'original_code', '') or (
            lines[ln - 1] if 0 < ln <= len(lines) else '')
        out.append(f"### Проблема {i}")
        out.append(f"- Строка: {ln}")
        out.append(f"- Код правила: {rule}")
        out.append(f"- Уровень: {_level(rule)}")
        out.append(f"- Описание: {desc}")
        out.append("- Текущий код:")
        out.append("```")
        out.append(str(code))
        out.append("```")
        out.append("- Контекст (5 строк до/после):")
        out.append("```")
        out.append(_context_block(lines, ln))
        out.append("```")
        out.append("")

    out.append("## Вопрос к AI")
    out.append("")
    out.append("Для каждой проблемы предложи исправление. Ответ оформи как JSON-массив:")
    out.append("")
    out.append("```json")
    out.append("[")
    out.append("  {")
    out.append("    \"id\": <номер>,")
    out.append("    \"line\": <номер>,")
    out.append("    \"before\": \"<исходный код строки>\",")
    out.append("    \"after\": \"<исправленный код или null>\",")
    out.append("    \"reason\": \"<обоснование, 1-2 предложения>\",")
    out.append("    \"confidence\": <0.0-1.0>")
    out.append("  }")
    out.append("]")
    out.append("```")
    out.append("")
    out.append("**Требования:**")
    out.append("- Роль: эксперт по миграции PL/SQL → PostgreSQL (DBI) и стандартам ЦФТ.")
    out.append("- Не меняй ничего, кроме указанной строки.")
    out.append("- Сохраняй отступы и комментарии.")
    out.append("- Если предлагаешь удалить строку — `after = \"-- (удалено)\"`.")
    out.append("- Если не уверен — `confidence < 0.5` и `reason = \"needs_manual: <почему>\"`.")
    out.append("")
    return '\n'.join(out)


def write_request(source_path: Path, issues: List, flags: Dict[str, bool],
                  rubricators: Optional[List[str]] = None,
                  severity_fn: Optional[Callable[[str], str]] = None,
                  base: Optional[Path] = None,
                  timestamp: Optional[str] = None) -> Path:
    """Записать файл-запрос в AI_IN. Вернуть путь к нему."""
    dirs = ensure_dirs(base)
    source_path = Path(source_path)
    ts = timestamp or datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = f"{REQUEST_PREFIX}{source_path.stem}_{ts}.md"
    path = dirs['AI_IN'] / fname
    text = build_request_text(source_path, issues, flags, rubricators, severity_fn)
    # CRLF для файлов обмена (см. AGENTS.md).
    path.write_text(text.replace('\r\n', '\n').replace('\n', '\r\n'),
                    encoding='utf-8', newline='')
    return path


# ----------------------------------------------------------------------
# Парсинг файла-ответа
# ----------------------------------------------------------------------
def extract_json_array(text: str) -> List[dict]:
    """Извлечь JSON-массив исправлений из Markdown/чистого JSON.

    Ищем блок ```json ... ```; если не найден — первый вложенный [...] в тексте.
    """
    if not text:
        return []
    # 1) fenced ```json ... ```
    m = re.search(r'```json\s*(.*?)```', text, re.IGNORECASE | re.DOTALL)
    candidate = m.group(1) if m else None
    if candidate is None:
        # 2) fenced без языка
        m2 = re.search(r'```\s*(\[.*?\])\s*```', text, re.DOTALL)
        candidate = m2.group(1) if m2 else None
    if candidate is None:
        # 3) первый сбалансированный [...] в тексте
        candidate = _first_json_array(text)
    if not candidate:
        return []
    data = _loads_lenient(candidate)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []
    return [d for d in data if isinstance(d, dict)]


def _first_json_array(text: str) -> Optional[str]:
    start = text.find('[')
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _loads_lenient(candidate: str):
    """Разобрать JSON, при неудаче — убрать висячие запятые."""
    candidate = candidate.strip()
    try:
        return json.loads(candidate)
    except Exception:
        cleaned = re.sub(r',(\s*[}\]])', r'\1', candidate)
        try:
            return json.loads(cleaned)
        except Exception:
            return None


# ----------------------------------------------------------------------
# Применение исправлений
# ----------------------------------------------------------------------
def classify_fix(fix: dict) -> str:
    """Классифицировать исправление по confidence/reason.

    Возвращает 'auto' | 'medium' | 'manual' | 'noop'.
    """
    reason = str(fix.get('reason', '') or '')
    if reason.strip().lower().startswith('needs_manual'):
        return 'manual'
    try:
        conf = float(fix.get('confidence', 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    after = fix.get('after', None)
    if after is None or str(after).strip() == '':
        # AI не предложил замену.
        return 'manual' if conf < CONF_MEDIUM else 'noop'
    if conf < CONF_MEDIUM:
        return 'manual'
    if conf >= CONF_AUTO:
        return 'auto'
    return 'medium'


def apply_fixes(file_path: Path, fixes: List[dict]) -> Dict[str, object]:
    """Применить исправления к файлу по порогам confidence.

    Возвращает сводку: applied_auto, applied_medium, needs_manual, skipped,
    changes (список деталей).
    Сортировка по строке снизу вверх сохраняет номера строк.
    """
    file_path = Path(file_path)
    lines, enc, newline = _read_lines(file_path)
    stats = {'applied_auto': 0, 'applied_medium': 0, 'needs_manual': 0,
             'skipped': 0, 'changes': []}

    # Нормализуем номера строк и сортируем по убыванию, чтобы замены
    # не сдвигали индексы нижних строк.
    prepared = []
    for fx in fixes:
        try:
            ln = int(fx.get('line', 0) or 0)
        except (TypeError, ValueError):
            ln = 0
        prepared.append((ln, fx))
    prepared.sort(key=lambda p: p[0], reverse=True)

    for ln, fx in prepared:
        kind = classify_fix(fx)
        detail = {'line': ln, 'kind': kind,
                  'confidence': fx.get('confidence'),
                  'reason': fx.get('reason', '')}
        if kind == 'manual':
            stats['needs_manual'] += 1
            stats['changes'].append(detail)
            continue
        if kind == 'noop':
            stats['skipped'] += 1
            stats['changes'].append(detail)
            continue
        if ln <= 0 or ln > len(lines):
            stats['skipped'] += 1
            detail['kind'] = 'skipped'
            detail['error'] = 'line out of range'
            stats['changes'].append(detail)
            continue

        old = lines[ln - 1]
        before = fx.get('before')
        # Проверка соответствия исходной строки (нечувствительно к отступам).
        if before not in (None, '') and str(before).strip() != old.strip():
            stats['skipped'] += 1
            detail['kind'] = 'skipped'
            detail['error'] = 'before mismatch'
            stats['changes'].append(detail)
            continue

        after = str(fx.get('after'))
        leading = old[:len(old) - len(old.lstrip())]
        if after.strip() == DELETED_MARKER:
            new_line = leading + DELETED_MARKER
        else:
            # Сохраняем отступ оригинала, убираем ведущие пробелы из after.
            new_line = leading + str(after).lstrip()
        lines[ln - 1] = new_line
        if kind == 'auto':
            stats['applied_auto'] += 1
        else:
            stats['applied_medium'] += 1
        detail['after'] = new_line
        stats['changes'].append(detail)

    # Запись только если были применения.
    if stats['applied_auto'] or stats['applied_medium']:
        content = newline.join(lines)
        # Сохраняем финальный перевод строки, если он был в оригинале.
        try:
            raw = file_path.read_bytes()
            if raw.endswith(b'\r\n') or raw.endswith(b'\n'):
                content += newline
        except Exception:
            content += newline
        enc_out = enc if enc and 'replace' not in enc else 'utf-8'
        file_path.write_text(content, encoding=enc_out, newline='')
    return stats


# ----------------------------------------------------------------------
# Обработка файла-ответа
# ----------------------------------------------------------------------
def _find_request_for_response(resp_name: str, dirs: Dict[str, Path]) -> Optional[Path]:
    """Найти файл-запрос, соответствующий ответу, по <source>_<date>_<time>."""
    m = _RE_RESPONSE.match(Path(resp_name).stem)
    if not m:
        return None
    tail = f"{m.group('source')}_{m.group('date')}_{m.group('time')}"
    req_name = f"{REQUEST_PREFIX}{tail}.md"
    for cat in ('AI_IN', 'AI_IN_PROCESSED'):
        cand = dirs[cat] / req_name
        if cand.exists():
            return cand
    return None


def _source_from_request(req_path: Path) -> Optional[Path]:
    """Достать путь источника из блока «Метаданные» файла-запроса."""
    try:
        text = req_path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return None
    m = re.search(r'^-\s*Источник:\s*(.+)$', text, re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).strip()
    return Path(raw) if raw else None


def process_response(response_path: Path, base: Optional[Path] = None,
                     backup: bool = True) -> Dict[str, object]:
    """Обработать один файл-ответ: применить исправления, заархивировать.

    Возвращает сводку для журнала/КР.
    """
    response_path = Path(response_path)
    dirs = ensure_dirs(base)
    result: Dict[str, object] = {
        'response': str(response_path),
        'request': None, 'source': None,
        'applied_auto': 0, 'applied_medium': 0, 'needs_manual': 0, 'skipped': 0,
        'status': 'ok', 'error': None, 'changes': [],
    }

    text = response_path.read_text(encoding='utf-8', errors='replace')
    fixes = extract_json_array(text)
    if not fixes:
        result['status'] = 'no_fixes'
        result['error'] = 'В ответе не найден JSON-массив исправлений'
        return result

    req_path = _find_request_for_response(response_path.name, dirs)
    if req_path:
        result['request'] = str(req_path)
        source = _source_from_request(req_path)
    else:
        # Путь источника может быть указан прямо в ответе.
        m = re.search(r'^-\s*Источник:\s*(.+)$', text, re.MULTILINE)
        source = Path(m.group(1).strip()) if m else None

    if not source or not Path(source).exists():
        result['status'] = 'no_source'
        result['error'] = f'Не определён источник для ответа: {response_path.name}'
        _archive(response_path, dirs['AI_OUT_PROCESSED'])
        return result

    result['source'] = str(source)
    if backup:
        try:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy2(source, source.with_name(f"{source.stem}_{ts}_preai{source.suffix}"))
        except Exception:
            pass

    stats = apply_fixes(Path(source), fixes)
    result['applied_auto'] = stats['applied_auto']
    result['applied_medium'] = stats['applied_medium']
    result['needs_manual'] = stats['needs_manual']
    result['skipped'] = stats['skipped']
    result['changes'] = stats['changes']

    _archive(response_path, dirs['AI_OUT_PROCESSED'])
    if req_path and Path(req_path).exists():
        _archive(Path(req_path), dirs['AI_IN_PROCESSED'])
    return result


def process_all_responses(base: Optional[Path] = None,
                          backup: bool = True) -> List[Dict[str, object]]:
    """Обработать все файлы-ответы в AI_OUT (по возрастанию имён)."""
    dirs = ensure_dirs(base)
    out_dir = dirs['AI_OUT']
    files = sorted(list(out_dir.glob(f"{RESPONSE_PREFIX}*.md")) +
                   list(out_dir.glob(f"{RESPONSE_PREFIX}*.json")))
    results = []
    for f in files:
        results.append(process_response(f, base=base, backup=backup))
    return results


def _archive(src: Path, dst_dir: Path) -> None:
    """Переместить файл в архив (не перезаписывать — добавить суффикс)."""
    src = Path(src)
    dst_dir = Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    target = dst_dir / src.name
    if target.exists():
        ts = datetime.now().strftime('%H%M%S')
        target = dst_dir / f"{src.stem}_{ts}{src.suffix}"
    shutil.move(str(src), str(target))


# ----------------------------------------------------------------------
# Человекочитаемая сводка для журнала АРМ
# ----------------------------------------------------------------------
def summarize(results: List[Dict[str, object]]) -> List[str]:
    """Строки сводки для журнала (журнал АРМ / КР)."""
    lines: List[str] = []
    tot = {'auto': 0, 'med': 0, 'man': 0, 'skip': 0}
    for r in results:
        nm = Path(r.get('response', '?')).name
        st = r.get('status', 'ok')
        if st != 'ok':
            lines.append(f"  [!] {nm}: {st} — {r.get('error', '')}")
            continue
        a = r.get('applied_auto', 0)
        m = r.get('applied_medium', 0)
        mn = r.get('needs_manual', 0)
        sk = r.get('skipped', 0)
        tot['auto'] += a
        tot['med'] += m
        tot['man'] += mn
        tot['skip'] += sk
        src = Path(r.get('source', '?')).name if r.get('source') else '?'
        lines.append(f"  {nm} → {src}: авто={a}, средняя={m}, "
                     f"needs_manual={mn}, пропущено={sk}")
        for ch in r.get('changes', []):
            kind = ch.get('kind')
            if kind == 'medium':
                lines.append(f"      стр.{ch.get('line')}: применено "
                             f"(средняя уверенность, conf={ch.get('confidence')})")
            elif kind == 'auto':
                lines.append(f"      стр.{ch.get('line')}: применено "
                             f"(conf={ch.get('confidence')})")
            elif kind == 'manual':
                lines.append(f"      стр.{ch.get('line')}: needs_manual "
                             f"({ch.get('reason', '')})")
            elif kind == 'skipped':
                lines.append(f"      стр.{ch.get('line')}: пропущено "
                             f"({ch.get('error', '')})")
    lines.append(f"ИТОГО: авто={tot['auto']}, средняя уверенность={tot['med']}, "
                 f"needs_manual={tot['man']}, пропущено={tot['skip']}")
    return lines


if __name__ == '__main__':  # pragma: no cover - ручная проверка
    d = ensure_dirs()
    print('Каталоги:', {k: str(v) for k, v in d.items()})
