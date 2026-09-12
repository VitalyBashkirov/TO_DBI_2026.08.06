#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exchange Bot - Pure Courier Mode (Variant C)
Runs every 15 seconds, checks INBOX, saves task copies to OUTBOX, archives processed.
"""

import os
import shutil
import time
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent / 'EXCHANGE'
INBOX = BASE_DIR / 'INBOX'
OUTBOX = BASE_DIR / 'OUTBOX'
PROCESSED = BASE_DIR / 'PROCESSED'

# Log file
LOG_FILE = BASE_DIR / 'bot.log'

# Create folders
for folder in [INBOX, OUTBOX, PROCESSED]:
    folder.mkdir(parents=True, exist_ok=True)


def write_log(message: str):
    """Write message to log file (2 MB limit)"""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 2 * 1024 * 1024:
        print(f"[INFO] Log file too large. Stopping logging.")
        return
    # ВАЖНО: используем newline='\r\n' для Windows CR LF
    with open(LOG_FILE, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")


def process_task(task_file: Path, content: str):
    """
    Pure courier: save a copy of the task to OUTBOX and archive the original.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing task: {task_file.name}")
    write_log(f"[{datetime.now().strftime('%H:%M:%S')}] Processing task: {task_file.name}")
    
    # Save copy of task to OUTBOX
    response_filename = f"response_{task_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    response_path = OUTBOX / response_filename
    
    response = {
        'status': 'courier_success',
        'task': task_file.name,
        'received_at': datetime.now().isoformat(),
        'content': content,
        'note': 'Task received. Koda will read this and execute according to AGENTS.md.'
    }
    
    # ВАЖНО: используем newline='\r\n' для Windows CR LF
    with open(response_path, 'w', encoding='utf-8', newline='\r\n') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
    
    print(f"[+] Response saved: {response_path}")
    write_log(f"[+] Response saved: {response_path}")
    
    # Move task to archive
    shutil.move(str(task_file), str(PROCESSED / task_file.name))
    print(f"[+] Task moved to archive: {PROCESSED / task_file.name}")
    write_log(f"[+] Task moved to archive: {PROCESSED / task_file.name}")


def main():
    """
    Continuous courier: watches INBOX every 15 seconds.
    """
    print(f"[INFO] Exchange Courier started (continuous mode)")
    print(f"[INFO] Watching: {INBOX}")
    print(f"[INFO] Saving to: {OUTBOX}")
    print(f"[INFO] Log file: {LOG_FILE}")
    print(f"[INFO] Press Ctrl+C to stop\n")
    
    write_log("[INFO] Exchange Courier started (continuous mode)")
    
    while True:
        # Check INBOX for tasks
        tasks = list(INBOX.glob('*'))
        
        if tasks:
            print(f"[INFO] Found {len(tasks)} task(s).")
            write_log(f"[INFO] Found {len(tasks)} task(s).")
            
            for task_file in tasks:
                try:
                    # Read file with encoding detection
                    try:
                        with open(task_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        try:
                            with open(task_file, 'r', encoding='cp1251') as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            with open(task_file, 'r', encoding='latin-1') as f:
                                content = f.read()
                    
                    process_task(task_file, content)
                    
                except Exception as e:
                    print(f"[ERROR] Error processing {task_file.name}: {e}")
                    write_log(f"[ERROR] Error processing {task_file.name}: {e}")
                    
                    # Save error to OUTBOX
                    error_response = {
                        'status': 'error',
                        'task': task_file.name,
                        'error': str(e)
                    }
                    error_path = OUTBOX / f"error_{task_file.stem}.json"
                    with open(error_path, 'w', encoding='utf-8', newline='\r\n') as f:
                        json.dump(error_response, f, ensure_ascii=False, indent=2)
        
        # Wait 15 seconds
        time.sleep(15)


if __name__ == '__main__':
    main()