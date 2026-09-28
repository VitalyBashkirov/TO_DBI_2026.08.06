# -*- coding: utf-8 -*-
"""DS_082a — Rule-based fixer для тривиальных правил.

Читает AI_REQUEST_<source>_<ts>.md (DS_054), закрывает тривиальные issues
детерминированными алгоритмами (без вызова AI) и пишет AI_RESPONSE_<source>_<ts>.md
в том же формате. АРМ применяет ответ через существующий receive_from_ai (DS_081).

Тривиальные правила (tools/rule_based_rules.json, v1):
  BAD_PREFIX / PREFIX_TYPE_IN_VAR_NAME — rename old->new (new из description);
  WRONG_METHOD_SYNTAX                  — [X].Y -> ::[X].[Y];
  CODE_IN_COMMENT                      — удалить строку (code начинается с -- или /*);
  QUOTING                              — # -> _ в идентификаторах;
  SIZELESS                             — string/varchar2 без размера -> varchar2(255);
  NOT_MENTIONED                        — удалить объявление.

Неприменимый алгоритм или нетривиальное правило -> issue пропускается
(лог «skip rule_code=...») и уходит в AI (DS_082b).

CLI (glob НЕ в cmd — только внутри Python):
  python tools\\rule_based_fixer.py --request <файл> [--out <каталог>] [--rules <json>]
  python tools\\rule_based_fixer.py --in-dir EXCHANGE\\AI_IN --out-dir EXCHANGE\\AI_OUT

Не меняет: SRC\\, DATA\\, формат AI_REQUEST/AI_RESPONSE, EXCHANGE\\.
Логи: stdout + EXCHANGE\\bot.log (DS_050, best effort).
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RULES = Path(__file__).resolve().parent / 'rule_based_rules.json'
BOT_LOG = ROOT / 'EXCHANGE' / 'bot.log'

REQUEST_PREFIX = 'AI_REQUEST_'
RESPONSE_PREFIX = 'AI_RESPONSE_'
DELETED_MARKER = '-- (удалено)'

# Разбор блока «### Проблема N» из AI_REQUEST.
_RE_PROBLEM = re.compile(
    r'^###\s*Проблема\s+(?P<id>\d+)\s*$'
    r'(?:.*?^-\s*Строка:\s*(?P<line>\d+)\s*$'
    r'.*?^-\s*Код правила:\s*(?P<rule>\S+)\s*$'
    r'.*?^-\s*Описание:\s*(?P<desc>[^\r\n]*)$'
    r'.*?^-\s*Текущий код:\s*$.*?^```\s*$'
    r'(?P<code>.*?)^```\s*$)?',
    re.MULTILINE | re.DOTALL,
)
_RE_SOURCE = re.compile(r'^-\s*Источник:\s*(.+)$', re.MULTILINE)
_RE_WORD = re.compile(r'\b[A-Za-z_][A-Za-z0-9_#]*\b')


# ----------------------------------------------------------------------
# Лог: stdout + EXCHANGE\bot.log (DS_050, только best effort)
# ----------------------------------------------------------------------
def _log(msg: str, to_bot: bool = False) -> None:
    print(msg, flush=True)
    if not to_bot:
        return
    try:
        ts = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        with open(BOT_LOG, 'a', encoding='utf-8', newline='') as f:
            f.write(f"[{ts}] DS 082a: {msg}\r\n")
    except Exception:
        pass


# ----------------------------------------------------------------------
# Разбор AI_REQUEST
# ----------------------------------------------------------------------
def parse_request(path: Path) -> dict:
    """Разобрать AI_REQUEST: источник + список issues (id, line, rule_code,
    description, code). Формат файла не меняется — только чтение."""
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    m = _RE_SOURCE.search(text)
    source = m.group(1).strip() if m else ''
    issues = []
    for mm in _RE_PROBLEM.finditer(text):
        if not mm.group('line'):
            continue
        issues.append({
            'id': int(mm.group('id')),
            'line': int(mm.group('line')),
            'rule_code': mm.group('rule').strip(),
            'description': mm.group('desc').strip(),
            'code': mm.group('code').strip('\r\n'),
        })
    return {'path': Path(path), 'source': source, 'issues': issues}


# ----------------------------------------------------------------------
# Алгоритмы правил (каждый возвращает new_code или None -> skip)
# ----------------------------------------------------------------------
_DECL_KEYWORDS = {'function', 'procedure', 'public', 'private', 'protected',
                  'static', 'method', 'pragma', 'type', 'const', 'return',
                  'declare', 'begin', 'if', 'for', 'while', 'loop'}


def _is_subseq(sub: str, s: str) -> bool:
    """sub — подпоследовательность s (все символы sub в s по порядку)."""
    it = iter(s)
    return all(ch in it for ch in sub)


def _find_old_token(code: str, new_name: str) -> str | None:
    """Старое имя переменной в строке объявления.

    Два способа (по надёжности):
    1) самое длинное слово из code, которым оканчивается new_name
       (IS_EOD_NEW <- v_bIS_EOD_NEW, OpDateBranch <- v_OpDateBranch);
    2) первое слово-идентификатор code (не ключевое слово), являющееся
       подпоследовательностью new_name — покрывает короткие имена
       (t1 <- v_iT1, i <- v_nI, m <- v_rM) и вставку префикса
       (vHours <- v_nHours).
    """
    nl = new_name.lower()
    words = _RE_WORD.findall(code)
    best = ''
    for w in words:
        if len(w) > len(best) and nl.endswith(w.lower()) and len(w) >= 3:
            best = w
    if best:
        return best
    first = None
    for w in words:
        if w.lower() not in _DECL_KEYWORDS:
            first = w
            break
    if first and _is_subseq(first.lower(), nl) and first != new_name:
        return first
    return None


def fix_rename(issue: dict, rule: dict) -> str | None:
    """BAD_PREFIX / PREFIX_TYPE_IN_VAR_NAME: заменить старое имя на new_name."""
    m = re.search(rule['new_from_desc'], issue['description'])
    if not m:
        return None
    new_name = m.group(1)
    old = _find_old_token(issue['code'], new_name)
    if not old or old == new_name:
        return None
    return re.sub(rf'\b{re.escape(old)}\b', new_name, issue['code'])


def fix_method_syntax(issue: dict, rule: dict) -> str | None:
    """WRONG_METHOD_SYNTAX: [X].Y -> ::[X].[Y] (target из description)."""
    m = re.search(rule['target_from_desc'], issue['description'])
    if not m:
        return None
    target = m.group(1)
    mt = re.match(r'::\[(?P<x>[^\]]+)\]\.\[(?P<y>[^\]]+)\]', target)
    if not mt:
        return None
    x, y = re.escape(mt.group('x')), re.escape(mt.group('y'))
    new_code, n = re.subn(
        rf'(?<!:)\[{x}\]\.\s*{y}\b', target, issue['code'],
        flags=re.IGNORECASE)
    return new_code if n else None


def _strip_ranges(text: str) -> str:
    """Убрать из строки литералы '...' и комментарии -- / /* */ (для QUOTING).

    Возвращает «маску» той же длины: позиции литералов/комментариев — пробелы.
    """
    out = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "'":                              # строковый литерал
            j = i + 1
            while j < n:
                if text[j] == "'":
                    if j + 1 < n and text[j + 1] == "'":   # экранированная ''
                        j += 2
                        continue
                    break
                j += 1
            j = min(j, n - 1)
            out.append(' ' * (j + 1 - i))
            i = j + 1
            continue
        if ch == '-' and text[i:i + 2] == '--':    # комментарий до конца строки
            out.append(' ' * (n - i))
            break
        if ch == '/' and text[i:i + 2] == '/*':    # блочный комментарий
            j = text.find('*/', i + 2)
            j = n if j == -1 else j + 2
            out.append(' ' * (j - i))
            i = j
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def fix_quoting(issue: dict, _rule: dict) -> str | None:
    """QUOTING: # -> _ только в идентификаторах (не в '...' и не в комментариях)."""
    code = issue['code']
    mask = _strip_ranges(code)
    out = []
    changed = False
    for i, ch in enumerate(code):
        if ch == '#' and mask[i] == '#':
            prev_ok = i > 0 and (mask[i - 1].isalnum() or mask[i - 1] == '_')
            next_ok = (i + 1 < len(code) and
                       (mask[i + 1].isalnum() or mask[i + 1] == '_'))
            if prev_ok or next_ok:
                out.append('_')
                changed = True
                continue
        out.append(ch)
    return ''.join(out) if changed else None


