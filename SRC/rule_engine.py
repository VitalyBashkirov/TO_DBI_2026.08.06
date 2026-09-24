#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RuleEngine — единый механизм правил для сканера и фиксера (DS_053).

Отвечает за:
  * загрузку правил исправления из 5.RUBRICATOR_PARSER_SQL v5.json;
  * классификацию правил/паттернов по корзинам (regex / hybrid / other);
  * фильтрацию правил по флагам-чекбоксам GUI;
  * применение детерминированного исправления к строке.

Поиск проблем (для сканера) и применение фиксов (для фиксера) опираются на
один и тот же набор правил и одну и ту же классификацию корзин.

Флаги (6 чекбоксов GUI):
  regex        — transform_type == 'regex'
  hybrid       — transform_type == 'hybrid' с algorithmic_hint
  other        — transform_type == 'hybrid' без algorithmic_hint
  ai_fallback  — в DS_053 только пометка needs_ai_fix (вызов AI — DS_054)
  ignore       — не подлежит автофиксу (только уведомление)
  backup       — резервные regex-правила self.FIXES (ведёт фиксер)
"""
from pathlib import Path
import sys
from typing import Dict, List, Optional, Set, Tuple, Any

sys.path.insert(0, str(Path(__file__).parent))

from analyzer.sql_parser import (  # noqa: E402
    load_config,
    find_rule,
    apply_fix_ex,
    apply_fix_multiline,
    _pattern_bucket,
)

# Порядковый список корзин-флагов для формирования имени лога VVxVVx.
FLAG_ORDER: List[str] = ['regex', 'hybrid', 'ai_fallback', 'ignore', 'backup', 'other']

# Корзины, которым соответствуют transform_type из PARSER_SQL.
TRANSFORM_BUCKETS: Set[str] = {'regex', 'hybrid', 'other'}


class RuleEngine:
    """Единый движок правил исправления (загрузка + фильтр по флагам + фикс)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config if config is not None else load_config()
        self._rules: Dict[str, Dict[str, Any]] = {}
        for rule in self._config.get('rules', []):
            code = rule.get('rule_code')
            if code:
                self._rules[code] = rule
        self.version = self._config.get('version', 'N/A')

    # ------------------------------------------------------------------
    # Загрузка / классификация
    # ------------------------------------------------------------------
    def _resolve_code(self, rule_code: str) -> str:
        """DS_059: маппинг кодов сканера на коды PARSER_SQL.

        Сканер PlpCheck выдаёт ``plpcheck.<NAME>``, а PARSER_SQL содержит
        ``PlpCheck.<CAT>.<NAME>.п.<N>``. Возвращаем найденный код PARSER_SQL
        (первое совпадение; NAME уникальны), иначе исходный rule_code.
        """
        if not rule_code or not rule_code.lower().startswith('plpcheck.'):
            return rule_code
        name = rule_code.split('.', 1)[1].strip()
        if not name:
            return rule_code
        name_lower = name.lower()
        for code in self._rules:
            if not code.startswith('PlpCheck.'):
                continue
            parts = code.split('.')
            # Формат: PlpCheck.<CAT>.<NAME>.п.<N>[.<N>]
            if len(parts) >= 4 and parts[2].lower() == name_lower \
                    and parts[3].lower().startswith('п'):
                return code
        return rule_code

    def has_rule(self, rule_code: str) -> bool:
        """Есть ли правило с детерминированным исправлением в PARSER_SQL.

        DS_059: учитывает маппинг plpcheck.<NAME> -> PlpCheck.*.<NAME>.п.*
        """
        return self._resolve_code(rule_code) in self._rules

    def get_rule(self, rule_code: str) -> Optional[Dict[str, Any]]:
        """DS_059: правило PARSER_SQL по коду (с учётом маппинга plpcheck.*)."""
        return self._rules.get(self._resolve_code(rule_code))

    def rule_buckets(self, rule_code: str) -> Set[str]:
        """Множество корзин (regex/hybrid/other), к которым относится правило."""
        rule = self.get_rule(rule_code)
        buckets: Set[str] = set()
        if not rule:
            return buckets
        for pt in rule.get('patterns', []):
            buckets.add(_pattern_bucket(pt))
        return buckets

    # ------------------------------------------------------------------
    # Фильтр по флагам
    # ------------------------------------------------------------------
    @staticmethod
    def enabled_transform_buckets(flags: Dict[str, bool]) -> Set[str]:
        """Корзины-флаги из трансформационных, которые включены пользователем."""
        return {b for b in TRANSFORM_BUCKETS if flags.get(b, False)}

    def rule_enabled(self, rule_code: str, flags: Dict[str, bool]) -> bool:
        """Подлежит ли правило обработке при заданных флагах (без учёта backup).

        True, если хотя бы одна корзина правила включена флагом.
        """
        buckets = self.rule_buckets(rule_code)
        return bool(buckets & self.enabled_transform_buckets(flags))

    # ------------------------------------------------------------------
    # Применение исправления
    # ------------------------------------------------------------------
    def apply_fix(self, line: str, rule_code: str,
                  flags: Dict[str, bool]) -> Optional[Tuple[str, str, str]]:
        """Применить детерминированное исправление с учётом активных флагов.

        Args:
            line: Исходная строка.
            rule_code: Код правила.
            flags: Флаги-чекбоксы.

        Returns:
            None, если не применимо; иначе (result, bucket, kind),
            kind в {'transform','instruction'}.
        """
        allowed = self.enabled_transform_buckets(flags)
        if not allowed:
            return None
        # DS_059: маппинг plpcheck.<NAME> -> PlpCheck.*.<NAME>.п.*
        resolved = self._resolve_code(rule_code)
        res = apply_fix_ex(line, resolved, allowed_buckets=allowed)
        # DS_059_Уточнение_E: разделение bad_prefix/missing_prefix. Сканерные
        # issues plpcheck.BAD_PREFIX покрывают и простое отсутствие префикса
        # (зона missing_prefix_* правила PREFIX_TYPE_IN_VAR_NAME.п.4.4), поэтому
        # если плохие префиксы не сматчились — пробуем missing-паттерны вторым
        # шагом (регресс DS_059_Уточнение_D: Dp -> v_Dp, Cnt -> n_Cnt).
        if res is None and resolved == 'PlpCheck.STYLE.BAD_PREFIX.п.4.3':
            res = apply_fix_ex(
                line, 'PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4',
                allowed_buckets=allowed)
        return res

    def apply_fix_multiline(self, text: str, rule_code: str,
                            flags: Dict[str, bool]) -> Optional[Tuple[str, str, str]]:
        """Многострочное исправление блока/файла (DS_072c, replace_scope: "multiline").

        Args:
            text: Многострочный фрагмент (блок begin..end, view и т.п.).
            rule_code: Код правила (с маппингом plpcheck.<NAME>, DS_059).
            flags: Флаги-чекбоксы.

        Returns:
            None, если не применимо; иначе (result, bucket, kind).
        """
        allowed = self.enabled_transform_buckets(flags)
        if not allowed:
            return None
        resolved = self._resolve_code(rule_code)
        return apply_fix_multiline(text, resolved, allowed_buckets=allowed)

    # ------------------------------------------------------------------
    # Формирование имени лога по флагам
    # ------------------------------------------------------------------
    @staticmethod
    def flag_signature(flags: Dict[str, bool]) -> str:
        """Строка VVxVVx: V — флаг выбран, x — нет (порядок FLAG_ORDER).

        Пример: regex,hybrid включены; ai_fallback выключен; ignore,backup
        включены; other выключен -> 'VVxVVx'.
        """
        return ''.join('V' if flags.get(name, False) else 'x' for name in FLAG_ORDER)

    @staticmethod
    def any_replacement_flag(flags: Dict[str, bool]) -> bool:
        """Включён ли хотя бы один флаг замены (для доп. лога scan_*)."""
        return any(flags.get(name, False) for name in FLAG_ORDER)

    def log_name(self, source_name: str, timestamp: str, flags: Dict[str, bool]) -> str:
        """Имя файла лога scan_VVxVVx_<source>_<timestamp>.md."""
        return f"scan_{self.flag_signature(flags)}_{source_name}_{timestamp}.md"


# ----------------------------------------------------------------------
# Глобальный кэш движка (правила неизменяемы в рамках процесса).
# ----------------------------------------------------------------------
_ENGINE_CACHE: Optional[RuleEngine] = None


def get_rule_engine() -> RuleEngine:
    """Единый экземпляр RuleEngine (ленивая загрузка)."""
    global _ENGINE_CACHE
    if _ENGINE_CACHE is None:
        _ENGINE_CACHE = RuleEngine()
    return _ENGINE_CACHE
