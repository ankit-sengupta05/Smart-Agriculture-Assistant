# scripts/check_requirements.py
from pathlib import Path
import sys

req_file = Path('requirements.txt')
if req_file.exists():
    for i, line in enumerate(req_file.read_text().splitlines(), start=1):
        if not line.strip():
            print(f'Error: Empty line at {i} in requirements.txt')
            sys.exit(1)
