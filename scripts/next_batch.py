"""Affiche un lot de chaines anglaises a traduire (une par ligne, numerotee).

N'affiche QUE la valeur anglaise : la cle chinoise est implicite (l'ordre du
morceau de traduction doit correspondre a l'ordre du catalogue extrait).

Usage:
  python3 next_batch.py                 # prochain lot, tous fichiers
  python3 next_batch.py --file en_usage.json   # un fichier precis, en entier
  python3 next_batch.py 80              # lot de 80
"""
import os, json, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACTED = paths.EXTRACTED
PARTS = paths.FR_PARTS

n = 60
only = None
args = sys.argv[1:]
for i, a in enumerate(args):
    if a == '--file':
        only = args[i+1]
    elif a.startswith('--file='):
        only = a.split('=', 1)[1]
    elif a.isdigit():
        n = int(a)

def done_for(name):
    p = os.path.join(PARTS, name)
    if os.path.isfile(p):
        d = json.load(open(p, encoding='utf-8'))
        if isinstance(d, list):
            return len(d)
        return len(d)
    return 0

files = sorted(glob.glob(os.path.join(EXTRACTED, '*.json')))
if only:
    files = [f for f in files if os.path.basename(f) == only]

total_left = 0
for f in files:
    name = os.path.basename(f)
    rows = json.load(open(f, encoding='utf-8'))
    d = done_for(name)
    total_left += max(0, len(rows) - d)

print(f'# total restant (selon fr_parts): {total_left}')

shown = 0
for f in files:
    name = os.path.basename(f)
    rows = json.load(open(f, encoding='utf-8'))
    d = done_for(name)
    if d >= len(rows):
        continue
    print(f'\n### {name}   (fait {d} / {len(rows)})')
    for e in rows[d:]:
        print(f'{shown+1:>4}. {e["value"]}')
        shown += 1
        if shown >= n and not only:
            break
    if shown >= n and not only:
        break
print(f'\n# {shown} lignes affichees')
