"""Verifie le bundle REELLEMENT installe (pas une copie) en le chargeant en ESM.

Copie le fichier installe vers un .mjs temporaire (Node exige .mjs pour ESM),
puis delegue a verify_i18n.mjs.
"""
import os, glob, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

RES = paths.app_assets()
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(paths.TESTDIR, 'installed.mjs')

inst = glob.glob(os.path.join(RES, 'i18n-*.js'))[0]
print('fichier installe :', os.path.basename(inst), os.path.getsize(inst), 'octets')
shutil.copy2(inst, TMP)

r = subprocess.run(['node', os.path.join(HERE, 'verify_i18n.mjs'), TMP, 'fr'],
                   capture_output=True, text=True, encoding='utf-8')
print(r.stdout)
if r.stderr.strip():
    print('STDERR:', r.stderr[:800])
sys.exit(r.returncode)