def fix_sizeless(issue: dict, rule: dict) -> str | None:
    """SIZELESS: string -> varchar2(255); bare varchar2 (без размера) -> varchar2(255)."""
    code = issue['code']
    new_type = rule.get('string_type', 'varchar2(255)')
    new_code, n = re.subn(r'\bstring\b', new_type, code, flags=re.IGNORECASE)
    if n:
        return new_code
    new_code, n = re.subn(r'\bvarchar2\b(?!\s*\()', new_type, code,
                          flags=re.IGNORECASE)
    return new_code if n else None


def fix_delete_line(issue: dict, _rule: dict) -> str | None:
    """CODE_IN_COMMENT / NOT_MENTIONED: удалить строку.

    CODE_IN_COMMENT — только если code начинается с -- или /* (иначе живой код);
    NOT_MENTIONED — удалить объявление. Диапазон N–M в description не
    встречается (см. DS_082a_report §5.5), формат AI_RESPONSE однострочный.
    """
    rule_name = issue['rule_code'].split('.')[-1]
    stripped = issue['code'].strip()
    if rule_name == 'CODE_IN_COMMENT' and not stripped.startswith(('--', '/*')):
        return None
    return DELETED_MARKER


ACTIONS = {
    'rename': fix_rename,
    'method_syntax': fix_method_syntax,
    'quoting': fix_quoting,
    'sizeless': fix_sizeless,
    'delete_line': fix_delete_line,
}


