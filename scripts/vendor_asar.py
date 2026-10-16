"""Embarque 'asar' et ses dependances dans <projet>/build/tools/node_modules.

Apres cela, plus besoin de `npx asar` ni d'internet : le projet est autonome.
Ne copie que la fermeture de dependances necessaire (14 paquets), pas tout
node_modules.
"""
import os, json, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

# Source configurable : variable d'environnement, sinon emplacements usuels.
def find_src_node_modules():
    forced = os.environ.get('NODE_MODULES_SRC')
    if forced and os.path.isdir(forced):
        return forced
    candidates = [
        os.path.join(os.path.expanduser('~'), 'node_modules'),
        os.path.join(paths.ROOT, 'node_modules'),
    ]
    # derniere tentative : node_modules global de npm
    try:
        import subprocess
        out = subprocess.run('npm root -g', shell=True, capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            candidates.append(out.stdout.strip())
    except Exception:
        pass
    for c in candidates:
        if os.path.isdir(os.path.join(c, 'asar')):
            return c
    return candidates[0]

SRC_NM = find_src_node_modules()          # node_modules d'origine (a trouver)
DEST_NM = os.path.join(paths.TOOLS, 'node_modules')

if not os.path.isdir(os.path.join(SRC_NM, 'asar')):
    raise SystemExit(
        f"'asar' introuvable dans {SRC_NM}.\n"
        "Installez-le (npm install asar) ou definissez NODE_MODULES_SRC."
    )

os.makedirs(DEST_NM, exist_ok=True)

def deps_of(pkg_dir):
    pj = os.path.join(pkg_dir, 'package.json')
    if not os.path.isfile(pj):
        return []
    try:
        d = json.load(open(pj, encoding='utf-8'))
    except Exception:
        return []
    return list(d.get('dependencies', {}).keys())

# fermeture depuis asar
seen, stack = set(), ['asar']
while stack:
    name = stack.pop()
    if name in seen:
        continue
    seen.add(name)
    stack.extend(deps_of(os.path.join(SRC_NM, name)))

copied = []
for name in sorted(seen):
    src = os.path.join(SRC_NM, name)
    if not os.path.isdir(src):
        print('  MANQUANT', name)
        continue
    dst = os.path.join(DEST_NM, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    copied.append(name)
    print('  copié', name)

total = 0
for root, dirs, files in os.walk(DEST_NM):
    for f in files:
        total += os.path.getsize(os.path.join(root, f))

print()
print('paquets embarqués :', len(copied))
print('taille totale     :', f'{total:,} o ({total/1024:.0f} Ko)')
print('asar.js présent   :', os.path.isfile(paths.ASAR_JS))
