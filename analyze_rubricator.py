#!/usr/bin/env python3
"""Анализ структуры рубрикатора v3.3.0"""
import json

with open('../DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json', 'r', encoding='cp1251') as f:
    d = json.load(f)

rules = d.get('rules', {})
print('Total rules:', len(rules))

# Check first rule structure
first = list(rules.values())[0]
print('\nFields in first rule:')
for k in sorted(first.keys()):
    v = first[k]
    t = type(v).__name__
    if isinstance(v, dict):
        t += ' keys=' + str(list(v.keys())[:5])
    elif isinstance(v, list):
        t += ' len=%d' % len(v)
    print('  %s: %s' % (k, t))

# Count AI analysis required
ai_count = sum(1 for r in rules.values() if r.get('ai_analysis_required'))
print('\nRules with ai_analysis_required: %d' % ai_count)

# Show one AI rule example
for code, rule in rules.items():
    if rule.get('ai_analysis_required'):
        print('\nExample AI rule: %s' % code)
        ai = rule.get('ai_analysis_instructions', {})
        print('  steps: %d steps' % len(ai.get('steps', [])))
        print('  fix_strategy: %s' % ai.get('fix_strategy', 'N/A'))
        print('  replacements: %s' % str(list(ai.get('replacements', {}).keys())[:3]))
        print('  priority_level: %s' % rule.get('priority_level', 'N/A'))
        print('  multiline: %s' % rule.get('multiline', 'N/A'))
        break

# Show all AI rules
print('\nAll AI rules:')
for code, rule in rules.items():
    if rule.get('ai_analysis_required'):
        print('  %s' % code)