# ----------------------------------------------------------------------
# Генерация AI_RESPONSE
# ----------------------------------------------------------------------
def build_fixes(request: dict, rules_cfg: dict,
                log=_log) -> tuple[list[dict], list[dict]]:
    """Прогнать issues через алгоритмы. Возвращает (fixes, skipped)."""
    by_suffix = {r['rule_code'].split('.')[-1]: r for r in rules_cfg['rules']}
    conf = float(rules_cfg.get('confidence', 0.99))
    fixes, skipped = [], []
    for it in request['issues']:
        suffix = it['rule_code'].split('.')[-1]
        rule = by_suffix.get(suffix)
        if not rule:
            skipped.append({**it, 'why': 'нет в rules.json'})
            log(f"skip rule_code={it['rule_code']} (line {it['line']}): "
                f"правило не тривиальное")
            continue
        try:
            after = ACTIONS[rule['action']](it, rule)
        except Exception as e:                          # noqa: BLE001
            after = None
            log(f"skip rule_code={it['rule_code']} (line {it['line']}): {e}")
        if after is None or after == it['code']:
            skipped.append({**it, 'why': 'алгоритм неприменим'})
            log(f"skip rule_code={it['rule_code']} (line {it['line']}): "
                f"алгоритм неприменим")
            continue
        fixes.append({
            'id': it['id'],
            'line': it['line'],
            'before': it['code'],
            'after': after,
            'reason': f"rule-based: {it['rule_code']}",
            'confidence': conf,
        })
    return fixes, skipped


