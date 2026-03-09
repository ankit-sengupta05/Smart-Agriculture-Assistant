# scripts/mask_keys.py
import re
from pathlib import Path

SECRET_PATTERNS = [
    r'(_KEY|_SECRET|_TOKEN|API_KEY|PASSWORD)=[^\s]+',
]

# Scan all files recursively in the repo
for file_path in Path('.').rglob('*'):
    if file_path.is_file():
        try:
            content = file_path.read_text(errors='ignore')
        except Exception:
            continue
        original = content
        for pattern in SECRET_PATTERNS:
            content = re.sub(
                pattern,
                lambda m: m.group(0).split('=')[0] + '=******',
                content
            )
        if content != original:
            file_path.write_text(content)
