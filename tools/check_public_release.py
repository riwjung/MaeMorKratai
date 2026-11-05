#!/usr/bin/env python3
"""Inspect staged Git blobs for private files and common credential patterns.

This is a sharing guard, not a full security audit or a scan of Git history.
Only file/line/rule are printed; matching values are never echoed.
"""
import re
import subprocess
from pathlib import Path

root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
names = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z'], cwd=root).decode().split('\0')
rules = {
    'supabase-secret': re.compile(r'sb_secret_[A-Za-z0-9_-]{20,}'),
    'github-token': re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
    'provider-secret': re.compile(r'(?:sk_live_[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{30,}|xox[baprs]-[A-Za-z0-9-]{20,})'),
    'private-key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'jwt-like-token': re.compile(r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}'),
    'personal-mailbox': re.compile(r'[A-Za-z0-9._%+-]+@(?:gmail|hotmail|outlook|yahoo)\.com', re.I),
    'credential-in-url': re.compile(r'(?:postgres(?:ql)?|https?)://[^\s/:@]+:[^\s/@]+@'),
}
forbidden = {'.vercel', 'node_modules', '.next', '.venv', 'raw', 'backups', 'knowledge-prep', 'knowledge-intake', 'browser-profile'}
errors = []
count = 0
for name in filter(None, names):
    path = Path(name)
    if set(path.parts) & forbidden or path.suffix.lower() in {'.db', '.sqlite', '.sqlite3', '.pem', '.key', '.wav', '.mp3', '.zip'}:
        errors.append((name, 0, 'private-file'))
    if path.name.startswith('.env') and path.name != '.env.example':
        errors.append((name, 0, 'environment-file'))
    data = subprocess.check_output(['git', 'show', ':' + name], cwd=root)
    count += 1
    if len(data) > 25 * 1024 * 1024:
        errors.append((name, 0, 'large-artifact'))
    if b'\0' in data[:8192]:
        continue
    for number, line in enumerate(data.decode('utf-8', errors='replace').splitlines(), 1):
        for rule, pattern in rules.items():
            if pattern.search(line):
                # Manually reviewed credential-rejection test, not an account URL.
                if (rule == 'credential-in-url'
                        and name == 'services/social-center/tests/test_data.py'
                        and line.endswith('# public-release: synthetic URL rejection fixture')
                        and "@cdninstagram.com/a.jpg')==''" in line):
                    continue
                errors.append((name, number, rule))
for name, number, rule in errors:
    print(f'{name}:{number}: {rule}')
if errors:
    raise SystemExit(1)
print(f'PASS: {count} staged files checked; no blocked files/common credential patterns/personal mailboxes found')
