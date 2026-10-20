"""Traduit les descriptions d'outils venues du noyau Go (2.46.0).

Les descriptions sont affichees telles quelles par l'interface (`e.description`),
sans passer par le dictionnaire : elles sont compilees dans le binaire Go.
Ce script ajoute une table EN -> FR dans le bundle Settings et fait passer
l'affichage par une fonction de traduction tolerante aux espaces et aux
variantes de prefixe.

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

# 1. Faire passer l'affichage par la fonction de traduction.
#    Deux formes possibles : le lookup simple (version precedente) ou rien.
OLD_LOOKUP = 'title:globalThis.__TOOLDESC?.[e.description]??e.description,children:globalThis.__TOOLDESC?.[e.description]??e.description}'
OLD_RAW = 'title:e.description,children:e.description}'
NEW = ('title:globalThis.__TOOLFR?.(e.description)??e.description,'
       'children:globalThis.__TOOLFR?.(e.description)??e.description}')
changed = False
if s.count(NEW) == 1:
    print('  affichage : deja patche (fonction)')
elif s.count(OLD_LOOKUP) == 1:
    s = s.replace(OLD_LOOKUP, NEW, 1)
    print('  affichage : lookup -> fonction')
    changed = True
elif s.count(OLD_RAW) == 1:
    s = s.replace(OLD_RAW, NEW, 1)
    print('  affichage : patche')
    changed = True
else:
    raise SystemExit(f'ancre introuvable (lookup={s.count(OLD_LOOKUP)}, brut={s.count(OLD_RAW)})')

# 2. Remplacer / ajouter la table et la fonction.
js = json.dumps(table, ensure_ascii=False)
block = (
    ';globalThis.__TOOLDESC=' + js + ';'
    'globalThis.__TOOLFR=(s)=>{'
    'const d=globalThis.__TOOLDESC;'
    'if(!s)return s;'
    'if(d[s])return d[s];'
    'const n=(x)=>String(x||"").replace(/\\s+/g," ").trim();'
    'const k=n(s);'
    'for(const [a,b] of Object.entries(d)){if(n(a)===k)return b}'
    'for(const [a,b] of Object.entries(d)){const p=n(a);if(p.slice(0,60)===k.slice(0,60))return b}'
    'return s};'
)
if ';globalThis.__TOOLDESC=' in s:
    s2 = re.sub(r';globalThis\.__TOOLDESC=\{.*?\};\s*(?:globalThis\.__TOOLFR=.*?;\s*)?$',
                lambda m: block, s, count=1, flags=re.S)
    if s2 != s:
        s = s2
        changed = True
    print('  table : mise a jour')
else:
    s = s + '\n' + block + '\n'
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
