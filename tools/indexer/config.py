# -*- coding: utf-8 -*-
"""DS_CNT_005c: Indexer config. DS_CNT_014: applied recommendations."""
import os

ARM_ROOT = r'F:\TO_DBI'
MODEL = 'nomic-embed-text'
OLLAMA_URL = 'http://localhost:11434'
STORE_DIR = os.path.join(ARM_ROOT, 'logs', 'indexer')
DB_PATH = os.path.join(STORE_DIR, 'chunks.db')
NPY_PATH = os.path.join(STORE_DIR, 'embeddings.npy')

CHUNK_SIZE = 256  # DS_CNT_014: было 512
CHUNK_OVERLAP = 64
BATCH_SIZE = 16
SCHEMA_VERSION = 2  # DS_CNT_014: было '1' — заставит переиндексацию

# DS_CNT_014: фильтр больших файлов (JSON/SQL > 50 KB — пропускать)
LARGE_FILE_LIMITS = {
    '.json': 50 * 1024,
    '.sql': 50 * 1024,
}

TEXT_EXTENSIONS = {'.md', '.txt'}

EXCLUDE_DIRS = {
    'logs', 'PATCH_IN', 'PATCH_OUT', '.git', 'node_modules',
    '__pycache__',
    # DS_CNT_014: расширение (~25 файлов)
    'SRC', 'tools', 'logs_Deep', 'reports', 'temp', 'temp_fix',
    'RubricatorTemp', 'Презентация', 'Вопросы-ответы', 'done',
    '.kilo', '.kilocode', '.vscode', '.pytest_cache',
    'INBOX', 'OUTBOX', 'PROCESSED', 'AI_IN', 'AI_OUT',
    '.github',
}
EXCLUDE_SUBPATHS = {
    # DS_CNT_014: DATA subdirs
    'DATA/CFT Platform IDE Documentation', 'DATA/Patch_USERNAME',
    'DATA/Тестовые файлы',
}
EXCLUDE_GLOBS = {'*.log', '*.tmp', '*.npy', '*.db', '*.bak', '*.old'}

# DS_CNT_014: точные исключения файлов (относительный путь, /)
EXCLUDE_FILES = {
    'ALGORITHM_FLOWCHART.md',
    'EXCHANGE/CNT_config_example.yaml',
    '.continue/config.yaml',
    # DS_CNT_015: шум в индексе
    'EXCHANGE/DS_031_NIGHTLY.md',
    'EXCHANGE/DS_031_NIGHTLY_report.md',
    'EXCHANGE/DS_054_AI-fallback_черновик.md',
}

# DS_CNT_014: исключить не-MD файлы в корне проекта
ROOT_EXCLUDE_GLOBS = {'*.py', '*.ps1', '*.yml', '*.json', '*.txt', '*.cmd', '*.sh'}

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB
