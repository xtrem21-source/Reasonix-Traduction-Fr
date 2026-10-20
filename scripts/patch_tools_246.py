"""Traduit les descriptions d'outils venues du noyau Go (2.46.0).

Les descriptions sont affichees telles quelles par l'interface (`e.description`),
sans passer par le dictionnaire : elles sont compilees dans le binaire Go.
Ce script ajoute une table EN -> FR dans le bundle Settings et fait passer
l'affichage par cette table.

Usage: python3 patch_tools_246.py [--dry-run]
"""
import glob, os, re, shutil, sys, json, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ASSETS = paths.app_assets()
HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, 'tool_desc_246.json')
BACKUP = paths.BACKUP

hits = glob.glob(os.path.join(ASSETS, 'Settings-*.js'))
if len(hits) != 1:
    raise SystemExit(f'Settings bundle introuvable ou multiple : {hits}')
p = hits[0]
s = open(p, encoding='utf-8').read()
dry = '--dry-run' in sys.argv

table = json.load(open(TABLE, encoding='utf-8'))
print('descriptions FR :', len(table))

# 1. Faire passer l'affichage par la table.
OLD = 'title:e.description,children:e.description}'
NEW = ('title:globalThis.__TOOLDESC?.[e.description]??e.description,'
       'children:globalThis.__TOOLDESC?.[e.description]??e.description}')
changed = False
if s.count(NEW) == 1:
    print('  affichage : deja patche')
elif s.count(OLD) == 1:
    s = s.replace(OLD, NEW, 1)
    print('  affichage : patche')
    changed = True
else:
    raise SystemExit(f'ancre introuvable (attendu 1, trouve {s.count(OLD)}): {OLD!r}')

# 2. Ajouter / mettre a jour la table globale.
js = json.dumps(table, ensure_ascii=False)
if ';globalThis.__TOOLDESC=' in s:
    s2 = re.sub(r';globalThis\.__TOOLDESC=\{.*?\};\s*$', ';globalThis.__TOOLDESC=' + js + ';', s, count=1, flags=re.S)
    if s2 != s:
        s = s2
        changed = True
    print('  table : mise a jour')
else:
    s = s + '\n;globalThis.__TOOLDESC=' + js + ';\n'
    print('  table : ajoutee')
    changed = True

if not changed:
    print('aucun changement')
    raise SystemExit(0)
if dry:
    print('(dry-run : rien ecrit)')
    raise SystemExit(0)

os.makedirs(BACKUP, exist_ok=True)
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
dst = os.path.join(BACKUP, f'{stamp}__{os.path.basename(p)}')
shutil.copy2(p, dst)
open(p, 'w', encoding='utf-8').write(s)
print('sauvegarde :', os.path.basename(dst))
