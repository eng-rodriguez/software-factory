#!/usr/bin/env python3
"""Check upstream tag changes; --write updates pins after reviewing upstream releases.

Includes templates, which GitHub's normal Dependabot workflow scan can miss.
Only reads public Git refs; never executes downloaded action code.
"""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = re.compile(r'(uses:\s+)([\w.-]+/[\w./-]+)@([0-9a-f]{40})\s+# ([\w.-]+)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    resolved = {}
    updates = {}
    files = list((ROOT / '.github/workflows').glob('*.yml'))
    files += list((ROOT / 'plugins/factory/skills/devsecops-gha/templates').glob('*.yml'))
    for path in files:
        original = path.read_text()

        def replace(match):
            prefix, repo, old, tag = match.groups()
            key = (repo, tag)
            if key not in resolved:
                result = subprocess.run(['git', 'ls-remote', f'https://github.com/{repo}.git',
                    f'refs/tags/{tag}', f'refs/tags/{tag}^{{}}'],
                    check=True, text=True, capture_output=True, timeout=30)
                refs = dict(line.split()[::-1] for line in result.stdout.splitlines())
                sha = refs.get(f'refs/tags/{tag}^{{}}', refs.get(f'refs/tags/{tag}', ''))
                if not re.fullmatch('[0-9a-f]{40}', sha):
                    raise ValueError(f'Missing upstream tag: {repo}@{tag}; review its release history')
                resolved[key] = sha
            new = resolved[key]
            if new != old:
                print(f'{path.relative_to(ROOT)}: {repo}@{tag} {old} -> {new}')
            return f'{prefix}{repo}@{new} # {tag}'

        updated = PIN.sub(replace, original)
        if updated != original:
            updates[path] = updated
    # Resolve everything before writing anything. A moved tag is not proof of safety.
    if args.write:
        for path, updated in updates.items():
            path.write_text(updated)
    elif updates:
        print('Review upstream release/advisory history before using --write.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
