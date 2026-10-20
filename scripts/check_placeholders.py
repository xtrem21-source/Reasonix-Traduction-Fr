"""Fail if a translation loses, renames, or invents a `{placeholder}`.

The dictionary keys are the Chinese source strings; the values are the French
translations. A placeholder present in the key must appear, unchanged, in the
value — and the other way round.

Usage: python3 scripts/check_placeholders.py [dict.json]
Exit code 0 when every entry preserves its placeholders, 1 otherwise.
"""
import os, json, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

DICT = paths.FR_DICT
for a in sys.argv[1:]:
    if a.endswith('.json'):
        DICT = a

PH = re.compile(r'\{(\w+)\}')

if not os.path.isfile(DICT):
    raise SystemExit(f'dictionary not found: {DICT}')

data = json.load(open(DICT, encoding='utf-8'))
bad = []
for zh, fr in data.items():
    want = sorted(PH.findall(zh))
    got = sorted(PH.findall(fr or ''))
    if want != got:
        bad.append((zh, fr, want, got))

print(f'dictionary     : {DICT}')
print(f'entries checked: {len(data)}')
print(f'placeholder mismatches: {len(bad)}')
for zh, fr, want, got in bad[:40]:
    print(f'  zh={zh!r}')
    print(f'  fr={fr!r}')
    print(f'  expected={want} got={got}')
    print()

sys.exit(1 if bad else 0)
