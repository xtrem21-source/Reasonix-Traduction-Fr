"""Fusionne les traductions en fr_dict.json.

Format des morceaux : build/fr_parts/<nom>.json doit etre un TABLEAU de chaines
françaises, dans le meme ordre que build/extracted/<nom>.json.
-> economise la reecriture des cles chinoises.

Un morceau peut aussi etre un OBJET { "chinois": "français" } (mode explicite).

Usage: python3 merge_fr.py [--write]
"""
import os, json, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACTED = paths.EXTRACTED
PARTS = paths.FR_PARTS
OUT = paths.FR_DICT

write = '--write' in sys.argv

# Catalogue source : par fichier, liste ordonnee des cles chinoises
src_by_file = {}
all_keys = set()
for p in sorted(glob.glob(os.path.join(EXTRACTED, '*.json'))):
    name = os.path.basename(p)
    keys = [e['key'] for e in json.load(open(p, encoding='utf-8'))]
    src_by_file[name] = keys
    all_keys |= set(keys)

merged = {}
problems = []
for p in sorted(glob.glob(os.path.join(PARTS, '*.json'))):
    name = os.path.basename(p)
    data = json.load(open(p, encoding='utf-8'))
    if isinstance(data, dict):
        for k, v in data.items():
            if k in all_keys:
                merged[k] = v
            else:
                problems.append((name, 'cle inconnue', k))
        n = len(data)
    elif isinstance(data, list):
        src = src_by_file.get(name)
        if src is None:
            problems.append((name, 'pas de catalogue source', ''))
            continue
        if len(data) != len(src):
            problems.append((name, f'longueur {len(data)} != {len(src)}', ''))
        for k, v in zip(src, data):
            if v:
                merged[k] = v
        n = len(data)
    else:
        problems.append((name, 'type invalide', type(data).__name__))
        continue
    print(f'  {name:28} {n:>5}')

print()
print('Total chaines sources :', len(all_keys))
print('Total traduites       :', len(merged))
print('Restant               :', len(all_keys) - len(merged))
if problems:
    print('\nPROBLEMES:')
    for pr in problems[:20]:
        print('  !', pr)

# par fichier : combien il reste
print('\nPar fichier (reste / total):')
for name, keys in src_by_file.items():
    done = sum(1 for k in keys if k in merged)
    flag = 'OK ' if done == len(keys) else '...'
    print(f'  {flag} {name:28} {len(keys)-done:>5} / {len(keys)}')

if write:
    json.dump(merged, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('\nEcrit', OUT)
