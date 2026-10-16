"""Verifie la syntaxe des JS natifs patches, puis reconstruit app.asar.

Sortie : build/app_fr.asar  (asm non installe, verifie d'abord)
Usage: python3 repack_asar.py
"""
import os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

DST = paths.ASAR_FR
OUT = paths.APP_FR_ASAR
SRC = os.path.join(DST, 'src')

MODIFIED = ['uilang.js', 'starting.js', 'editmenu.js', 'hostexit.js',
            'shelllog.js', 'packagegrants.js', 'main.js', 'tray.js']

print('=== node --check sur les fichiers patches ===')
bad = 0
for f in MODIFIED:
    p = os.path.join(SRC, f)
    r = subprocess.run(f'node --check "{p}"', shell=True, capture_output=True, text=True)
    ok = r.returncode == 0
    if not ok:
        bad += 1
    print(f'  {"OK " if ok else "ERR"} {f}' + ('' if ok else f'  {r.stderr.strip()[:120]}'))
print('syntaxe:', 'toutes valides' if bad == 0 else f'{bad} en erreur')

print()
print('=== reconstruction asar ===')
if os.path.isfile(OUT):
    os.remove(OUT)
r = subprocess.run(f'{paths.asar_prefix()} pack "{DST}" "{OUT}"', shell=True, capture_output=True, text=True)
print('exit', r.returncode)
print(r.stdout[-400:])
print(r.stderr[-400:])
if os.path.isfile(OUT):
    print(f'app_fr.asar : {os.path.getsize(OUT):,} octets')
