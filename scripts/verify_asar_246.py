"""Verify app_fr_246.asar before installation (Reasonix Studio 2.46.0).

1. Is the file list identical to the installed original?
2. Does every patched JS pass `node --check` and carry its translation?
"""
import os, json, subprocess, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ORIG = paths.app_asar()
NEW = os.path.join(paths.WORK, 'app_fr_246.asar')
TMP = os.path.join(paths.WORK, 'asar_check_246')


def read_header(path):
    with open(path, 'rb') as f:
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
    return json.loads(data[i:j + 1].decode('utf-8'))


def walk(node, prefix=''):
    out = []
    for name, info in node.get('files', {}).items():
        p = f'{prefix}/{name}'
        if 'files' in info:
            out += walk(info, p)
        else:
            out.append(p)
    return out


ho = read_header(ORIG)
hn = read_header(NEW)
lo, ln = sorted(walk(ho)), sorted(walk(hn))
print('original files :', len(lo))
print('new files      :', len(ln))
print('identical sets :', lo == ln)
if lo != ln:
    print('  missing:', [x for x in lo if x not in ln][:10])
    print('  added  :', [x for x in ln if x not in lo][:10])

print()
print('=== extraction + node --check of patched files ===')
if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP, exist_ok=True)
r = subprocess.run(f'{paths.asar_prefix()} extract "{NEW}" "{TMP}"', shell=True,
                   capture_output=True, text=True)
print('extract exit', r.returncode)
if r.returncode != 0:
    print(r.stderr[-400:])
    raise SystemExit(1)

MOD = ['uilang.js', 'starting.js', 'editmenu.js', 'hostexit.js', 'shelllog.js',
       'packagegrants.js', 'main.js', 'tray.js']
bad = 0
for f in MOD:
    p = os.path.join(TMP, 'src', f)
    if not os.path.isfile(p):
        print(f'  MISSING {f}')
        bad += 1
        continue
    rc = subprocess.run(f'node --check "{p}"', shell=True, capture_output=True, text=True)
    if rc.returncode != 0:
        bad += 1
        print(f'  ERR {f}: {rc.stderr.strip()[:120]}')
    else:
        t = open(p, encoding='utf-8').read()
        mark = {'starting.js': 'Reasonix Studio démarre',
                'editmenu.js': 'Tout sélectionner',
                'tray.js': 'Ouvrir Reasonix Studio',
                'hostexit.js': "Le noyau s'est arrêté",
                'uilang.js': 'isFrench',
                'shelllog.js': "n'a pas pu démarrer",
                'packagegrants.js': "n'a pas pu ouvrir sa fenêtre",
                'main.js': 'Placer dans la corbeille'}.get(f)
        ok = (mark in t) if mark else True
        print(f'  {"OK " if ok else "?? "} {f}' + ('' if ok else '  (translation not found)'))
        if mark and not ok:
            bad += 1

print()
print('VERDICT:', 'OK' if (lo == ln and bad == 0) else 'PROBLEM')
sys.exit(0 if (lo == ln and bad == 0) else 1)
