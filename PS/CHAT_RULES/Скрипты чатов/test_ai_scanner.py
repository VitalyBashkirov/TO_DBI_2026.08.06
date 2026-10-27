#!/usr/bin/env python3
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
        'file_pattern': 'TestDeepSeek_full.plp',
        'exclude_patterns': []
    }
}

scanner = PLPlusScanner(config)
issues = scanner.scan_file(Path('PATCH_IN/patch_TEST_DS/TestDeepSeek_full.plp'))

print('Found issues:', len(issues))
print('AI results:', len(scanner.ai_results))

if scanner.ai_results:
    print('\nTop 5 AI results:')
    for r in scanner.ai_results[:5]:
        print('  [%s] line %d: %s (%.0f%%)' % (r.rule_code, r.line_number, r.steps_summary, r.confidence*100))

# Generate report
output_path = Path('logs/scan_report_ai_test.md')
scanner.generate_report(output_path)
print('\nReport saved:', output_path)
