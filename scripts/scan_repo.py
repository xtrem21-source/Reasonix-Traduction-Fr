"""Scan the repository for anything that must NOT be published.

Flags four kinds of trouble:

  1. Reasonix artefacts   — *.asar, *.exe, go_messages_en.json, and the minified
                            interface bundles (i18n-*.js, Settings-*.js)
  2. generated / vendored — work/, sources/, node_modules/, tools/, backup/
  3. build noise          — __pycache__/, *.pyc
  4. secrets              — .env

Exit code 0 when clean, 1 when something is found. Safe to run any time;
it only reads.

Usage:
    python3 scripts/scan_repo.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {'.git'}

# Directory names that must not appear in the published tree at all.
BAD_DIRS = {'work', 'sources', 'node_modules', 'tools', 'backup',
            '__pycache__', 'asar_orig', 'asar_fr', 'extracted', 'fr_parts'}

# File names or patterns that must not appear.
BAD_FILES = re.compile(
    r'(\.asar$|\.exe$|\.pyc$'
    r'|^go_messages.*\.json$'
    r'|^i18n-.*\.js$'
    r'|^Settings-.*\.js$'
    r'|^\.env$)',
    re.IGNORECASE,
)


def main():
    findings = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)

        # Do not descend into .git, but DO report any other forbidden directory.
        for d in list(dirnames):
            if d in SKIP_DIRS:
                dirnames.remove(d)
                continue
            if d in BAD_DIRS:
                findings.append(('directory', os.path.join(rel, d)))
                dirnames.remove(d)          # no need to list its contents

        for f in filenames:
            if BAD_FILES.search(f):
                findings.append(('file', os.path.join(rel, f)))

    print(f'scanning: {ROOT}')
    print()
    if not findings:
        print('CLEAN — nothing that must not be published was found.')
        return 0

    print(f'FOUND {len(findings)} thing(s) that must not be published:')
    for kind, path in sorted(findings):
        print(f'  [{kind}] {path}')
    print()
    print('These are covered by .gitignore, so `git status` should not show them —')
    print('but confirm, and delete anything you did not expect to be there.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
