"""Extrait les paires cle->valeur des catalogues TS en JSON.

Sortie: Desktop/DEV/build/extracted/<nom>.json  (liste de {key, value})
Gere les chaines TS a guillemets doubles avec echappements et placeholders {n}.
"""
import os, re, json, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SRC = os.path.join(paths.SOURCES, 'frontend-i18n')
OUT = paths.EXTRACTED
os.makedirs(OUT, exist_ok=True)

# Un litteral de chaine TS a guillemets doubles, avec echappements.
STR = r'"(?:[^"\\]|\\.)*"'

PAIR = re.compile(r'(' + STR + r')\s*:\s*(' + STR + r')\s*,?')

def unescape(ts_lit):
    body = ts_lit[1:-1]
    out = []
    i = 0
    while i < len(body):
        c = body[i]
        if c == '\\' and i + 1 < len(body):
            nxt = body[i+1]
            mapping = {'n': '\n', 't': '\t', '"': '"', '\\': '\\', "'": "'", 'r': '\r'}
            out.append(mapping.get(nxt, nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)

total = 0
summary = []
for name in sorted(os.listdir(SRC)):
    if not name.endswith('.ts'):
        continue
    # On ne garde que les fichiers de catalogue (en*.ts) : les autres (index, format, kernel)
    if not name.startswith('en'):
        continue
    path = os.path.join(SRC, name)
    raw = open(path, encoding='utf-8').read()
    pairs = []
    seen = set()
    for m in PAIR.finditer(raw):
        k = unescape(m.group(1))
        v = unescape(m.group(2))
        if k in seen:
            continue
        seen.add(k)
        pairs.append({'key': k, 'value': v})
    with open(os.path.join(OUT, name.replace('.ts', '.json')), 'w', encoding='utf-8') as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)
    total += len(pairs)
    summary.append((name, len(pairs)))
    print(f'{name:24} {len(pairs):>5} paires')

print()
print('TOTAL paires en*:', total)
print('Fichiers JSON ecrits dans:', OUT)
