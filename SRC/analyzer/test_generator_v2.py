#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DS_147: TestGeneratorV2 - генератор тестовых .plp по рубрикатору v5.3.0.
#
# Формирует тестовые .plp-файлы в стиле TestDeepSeek.plp:
#   single   - один сводный файл со всеми выбранными правилами;
#   per-rule - по одному файлу на правило.
#
# Источник правил: DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json (332 правила).
# Фильтры: sources, priorities (HIGH/MEDIUM/LOW), categories (PlpCheck).
#
# Имена файлов:
#   single:   test_<src>_<prio>_<cat>_single_<YYYYMMDD_HHMMSS>.plp
#   per-rule: test_<safe_name>_<YYYYMMDD_HHMMSS>.plp
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from fixer.markdown_rubricator_loader_v3 import (
        MarkdownRubricatorLoaderV3,
        RubricatorRule,
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from fixer.markdown_rubricator_loader_v3 import (
        MarkdownRubricatorLoaderV3,
        RubricatorRule,
    )


_CYR_TO_LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
}

_PRIO_LETTER = {'HIGH': 'H', 'MEDIUM': 'M', 'LOW': 'L'}


def _translit(text: str) -> str:
    return ''.join(_CYR_TO_LAT.get(ch, ch) for ch in text)


def safe_name(rule_code: str) -> str:
    s = rule_code
    s = _translit(s)
    s = re.sub(r'[^0-9A-Za-z_]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def _prio_tag(priorities):
    if not priorities:
        return 'all'
    return ''.join(sorted({_PRIO_LETTER.get(p, '?') for p in priorities}))


def _src_tag(sources):
    if not sources:
        return 'all'
    return '+'.join(sorted(set(sources)))


def _cat_tag(categories):
    if not categories:
        return 'all'
    return '+'.join(sorted(set(categories)))

class TestGeneratorV2:
    # DS_147: пометка для pytest — это не тестовый класс
    __test__ = False

    # Генератор тестовых .plp по рубрикатору v5.3.0 (DS_147).

    def __init__(
        self,
        rubricator_dir: Optional[Path] = None,
        sources: Optional[List[str]] = None,
        priorities: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
    ) -> None:
        if rubricator_dir is None:
            rubricator_dir = Path(__file__).resolve().parent.parent.parent / 'DATA' / 'Рубрикатор v5'
        self.rubricator_dir = Path(rubricator_dir)
        self.sources = list(sources) if sources else None
        self.priorities = list(priorities) if priorities else None
        self.categories = list(categories) if categories else None

        self.loader = MarkdownRubricatorLoaderV3(self.rubricator_dir)
        self.rules = dict(self.loader.rules)
        self._json_data = self._load_json()

    def _load_json(self) -> Dict[str, Any]:
        p = self.rubricator_dir / '4.RUBRICATOR_PROMPT v5.json'
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding='utf-8-sig'))

    def _passes_filters(self, code: str, rule) -> bool:
        src = code.split('.', 1)[0]
        src_lc = src.lower()

        if self.sources:
            want = {s.lower() for s in self.sources}
            if src_lc not in want:
                return False

        if self.priorities:
            prio = (rule.priority or '').upper()
            if prio not in {p.upper() for p in self.priorities}:
                return False

        # DS_147: categories-фильтр ОТКЛЮЧЁН (маппинг PLPCHECK_CATEGORIES <->
        # subcategory в v5.json отсутствует). Фильтрация по категориям -
        # ответственность GUI перед вызовом generate().
        return True

    def select_rules(self, rule_codes: Optional[List[str]] = None) -> List[str]:
        if rule_codes:
            return sorted(rc for rc in rule_codes if rc in self.rules)
        return sorted(c for c, r in self.rules.items() if self._passes_filters(c, r))

    def _meta_block(self, code: str, rule) -> List[str]:
        lines = []
        lines.append('-- ' + '=' * 76)
        lines.append('-- Правило: ' + code)
        lines.append('-- Описание: ' + (rule.short_description or ''))
        lines.append('-- Категория: ' + (rule.category or ''))
        if getattr(rule, 'subcategory', None):
            lines.append('-- Подкатегория: ' + rule.subcategory)
        lines.append('-- Приоритет: ' + (rule.priority or ''))
        tags = []
        jr = (self._json_data.get('rules', {}) or {}).get(code, {}) or {}
        tags = jr.get('tags', []) or []
        if tags:
            lines.append('-- Теги: ' + ', '.join(tags))
        lines.append('-- ' + '=' * 76)
        lines.append('-- 4.RUBRICATOR_PROMPT v5.json:')

        def _emit_multi(label: str, value: str):
            if not value:
                return
            vlines = value.splitlines() or ['']
            first = True
            for vl in vlines:
                if first:
                    lines.append('--   ' + label + ': ' + vl)
                    first = False
                else:
                    lines.append('--   ' + ' ' * len(label) + '  ' + vl)

        _emit_multi('documentation_text', rule.documentation_text or '')
        if getattr(rule, 'plplus_materials_note', None):
            _emit_multi('plplus_materials_note', rule.plplus_materials_note)
        if getattr(rule, 'search_prompt', None):
            _emit_multi('search_prompt', rule.search_prompt)
        bad_list = list(rule.code_example_bad or [])
        if bad_list:
            _emit_multi('code_example_bad', str(bad_list[0]))
            for k, b in enumerate(bad_list[1:], 2):
                _emit_multi('code_example_bad' + str(k), str(b))
        if getattr(rule, 'code_example_good', None):
            _emit_multi('code_example_good', rule.code_example_good)
        if rule.fix_instruction:
            _emit_multi('fix_instruction', rule.fix_instruction)
        patterns = getattr(rule, 'regex_patterns_search', None) or []
        if patterns:
            pats = []
            for n, pat in enumerate(patterns, 1):
                desc = pat.get('description', pat.get('pattern', ''))
                pats.append('(' + str(n) + ') ' + desc)
            lines.append('--   regex_patterns.for_search: ' + '; '.join(pats))
        lines.append('-- ' + '=' * 76)
        return lines

    @staticmethod
    def _split_declare(example: str) -> Tuple[List[str], str]:
        if not example:
            return [], ''
        text = example.strip()
        if not text.lower().startswith('declare'):
            return [], text
        m = re.search(r'\bbegin\b', text, re.IGNORECASE)
        if not m:
            return [], text
        decl = text[:m.start()].strip()
        body = text[m.start():].strip()
        decl_lines = decl.splitlines()
        if decl_lines and decl_lines[0].strip().lower() == 'declare':
            decl_lines = decl_lines[1:]
        # C4c: снимаем префикс 'declare ' с каждой строки decl_lines
        decl_lines = [d.strip() for d in decl_lines if d.strip()]
        decl_lines = [re.sub(r'^\s*declare\s+', '', d, flags=re.IGNORECASE).strip()
                      for d in decl_lines]
        decl_lines = [d for d in decl_lines if d]

        # A4h: удаляем внешние begin ... end; аккуратно
        body = re.sub(r'^\s*begin\b[ \t]*', '', body, count=1, flags=re.IGNORECASE)
        body = re.sub(r'[ \t]*\bend\s*;?\s*$', '', body, flags=re.IGNORECASE)

        blines = body.splitlines()
        indents = [len(l) - len(l.lstrip()) for l in blines if l.strip()]
        if indents:
            min_ind = min(indents)
            blines = [l[min_ind:] if len(l) >= min_ind else l for l in blines]
        body = '\n'.join(blines).strip()
        return decl_lines, body

    @staticmethod
    def _indent_block(text: str, indent: int = 2) -> List[str]:
        pad = '    ' * indent
        out = []
        for line in (text or '').splitlines():
            if line.strip():
                out.append(pad + line.rstrip())
            else:
                out.append('')
        return out

    def _procedure_block(self, code: str, rule) -> List[str]:
        lines = []
        proc = safe_name(code)
        bad_list = list(rule.code_example_bad or [])
        bad_main = bad_list[0] if bad_list else ''
        extra_bads = bad_list[1:] if len(bad_list) > 1 else []
        good = (rule.code_example_good or '').strip()

        # A4d: декларации из bad и good, дедуп
        decl_bad, bad_body = self._split_declare(bad_main)
        decl_good, good_body = self._split_declare(good)
        decl_lines = []
        for d in decl_bad + decl_good:
            if d not in decl_lines:
                decl_lines.append(d)
        if decl_good:
            good = good_body

        lines.append('PUBLIC PROCEDURE ' + proc + ' IS')
        for d in decl_lines:
            lines.append('    ' + d)
        lines.append('BEGIN')
        lines.append('    BEGIN')
        lines.append('        savepoint sp1;')
        short = (rule.short_description or '').strip()
        # C4: одиночные кавычки -> двойные (не конфликтуют с '...' обёрткой)
        short_safe = short.replace(chr(39), chr(34))
        code_safe = code.replace(chr(39), chr(34))
        lines.append(f"        debug_pipe('-= {code_safe} {short_safe} =-', 0);")
        lines.append('')
        lines.append('        -- [-] НЕПРАВИЛЬНО')
        if bad_body:
            lines.append('        -- begin pl/sql')
            for l in self._indent_block(bad_body, indent=2):
                lines.append(l)
            lines.append('        -- end pl/sql')
            for extra in extra_bads:
                lines.append('        -- Дополнительный пример:')
                for l in self._indent_block(extra, indent=2):
                    lines.append(l)
        else:
            lines.append('        -- (нет примера)')
        lines.append('')
        lines.append('        -- [+] ПРАВИЛЬНО')
        if good:
            lines.append('        -- begin pl/sql')
            for l in self._indent_block(good, indent=2):
                lines.append(l)
            lines.append('        -- end pl/sql')
        elif rule.fix_instruction:
            lines.append('        -- begin pl/sql')
            lines.append('        -- Исправление: ' + rule.fix_instruction)
            lines.append('        -- end pl/sql')
        else:
            lines.append('        -- (нет примера)')
        lines.append('')
        lines.append('        RAISE; -- прерываем, чтобы случайно не внести изменения на схему')
        lines.append('    EXCEPTION WHEN OTHERS THEN')
        lines.append('        debug_pipe(substr(utils.error_stack, 1, 4000), 0);')
        lines.append('        ROLLBACK TO sp1;')
        lines.append('    END;')
        lines.append('END;')
        lines.append('')
        return lines

    def _filename_single(self, mode_sel: str) -> str:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        src = _src_tag(self.sources)
        prio = _prio_tag(self.priorities)
        cat = _cat_tag(self.categories)
        # B3: схема test_<src>_<prio>_<cat>_<sel|all>_single_<ts>.plp
        return 'test_' + src + '_' + prio + '_' + cat + '_' + mode_sel + '_single_' + ts + '.plp'

    def _filename_per_rule(self, code: str) -> str:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        return 'test_' + safe_name(code) + '_' + ts + '.plp'

    def generate(
        self,
        rule_codes: Optional[List[str]] = None,
        mode: str = 'single',
        out_dir: Optional[Path] = None,
    ):
        if out_dir is None:
            out_dir = Path(__file__).resolve().parent.parent.parent / 'DATA' / 'generated_plp'
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        codes = self.select_rules(rule_codes)
        if not codes:
            return [] if mode == 'per-rule' else None

        mode_sel = 'sel' if rule_codes else 'all'

        if mode == 'per-rule':
            paths = []
            for code in codes:
                rule = self.rules[code]
                meta = self._meta_block(code, rule)
                body = self._procedure_block(code, rule)
                header = [
                    '-- ' + '=' * 76,
                    '-- ТЕСТОВЫЙ ФАЙЛ ДЛЯ ПРАВИЛА: ' + code,
                    '-- Дата генерации: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    '-- ' + '=' * 76,
                    '',
                ]
                text = '\n'.join(header + meta + body)
                p = out_dir / self._filename_per_rule(code)
                p.write_text(text, encoding='utf-8')
                paths.append(p)
            return paths

        lines = []
        lines.append('-- ' + '=' * 76)
        lines.append('-- ТЕСТОВЫЙ ФАЙЛ: правила v5.3.0 (' + str(len(codes)) + ' шт.)')
        lines.append('-- Дата генерации: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if self.sources:
            lines.append('-- Источники: ' + ', '.join(self.sources))
        if self.priorities:
            lines.append('-- Приоритеты: ' + ', '.join(self.priorities))
        if self.categories:
            lines.append('-- Категории PlpCheck: ' + ', '.join(self.categories))
        lines.append('-- ' + '=' * 76)
        lines.append('')
        lines.append('-- Список правил:')
        for i, code in enumerate(codes, 1):
            r = self.rules[code]
            desc = (r.short_description or '')[:60].ljust(60)
            lines.append('-- ' + str(i).rjust(3) + '.  ' + code.ljust(50) + ' - ' + desc)
        lines.append('')
        for code in codes:
            rule = self.rules[code]
            lines.extend(self._meta_block(code, rule))
            lines.extend(self._procedure_block(code, rule))

        fname = self._filename_single(mode_sel)
        p = out_dir / fname
        p.write_text('\n'.join(lines), encoding='utf-8')
        return p


__all__ = ['TestGeneratorV2', 'safe_name']