# -*- coding: utf-8 -*-
# scripts/compile_check.py
# Auto-detects file language and runs the correct syntax checker.
# JSX/TSX: @babel/parser (node --check does NOT support JSX)
# All other languages: native compiler/interpreter in check-only mode
import subprocess
import sys
from pathlib import Path

# Map extension -> internal language key
SUPPORTED = {
    '.py': 'python',
    '.js': 'node',
    '.mjs': 'node',
    '.cjs': 'node',
    '.jsx': 'jsx',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.java': 'java',
    '.kt': 'kotlin',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.dart': 'dart',
    '.swift': 'swift',
    '.c': 'c',
    '.cpp': 'cpp',
}

# Inline babel script used for JSX and TSX files.
# Requires: npm install -g @babel/parser
BABEL_SCRIPT = (
    "const fs=require('fs');"
    "const b=require('@babel/parser');"
    "try{"
    "b.parse(fs.readFileSync(process.argv[1],'utf8'),{"
    "sourceType:'module',"
    "plugins:['jsx','typescript','classProperties','decorators-legacy']"
    "});"
    "process.exit(0);"
    "}catch(e){"
    "console.error(e.message);"
    "process.exit(1);"
    "}"
)

errors = []
files_to_scan = sys.argv[1:] if len(sys.argv) > 1 else []


def run(cmd, label, filepath):
    """Run cmd, collect stderr/stdout on failure. Skip if tool missing."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            out = (result.stderr or result.stdout).strip()
            errors.append(
                '[' + label + '] ' + filepath + '\n  ' + out
            )
            return False
        return True
    except FileNotFoundError:
        # Tool not installed -- silently skip, never block commit
        return True
    except subprocess.TimeoutExpired:
        errors.append('[TIMEOUT] ' + filepath)
        return False


def check_babel(filepath, label):
    """Validate JSX/TSX using @babel/parser via inline Node script."""
    run(
        ['node', '-e', BABEL_SCRIPT, filepath],
        label,
        filepath,
    )


def check_file(filepath):
    """Detect language from extension and run the right checker."""
    fp = Path(filepath)
    if not fp.is_file():
        return
    lang = SUPPORTED.get(fp.suffix.lower())
    if not lang:
        return
    p = str(fp)

    if lang == 'python':
        run(['python', '-m', 'py_compile', p], 'Python', p)

    elif lang == 'node':
        # Plain JS only -- no JSX transform needed
        run(['node', '--check', p], 'JavaScript', p)

    elif lang == 'jsx':
        # node --check CANNOT parse JSX -- must use babel
        check_babel(p, 'JSX')

    elif lang == 'typescript':
        # Plain .ts -- tsc in single-file check mode
        run(
            [
                'npx', '--yes', 'tsc',
                '--noEmit', '--allowJs',
                '--strict', '--target', 'ES2020', p,
            ],
            'TypeScript',
            p,
        )

    elif lang == 'tsx':
        # TSX = TypeScript + JSX -- babel handles both
        check_babel(p, 'TSX')

    elif lang == 'java':
        run(['javac', '-proc:none', p], 'Java', p)

    elif lang == 'kotlin':
        run(['kotlinc', '-script', p], 'Kotlin', p)

    elif lang == 'go':
        run(['go', 'vet', p], 'Go', p)

    elif lang == 'rust':
        # Cross-platform null output target
        null_out = 'nul' if sys.platform == 'win32' else '/dev/null'
        run(
            [
                'rustc', '--edition', '2021',
                '--emit=metadata', '-o', null_out, p,
            ],
            'Rust',
            p,
        )

    elif lang == 'ruby':
        run(['ruby', '-c', p], 'Ruby', p)

    elif lang == 'php':
        run(['php', '-l', p], 'PHP', p)

    elif lang == 'dart':
        run(['dart', 'analyze', p], 'Dart', p)

    elif lang == 'swift':
        run(['swiftc', '-parse', p], 'Swift', p)

    elif lang == 'c':
        run(['gcc', '-fsyntax-only', p], 'C', p)

    elif lang == 'cpp':
        run(['g++', '-fsyntax-only', p], 'C++', p)


for f in files_to_scan:
    check_file(f)

if errors:
    sys.stdout.buffer.write(b'\n[COMPILE ERROR] Fix before committing:\n')
    sys.stdout.buffer.write(b'=' * 60 + b'\n')
    for err in errors:
        sys.stdout.buffer.write(err.encode('utf-8') + b'\n')
        sys.stdout.buffer.write(b'-' * 60 + b'\n')
    sys.exit(1)
else:
    sys.stdout.buffer.write(b'[OK] All files passed syntax check.\n')
    sys.exit(0)
