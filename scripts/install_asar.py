"""Installe app_fr.asar dans l'app (avec sauvegarde de l'original).

Usage: python3 install_asar.py [--restore]
"""
import os, shutil, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

TARGET = paths.app_asar()
NEW = paths.APP_FR_ASAR
BACKUP_DIR = paths.BACKUP

if '--restore' in sys.argv:
    baks = sorted([p for p in os.listdir(BACKUP_DIR) if p.endswith('__app.asar')])
    if not baks:
        raise SystemExit('aucune sauvegarde app.asar')
    src = os.path.join(BACKUP_DIR, baks[-1])
    shutil.copy2(src, TARGET)
    print('restaure depuis', baks[-1])
    print('taille:', os.path.getsize(TARGET))
    raise SystemExit(0)

if not os.path.isfile(NEW):
    raise SystemExit('app_fr.asar introuvable')

os.makedirs(BACKUP_DIR, exist_ok=True)
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
bak = os.path.join(BACKUP_DIR, f'{stamp}__app.asar')
shutil.copy2(TARGET, bak)
print('sauvegarde  :', bak, f'({os.path.getsize(bak):,} o)')

shutil.copy2(NEW, TARGET)
print('installe    :', TARGET, f'({os.path.getsize(TARGET):,} o)')
