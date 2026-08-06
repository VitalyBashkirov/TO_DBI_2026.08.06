#!/usr/bin/env python3
"""Финальный тест двухфазного анализа v3.3.0"""
import sys
sys.path.insert(0, 'SRC')
from pathlib import Path
from analyzer.scanner import PLPlusScanner

config = {
    'paths': {
        'source_dir': 'PATCH_IN/patch_TEST_DS',
        'results_dir': 'PATCH_OUT/test',
        'logs_dir': 'logs'
    },
    'scan': {
        'recursive': False,
        'file_pattern': '*.plp',
        'exclude_patterns': []
    }
}

def log_callback(message, level='info'):
    print(f"[{level.upper()}] {message}")

scanner = PLPlusScanner(config)
stats = scanner.scan_directory(log_callback=log_callback)

print('\n' + '='*70)
print('FINAL RESULTS')
print('='*70)
print('Files scanned:', stats['files_scanned'])
print('Total issues:', stats['total_issues'])
print('AI results:', len(scanner.ai_results))
print('Rule types:', len(stats['by_type']))

if scanner.ai_results:
    print('\n--- AI ANALYSIS BREAKDOWN ---')
    by_rule = {}
    for r in scanner.ai_results:
        by_rule[r.rule_code] = by_rule.get(r.rule_code, 0) + 1
    for rule, count in sorted(by_rule.items(), key=lambda x: -x[1]):
        print(f'  {rule}: {count}')

# Generate report
output_path = Path('logs/scan_report_FINAL.md')
scanner.generate_report(output_path)
print('\nReport saved:', output_path)
