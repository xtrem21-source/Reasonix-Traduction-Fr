"""Get a pristine copy of app.asar — the reference for the native patch.

The native surfaces are patched by producing a modified copy of `app.asar`,
never by editing the installed file in place. That copy must start from an
*unpatched* archive. This script finds one:

  1. the **oldest** dated backup under `work/backup/`, if any — that is the
     original, captured before this tool first changed anything;
  2. otherwise the **currently installed** `app.asar`, if it looks unpatched.

Output: `work/asar_orig/` — an extraction of the original.
"""
import os, glob, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

BACKUP = paths.BACKUP
ORIG_DIR = paths.ASAR_ORIG

# A string that only exists after the French patch has been applied.
FRENCH_MARK = b'Reasonix Studio d\xc3\xa9marre'


def pick_source():
    backups = sorted(glob.glob(os.path.join(BACKUP, '*__app.asar')))
    if backups:
        return backups[0], 'oldest backup under work/backup'
    installed = paths.app_asar()
    if os.path.isfile(installed):
        return installed, 'currently installed app.asar'
    raise SystemExit(
        'No pristine app.asar could be found:\n'
        f'  no backup under {BACKUP}\n'
        f'  no installation at {installed}\n'
        'Is Reasonix Studio installed? Set REASONIX_STUDIO_DIR if it is elsewhere.'
    )


src, origin = pick_source()
print(f'source : {origin}')
print(f'         {src}  ({os.path.getsize(src):,} o)')

raw = open(src, 'rb').read()
already_patched = FRENCH_MARK in raw
print('contains the French patch ?', already_patched)
if already_patched:
    raise SystemExit(
        'The chosen source is already patched, so it cannot be the reference.\n'
        'Either restore the original first:\n'
        '    python3 scripts/install_asar.py --restore\n'
        'or remove the patched archive from work/backup/ and try again.'
    )

if os.path.isdir(ORIG_DIR):
    shutil.rmtree(ORIG_DIR)
os.makedirs(ORIG_DIR)

r = subprocess.run(f'{paths.asar_prefix()} extract "{src}" "{ORIG_DIR}"', shell=True,
                   capture_output=True, text=True)
print('extract exit', r.returncode, r.stderr[-200:])
print('files:', len(os.listdir(os.path.join(ORIG_DIR, 'src'))), 'in src/')
