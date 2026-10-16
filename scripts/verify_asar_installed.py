"""Verifie l'app.asar INSTALLE : extraction, syntaxe, et presence des traductions."""
import os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

TARGET = paths.app_asar()
TMP = os.path.join(paths.BUILD, 'asar_installed_check')

print('app.asar installe :', os.path.getsize(TARGET), 'octets')

if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP)

r = subprocess.run(f'{paths.asar_prefix()} extract "{TARGET}" "{TMP}"', shell=True,
                   capture_output=True, text=True)
print('extract exit:', r.returncode)

MARKS = {
    'starting.js': 'Reasonix Studio démarre',
    'editmenu.js': 'Tout sélectionner',
    'tray.js': 'Ouvrir Reasonix Studio',
    'hostexit.js': "Le noyau s'est arrêté",
    'shelllog.js': "n'a pas pu démarrer",
    'packagegrants.js': "n'a pas pu ouvrir sa fenêtre",
    'main.js': "Une ancienne version de Reasonix Studio",
    'uilang.js': 'isFrench',
}
bad = 0
for f, mark in MARKS.items():
    p = os.path.join(TMP, 'src', f)
    if not os.path.isfile(p):
        print(f'  MANQUANT {f}'); bad += 1; continue
    rc = subprocess.run(f'node --check "{p}"', shell=True, capture_output=True, text=True)
    t = open(p, encoding='utf-8').read()
    ok = (rc.returncode == 0) and (mark in t)
    if not ok:
        bad += 1
    print(f'  {"OK " if ok else "ERR"} {f}' + ('' if ok else f'  syntaxe={rc.returncode} marqueur={mark in t}'))

print()
print('VERDICT:', 'OK — asar installe francise' if bad == 0 else f'{bad} probleme(s)')
