"""Verifie que chaque traduction preserve les placeholders {..} de la source.

Compare l'ensemble des placeholders du chinois source et de la traduction FR.
Signale tout ecart (placeholder perdu, renomme ou ajoute).

Usage: python3 check_placeholders.py
Sortie: 0 si tout est bon, 1 sinon
"""
import os, json, glob, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACTED = paths.EXTRACTED
PARTS = paths.FR_PARTS

PH = re.compile(r'\{(\w+)\}')

bad = []
checked = 0
for p in sorted(glob.glob(os.path.join(PARTS, '*.json'))):
    name = os.path.basename(p)
    src = json.load(open(os.path.join(EXTRACTED, name), encoding='utf-8'))
    fr = json.load(open(p, encoding='utf-8'))
    if not isinstance(fr, list):
        continue
    for i, (e, f) in enumerate(zip(src, fr)):
        checked += 1
        want = sorted(PH.findall(e['key']))
        got = sorted(PH.findall(f or ''))
        if want != got:
            bad.append((name, i, e['key'][:40], e['value'][:40], f[:40], want, got))

print(f'chaines verifiees : {checked}')
print(f'ecarts de placeholders : {len(bad)}')
for b in bad[:40]:
    print(f'  {b[0]}[{b[1]}] zh={b[2]!r} en={b[3]!r} fr={b[4]!r} attendu={b[5]} obtenu={b[6]}')

sys.exit(1 if bad else 0)
