"""Verifie app_fr.asar avant installation.

1. Liste des fichiers identique a l'original ?
2. En-tete asar valide (JSON) ?
3. Chaque JS patché s'extrait et passe node --check.
"""
import os, json, struct, subprocess, tempfile, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ORIG = paths.app_asar()
NEW = paths.APP_FR_ASAR
TMP = os.path.join(paths.BUILD, 'asar_check')

def read_header(path):
    with open(path, 'rb') as f:
        # asar: 4 x uint32 pickle, puis la taille du JSON, puis le JSON
        pickle = f.read(16)
        if len(pickle) < 16:
            raise SystemExit('fichier trop court')
        # 'asar' magic is the 5th..8th byte area; simpler: locate '{'
        f.seek(0)
        data = f.read()
    i = data.find(b'{', 4)
    depth = 0
    j = i
    while j < len(data):
        if data[j] == ord('{'):
            depth += 1
        elif data[j] == ord('}'):
            depth -= 1
            if depth == 0:
                break
        j += 1
    return json.loads(data[i:j+1].decode('utf-8')), i, j

def walk(node, prefix=''):
    out = []
    for name, info in node.get('files', {}).items():
        p = f'{prefix}/{name}'
        if 'files' in info:
            out += walk(info, p)
        else:
            out.append(p)
    return out

ho, _, _ = read_header(ORIG)
hn, _, _ = read_header(NEW)
lo, ln = sorted(walk(ho)), sorted(walk(hn))
print('fichiers original :', len(lo))
print('fichiers nouveau  :', len(ln))
print('ensembles identiques :', lo == ln)
if lo != ln:
    print('  manquants:', [x for x in lo if x not in ln][:10])
    print('  ajoutes  :', [x for x in ln if x not in lo][:10])

print()
print('=== extraction + node --check des fichiers patches ===')
if os.path.isdir(TMP):
    import shutil; shutil.rmtree(TMP)
os.makedirs(TMP, exist_ok=True)
r = subprocess.run(f'{paths.asar_prefix()} extract "{NEW}" "{TMP}"', shell=True, capture_output=True, text=True)
print('extract exit', r.returncode, r.stderr[-200:])

MOD = ['uilang.js','starting.js','editmenu.js','hostexit.js','shelllog.js',
       'packagegrants.js','main.js','tray.js']
bad = 0
for f in MOD:
    p = os.path.join(TMP, 'src', f)
    if not os.path.isfile(p):
        print(f'  MANQUANT {f}'); bad += 1; continue
    rc = subprocess.run(f'node --check "{p}"', shell=True, capture_output=True, text=True)
    if rc.returncode != 0:
        bad += 1
        print(f'  ERR {f}: {rc.stderr.strip()[:120]}')
    else:
        # verifier que la traduction est bien la
        t = open(p, encoding='utf-8').read()
        mark = {'starting.js': 'Reasonix Studio démarre',
                'editmenu.js': 'Tout sélectionner',
                'tray.js': 'Ouvrir Reasonix Studio',
                'hostexit.js': "Le noyau s'est arrêté",
                'uilang.js': 'isFrench'}.get(f)
        ok = (mark in t) if mark else True
        print(f'  {"OK " if ok else "?? "} {f}' + ('' if ok else '  (traduction non trouvee)'))
        if mark and not ok:
            bad += 1

print()
print('VERDICT:', 'OK' if (lo == ln and bad == 0) else 'PROBLEME')
