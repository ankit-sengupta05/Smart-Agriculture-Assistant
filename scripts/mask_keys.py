# scripts/mask_keys.py
import re
from pathlib import Path

# Patterns to detect secrets
SECRET_PATTERNS = [
    r'(_KEY|_SECRET|_TOKEN|API_KEY|PASSWORD)=[^\s]+',
]

# Scan all files recursively for .env, .py, or .txt
for file_path in Path('.').rglob('*'):
    if file_path.is_file() and file_path.suffix in ['.env', '.py', '.txt']:
        content = file_path.read_text()
        original = content
        for pattern in SECRET_PATTERNS:
            content = re.sub(
                pattern,
                lambda m: m.group(0).split('=')[0] + '=******',
                content
            )
        if content != original:
            file_path.write_text(content)
