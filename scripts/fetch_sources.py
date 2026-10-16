"""Récupère les catalogues i18n du dépôt esengine/deepseek-reasonix.

Usage: python3 fetch_sources.py
Sortie: Desktop/DEV/sources/frontend-i18n/*.ts  +  un manifeste JSON
"""
import json, os, urllib.request, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

RAW = 'https://raw.githubusercontent.com/esengine/deepseek-reasonix/studio/'
OUT = os.path.join(paths.SOURCES, 'frontend-i18n')
os.makedirs(OUT, exist_ok=True)

# Catalogues frontend (clé = texte chinois source, valeur = anglais)
I18N_DIR = 'desktop/frontend-next/src/i18n/'
FILES = [
    'index.ts', 'en.ts', 'en_settings.ts', 'en_community.ts', 'en_composer.ts',
    'en_feedback.ts', 'en_graph.ts', 'en_kernel.ts', 'en_metrics.ts',
    'en_remote.ts', 'en_sponsor.ts', 'en_storage.ts', 'en_surfaces.ts',
    'en_trajectory.ts', 'en_usage.ts', 'en_window.ts', 'en_backup.ts',
    'format.ts', 'kernel.ts', 'notices.ts', 'notice_wording.ts',
    'queue_why.ts', 'compaction_why.ts', 'context_composition.ts',
    'subagent_waiting.ts', 'workspace_lease.ts',
]
# Electron (process principal)
ELECTRON = ['desktop/electron/src/uilang.js']

def fetch(rel, dest_dir):
    url = RAW + rel
    req = urllib.request.Request(url, headers={'User-Agent': 'probe'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    name = os.path.basename(rel)
    with open(os.path.join(dest_dir, name), 'wb') as f:
        f.write(data)
    return name, len(data)

manifest = []
for rel in [I18N_DIR + f for f in FILES]:
    try:
        n, sz = fetch(rel, OUT)
        manifest.append({'path': rel, 'file': n, 'bytes': sz})
        print(f'OK  {n:32} {sz:>8}')
    except Exception as e:
        print(f'ERR {rel}: {e}')

el_dir = os.path.join(os.path.dirname(OUT), 'electron')
os.makedirs(el_dir, exist_ok=True)
for rel in ELECTRON:
    try:
        n, sz = fetch(rel, el_dir)
        manifest.append({'path': rel, 'file': n, 'bytes': sz, 'dir': 'electron'})
        print(f'OK  electron/{n:21} {sz:>8}')
    except Exception as e:
        print(f'ERR {rel}: {e}')

with open(os.path.join(os.path.dirname(OUT), 'manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print('\nTotal fichiers:', len(manifest))
print('Total octets:', sum(m['bytes'] for m in manifest))
