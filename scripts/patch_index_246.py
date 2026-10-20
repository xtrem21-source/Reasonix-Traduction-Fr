"""Corrige les libelles d'outils anglais codes en dur dans le bundle web (2.46.0).

Le mapping `al` de index-*.js associe chaque outil a un libelle court. Une
partie est en chinois (traduite par le dictionnaire), une partie est restee en
anglais. Ce script remplace ces dernieres par du francais.

Usage: python3 patch_index_246.py [--dry-run]
"""
import glob, os, shutil, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ASSETS = paths.app_assets()
BACKUP = paths.BACKUP

REPL = [
    ('lsp_definition:`Definition`', 'lsp_definition:`Définition`'),
    ('lsp_references:`References`', 'lsp_references:`Références`'),
    ('lsp_hover:`Hover`', 'lsp_hover:`Survol`'),
    ('parallel_tasks:`Tasks`', 'parallel_tasks:`Tâches`'),
    ('list_subagents:`Subagents`', 'list_subagents:`Sous-agents`'),
    ('run_skill:`Skill`', 'run_skill:`Compétence`'),
    ('read_only_skill:`Skill`', 'read_only_skill:`Compétence`'),
    ('read_skill:`Playbook`', 'read_skill:`Guide`'),
    ('install_skill:`Install`', 'install_skill:`Installer`'),
    ('recall:`Recall`', 'recall:`Rappel`'),
    ('memory:`Memory`', 'memory:`Mémoire`'),
    ('forget:`Forget`', 'forget:`Oublier`'),
    ('history:`History`', 'history:`Historique`'),
    ('docs:`Docs`', 'docs:`Documentation`'),
    ('slash_command:`Command`', 'slash_command:`Commande`'),
    ('install_source:`Install`', 'install_source:`Installer`'),
    ('await_user:`Await`', 'await_user:`Attente`'),
    ('conclude_blocked:`Blocked`', 'conclude_blocked:`Bloqué`'),
    ('conclude_no_changes:`No Changes`', 'conclude_no_changes:`Aucun changement`'),
]

hits = glob.glob(os.path.join(ASSETS, 'index-*.js'))
if len(hits) != 1:
    raise SystemExit(f'index bundle introuvable ou multiple : {hits}')
p = hits[0]
s = open(p, encoding='utf-8').read()
dry = '--dry-run' in sys.argv

changed = []
for old, new in REPL:
    if s.count(new) == 1:
        print(f'  ok (deja applique) {old.split(":")[0]}')
        continue
    c = s.count(old)
    if c != 1:
        print(f'  !! {old!r}: {c} occurrence(s) -> IGNORE')
        continue
    s = s.replace(old, new, 1)
    changed.append(old)

if not changed:
    print('aucun changement')
    raise SystemExit(0)

if dry:
    print(f'{len(changed)} libelle(s) seraient corriges (dry-run)')
    raise SystemExit(0)

os.makedirs(BACKUP, exist_ok=True)
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
dst = os.path.join(BACKUP, f'{stamp}__{os.path.basename(p)}')
shutil.copy2(p, dst)
open(p, 'w', encoding='utf-8').write(s)
print(f'{len(changed)} libelle(s) corrige(s)')
print('sauvegarde :', os.path.basename(dst))
