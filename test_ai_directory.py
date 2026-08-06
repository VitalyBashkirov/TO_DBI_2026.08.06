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
        'file_pattern': '*.plp',
        'exclude_patterns': []
    }
}

scanner = PLPlusScanner(config)
stats = scanner.scan_directory()

print('\n=== SCAN DIRECTORY RESULTS ===')
print('Files scanned:', stats['files_scanned'])
print('Total issues:', stats['total_issues'])
print('AI results:', len(scanner.ai_results))
print('Rule types:', len(stats['by_type']))

# Generate report
output_path = Path('logs/scan_report_ai_directory.md')
scanner.generate_report(output_path)
print('\nReport saved:', output_path)
