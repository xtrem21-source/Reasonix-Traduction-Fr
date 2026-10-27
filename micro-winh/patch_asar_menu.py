import io, os, shutil, subprocess, sys

ASAR = r'J:\Reasonix Studio\resources\app.asar'
WORK = r'G:\Temp\asar-menu'
NEW = r'G:\Temp\app-menu.asar'
LOG = r'J:\Reasonix\dev\voix-winh\patch-menu.log'

def log(m):
    print(m)
    with io.open(LOG, 'a', encoding='utf-8') as f:
        f.write(m + '\n')

io.open(LOG, 'w', encoding='utf-8').write('')
log('=== francisation du menu contextuel ===')

if os.path.exists(WORK):
    shutil.rmtree(WORK, ignore_errors=True)

log('1. extraction...')
r = subprocess.run('npx -y @electron/asar extract "%s" "%s"' % (ASAR, WORK),
                   shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode != 0:
    log('ECHEC extraction : ' + ((r.stderr or r.stdout) or '')[:400]); sys.exit(2)

F = os.path.join(WORK, 'src', 'editmenu.js')
s = io.open(F, encoding='utf-8').read()

# uniquement la table anglaise : le chinois reste intact
paires = [
    ('    edit: "Edit",', '    edit: "Édition",'),
    ('    undo: "Undo",', '    undo: "Annuler",'),
    ('    redo: "Redo",', '    redo: "Rétablir",'),
    ('    cut: "Cut",', '    cut: "Couper",'),
    ('    copy: "Copy",', '    copy: "Copier",'),
    ('    paste: "Paste",', '    paste: "Coller",'),
    ('    selectAll: "Select All",', '    selectAll: "Tout sélectionner",'),
    ('    pasteAndMatchStyle: "Paste and Match Style",', '    pasteAndMatchStyle: "Coller et adapter le style",'),
    ('    delete: "Delete",', '    delete: "Supprimer",'),
    ('    quote: "Add to conversation",', '    quote: "Ajouter à la conversation",'),
    ('    substitutions: "Substitutions",', '    substitutions: "Substitutions",'),
    ('    showSubstitutions: "Show Substitutions",', '    showSubstitutions: "Afficher les substitutions",'),
    ('    smartQuotes: "Smart Quotes",', '    smartQuotes: "Guillemets intelligents",'),
    ('    smartDashes: "Smart Dashes",', '    smartDashes: "Tirets intelligents",'),
    ('    textReplacement: "Text Replacement",', '    textReplacement: "Remplacement de texte",'),
    ('    speech: "Speech",', '    speech: "Dictée",'),
    ('    startSpeaking: "Start Speaking",', '    startSpeaking: "Démarrer la lecture",'),
    ('    stopSpeaking: "Stop Speaking",', '    stopSpeaking: "Arrêter la lecture",'),
]

manques = []
for a, b in paires:
    if s.count(a) != 1:
        manques.append(a.strip())
    else:
        s = s.replace(a, b)

if manques:
    log('ECHEC : ancres introuvables : ' + ' | '.join(manques)); sys.exit(3)

io.open(F, 'w', encoding='utf-8').write(s)
log('2. 18 libelles francises (table en ; le zh est intact)')

r = subprocess.run('node --check "%s"' % F, shell=True, capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
if r.returncode != 0:
    log('ECHEC syntaxe : ' + ((r.stderr or '') or '')[:300]); sys.exit(4)
log('3. syntaxe editmenu.js : OK')

log('4. repaquetage...')
r = subprocess.run('npx -y @electron/asar pack "%s" "%s"' % (WORK, NEW),
                   shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode != 0 or not os.path.exists(NEW):
    log('ECHEC pack : ' + ((r.stderr or r.stdout) or '')[:400]); sys.exit(5)
log('   app-menu.asar : %d octets' % os.path.getsize(NEW))

bak = ASAR + '.avant-menu'
if not os.path.exists(bak):
    shutil.copy2(ASAR, bak)
    log('5. sauvegarde : ' + bak)
shutil.copy2(NEW, ASAR)
log('6. app.asar remplace (%d octets)' % os.path.getsize(ASAR))
log('=== TERMINE ===')
