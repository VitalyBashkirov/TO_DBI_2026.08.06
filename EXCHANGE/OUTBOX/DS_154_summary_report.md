# DS_154 — OQ-1 + OQ-2 (Chat 45)

## Scope
- OQ-1: scanner.py — `_is_rule_selected` narrows `plpcheck.*` by full rule code.
- OQ-2: tools/close_ds.ps1 — skip empty commit when only EXCHANGE/bot.log staged.

## OQ-1 — scanner.py

### Root cause
- `_is_rule_selected` had step 3: `any(s.startswith(rule_prefix + '.'))`
  -> `selected=['plpcheck.BAD_PREFIX']` matched every `plpcheck.*`.
- `scan_file` added regex issues unconditionally (no `_is_rule_selected` filter),
  so even with the fix multiline-only, regex rules of the same file still leaked.

### Fix
1. `_is_rule_selected`: removed prefix-widening (step 3 -> `return False`).
   Exact rule-code match is handled in step 2.
2. `scan_file`: added post-filter for regex issues:
   `if not self._is_rule_selected(base_issue_type): continue`
3. Multiline `_check_plp_*` were already guarded by `_is_rule_selected`
   (verified by AST test #8).

### Tests
- `test_ds153d_scanner_selected_rules.py`:
  - #2 switched to `plpcheck.CODE_IN_COMMENT` + strict all-equal assertion.
  - #3 renamed to `test_multiline_filtered_by_selected_rules` + `not others`.
  - #6 renamed to `test_selected_rule_narrows_plpcheck` + `not in types`.
  - 6 passed.
- `test_ds154_scanner_oq1.py` (new):
  - #7 functional: selected=['plpcheck.BAD_PREFIX'] -> no CODE_IN_COMMENT/NOT_MENTIONED/WRONG_METHOD_SYNTAX.
  - #8 AST: every `_check_plp_*` call is guarded by matching `_is_rule_selected('plpcheck.X')`.
  - 2 passed.

## OQ-2 — tools/close_ds.ps1

### Root cause
- Step [4/8] always `git add EXCHANGE/bot.log`.
- Step [5/8] `git commit` without checking staged content
  -> re-run creates duplicate empty commit (only bot.log).

### Fix
- Added step [4.9/8] OQ-2 between `git add` and `git commit`:
  - `git diff --cached --name-only`
  - if only `EXCHANGE/bot.log` (or nothing) staged -> print summary and `return`
    (no commit).
- Patch preserved original UTF-8 BOM (PS 5.1 + cyrillic requirement).

### Tests
- `test_ds154_close_ds_botlog_only.py` (new, 3 tests):
  - guard marker present + nonBotLog check + `return` in `nonBotLog.Count -eq 0` block;
  - guard position before `git commit -m`;
  - real PS parser: `[ScriptBlock]::Create` on close_ds.ps1 -> OK.
  - 3 passed.

## Regression
- Baseline: 314 passed.
- After: 319 passed (62.99s).
- Delta: +3 (OQ-2) +2 (OQ-1).

## Files changed
- SRC/analyzer/scanner.py (OQ-1)
- tools/close_ds.ps1 (OQ-2)
- SRC/tests/test_ds153d_scanner_selected_rules.py (#2, #3, #6)
- SRC/tests/test_ds154_scanner_oq1.py (new, #7, #8)
- SRC/tests/test_ds154_close_ds_botlog_only.py (new, 3 tests)
- AGENTS.md (status block)
- EXCHANGE/OUTBOX/DS_154_summary_report.md (this file)