def write_response(request: dict, fixes: list[dict], out_dir: Path) -> Path:
    """AI_RESPONSE_<source>_<ts>.md — Markdown + ```json [...]``` (формат DS_054)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(request['path']).stem
    tail = stem[len(REQUEST_PREFIX):] if stem.startswith(REQUEST_PREFIX) else stem
    resp = out_dir / f"{RESPONSE_PREFIX}{tail}.md"
    body = json.dumps(fixes, ensure_ascii=False, indent=2)
    text = (f"# AI-ответ (rule-based, DS_082a)\n\n"
            f"- Источник: {request['source']}\n"
            f"- Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            f"- Исправлений: {len(fixes)} (confidence=0.99, rule-based)\n\n"
            f"```json\n{body}\n```\n")
    resp.write_text(text.replace('\r\n', '\n').replace('\n', '\r\n'),
                    encoding='utf-8', newline='')
    return resp


# ----------------------------------------------------------------------
# Обработка одного запроса / каталога
# ----------------------------------------------------------------------
def process_request(req_path: Path, out_dir: Path, rules_path: Path,
                    log=_log) -> dict:
    rules_cfg = json.loads(Path(rules_path).read_text(encoding='utf-8'))
    request = parse_request(Path(req_path))
    if not request['issues']:
        log(f"skip {Path(req_path).name}: не разобрано ни одного issue")
        return {'request': str(req_path), 'fixes': 0, 'skipped': 0, 'response': None}
    fixes, skipped = build_fixes(request, rules_cfg, log=log)
    resp = write_response(request, fixes, out_dir) if fixes else None
    if not fixes:
        log(f"skip {Path(req_path).name}: 0 fixes (все issues нетривиальные)")
    log(f"{Path(req_path).name}: issues={len(request['issues'])}, "
        f"rule-based={len(fixes)}, skip={len(skipped)} -> "
        f"{resp.name if resp else 'нет ответа'}")
    return {'request': str(req_path), 'fixes': len(fixes),
            'skipped': len(skipped), 'response': str(resp) if resp else None}


def main(argv=None) -> int:
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                      errors='replace')
    ap = argparse.ArgumentParser(description='DS_082a rule-based fixer')
    ap.add_argument('--request', help='путь к одному AI_REQUEST_*.md')
    ap.add_argument('--out', help='каталог для AI_RESPONSE (по умолчанию EXCHANGE\\AI_OUT)')
    ap.add_argument('--in-dir', help='каталог с AI_REQUEST_* (batch, glob внутри Python)')
    ap.add_argument('--out-dir', help='каталог для AI_RESPONSE в batch-режиме')
    ap.add_argument('--rules', default=str(DEFAULT_RULES),
                    help='путь к rule_based_rules.json')
    args = ap.parse_args(argv)

    rules_path = Path(args.rules)
    if not rules_path.exists():
        _log(f"Файл правил не найден: {rules_path}", to_bot=True)
        return 2

    if args.request:
        out = Path(args.out) if args.out else ROOT / 'EXCHANGE' / 'AI_OUT'
        r = process_request(Path(args.request), out, rules_path)
        _log(f"Rule-based fixer: {Path(args.request).name}: fixes={r['fixes']}, "
             f"skip={r['skipped']}, response={r['response']}", to_bot=True)
        return 0

    if args.in_dir:
        in_dir = Path(args.in_dir)
        out = Path(args.out_dir) if args.out_dir else ROOT / 'EXCHANGE' / 'AI_OUT'
        requests = sorted(list(in_dir.glob(f'{REQUEST_PREFIX}*.md')) +
                          list(in_dir.glob(f'{REQUEST_PREFIX}*.json')))
        if not requests:
            _log(f"В каталоге нет AI_REQUEST_*: {in_dir}", to_bot=True)
            return 1
        total_f = total_s = 0
        for req in requests:
            r = process_request(req, out, rules_path)
            total_f += r['fixes']
            total_s += r['skipped']
        _log(f"Rule-based fixer (batch): запросов={len(requests)}, "
             f"fixes={total_f}, skip={total_s} -> {out}", to_bot=True)
        return 0

    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
