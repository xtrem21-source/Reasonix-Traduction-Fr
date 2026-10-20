"""Traduit les descriptions d'outils venues du noyau Go (2.46.0).

Les descriptions sont affichees telles quelles par l'interface, sans passer par
le dictionnaire : elles sont compilees dans le binaire Go. Ce script ajoute une
table EN -> FR dans le bundle Settings et fait passer les deux rendus
(la liste des outils et la liste des contributions) par une fonction tolerante
aux espaces et aux variantes de prefixe.

Usage: python3 patch_tools_246.py [--dry-run]
"""
import glob, os, re, shutil, sys, json, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
from log_246 import log

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

FUNC = 'globalThis.__TOOLFR?.(e.description)??e.description'

# 1. Liste des outils : ternaire e.byProject ? ... : e.description
OLD_LISTE = ('e.byProject?o(`这个项目的配置文件把它关掉了；要重新打开，请在项目的 '
             'reasonix.toml 里去掉。`):e.description})]}')
NEW_LISTE = ('e.byProject?o(`这个项目的配置文件把它关掉了；要重新打开，请在项目的 '
             'reasonix.toml 里去掉。`):' + FUNC + '})]}')

# 2. Liste des contributions : title/children
OLD_CONTRIB = 'title:e.description,children:e.description}'
NEW_CONTRIB = f'title:{FUNC},children:{FUNC}}}'

# Anciennes formes deja appliquees (pour l'idempotence).
OLD_FUNC = ('title:globalThis.__TOOLFR?.(e.description)??e.description,'
            'children:globalThis.__TOOLFR?.(e.description)??e.description}')
OLD_LOOKUP = ('title:globalThis.__TOOLDESC?.[e.description]??e.description,'
              'children:globalThis.__TOOLDESC?.[e.description]??e.description}')

changed = False

if s.count(NEW_LISTE) == 1:
    print('  liste des outils : deja patchee')
elif s.count(OLD_LISTE) == 1:
    s = s.replace(OLD_LISTE, NEW_LISTE, 1)
    print('  liste des outils : patchee')
    changed = True
else:
    print(f'  !! liste des outils : ancre introuvable ({s.count(OLD_LISTE)})')

if s.count(NEW_CONTRIB) == 1:
    print('  contributions : deja patchees')
elif s.count(OLD_CONTRIB) == 1:
    s = s.replace(OLD_CONTRIB, NEW_CONTRIB, 1)
    print('  contributions : patchees')
    changed = True
elif s.count(OLD_FUNC) == 1 or s.count(OLD_LOOKUP) == 1:
    s = s.replace(OLD_FUNC if s.count(OLD_FUNC) == 1 else OLD_LOOKUP, NEW_CONTRIB, 1)
    print('  contributions : lookup -> fonction')
    changed = True
else:
    print(f'  !! contributions : ancre introuvable')

# 3. Table + fonction, en fin de fichier.
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
    log('outils-descriptions', 'aucun changement (deja applique)')
    raise SystemExit(0)
if dry:
    print('(dry-run : rien ecrit)')
    log('outils-descriptions', 'dry-run')
    raise SystemExit(0)

os.makedirs(BACKUP, exist_ok=True)
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
dst = os.path.join(BACKUP, f'{stamp}__{os.path.basename(p)}')
shutil.copy2(p, dst)
open(p, 'w', encoding='utf-8').write(s)
print('sauvegarde :', os.path.basename(dst))
log('outils-descriptions', f'{len(table)} descriptions, sauvegarde {os.path.basename(dst)}')
