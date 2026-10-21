"""Patche les chaines NATIVES de Reasonix Studio 2.47 (app.asar).

Couvre : page de demarrage, menu contextuel, dialogues d'erreur, dialogue
ancienne version, menu du tray.

Usage :
  python patch_asar247.py --dry-run   # extrait et montre, ne reinstalle pas
  python patch_asar247.py             # applique (sauvegarde de app.asar)
"""
import os, sys, json, shutil, subprocess, tempfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASAR_MOD = r"C:\Users\Xtrem-21\Desktop\Reasonix-FR-Dev\build\tools\node_modules\asar"
APP = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Reasonix Studio')
ASAR = os.path.join(APP, 'resources', 'app.asar')
BACKUPS = os.path.join(ROOT, 'backups')
PATCHES = os.path.join(HERE, 'asar_patches.json')
DRY = '--dry-run' in sys.argv

def log(msg):
    print(msg, flush=True)

def node(js, *args):
    r = subprocess.run(['node', '-e', js] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('node : %s' % (r.stderr or r.stdout))
    return r.stdout

def extract(src, dst):
    node("require(process.argv[1]).extractAll(process.argv[2],process.argv[3])", ASAR_MOD, src, dst)

def pack(src, dst):
    node("const a=require(process.argv[1]);a.createPackage(process.argv[2],process.argv[3]).then(()=>process.exit(0))", ASAR_MOD, src, dst)

def main():
    if not os.path.isfile(ASAR):
        raise SystemExit('app.asar introuvable : %s' % ASAR)
    work = tempfile.mkdtemp(prefix='asar247-')
    src = os.path.join(work, 'orig')
    out = os.path.join(work, 'fr')
    log('extraction...')
    extract(ASAR, src)

    # deja patche ? on ne repack pas, on ne touche a rien
    def contains(rel, needle):
        p = os.path.join(src, 'src', rel)
        if not os.path.isfile(p):
            return False
        return needle in open(p, encoding='utf-8').read()
    if contains('uilang.js', 'isFrench') and contains('editmenu.js', '\u00c9dition'):
        log('app.asar : deja patche, rien a faire')
        return

    shutil.copytree(src, out)

    items = json.load(open(PATCHES, encoding='utf-8'))
    missed = []
    for item in items:
        p = os.path.join(out, 'src', item['file'])
        s = open(p, encoding='utf-8').read()
        for r in item['reps']:
            c = s.count(r['old'])
            if c != 1:
                missed.append((item['file'], r['tag'], c))
                continue
            s = s.replace(r['old'], r['new'], 1)
            log('  ok %-18s %s' % (item['file'], r['tag']))
        open(p, 'w', encoding='utf-8').write(s)

    # starting.js : le bloc TEXT a change en 2.47 ; le patch 'pick' ancien est
    # deja applique et reference TEXT.fr, il faut donc creer cette entree.
    p = os.path.join(out, 'src', 'starting.js')
    s = open(p, encoding='utf-8').read()
    old_en = '  en: ["Reasonix Studio is starting", "Waiting for the local service to be ready. This window will close automatically."],'
    fr_line = '  fr: ["Reasonix Studio d\u00e9marre", "En attente du service local. Cette fen\u00eatre se fermera automatiquement."],'
    if s.count(old_en) == 1 and 'fr: ["Reasonix Studio' not in s:
        s = s.replace(old_en, old_en + '\n' + fr_line, 1)
        open(p, 'w', encoding='utf-8').write(s)
        log('  ok starting.js           entree fr (2.47)')
    else:
        missed.append(('starting.js', 'entree fr', s.count(old_en)))

    if missed:
        log('MOTIFS NON APPLIQUES :')
        for m in missed:
            log('  %-18s %-18s %d' % m)

    # syntaxe
    for f in ['starting.js', 'editmenu.js', 'uilang.js', 'hostexit.js', 'shelllog.js', 'packagegrants.js', 'main.js', 'tray.js']:
        r = subprocess.run(['node', '--check', os.path.join(out, 'src', f)], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit('syntaxe invalide : %s\n%s' % (f, r.stderr))
    log('syntaxe : OK sur les 8 fichiers')

    dest = os.path.join(work, 'app-fr.asar')
    pack(out, dest)
    log('asar reconstruit : %d octets' % os.path.getsize(dest))

    if DRY:
        log('(dry-run) app.asar non remplace ; copie disponible dans %s' % dest)
        return

    os.makedirs(BACKUPS, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bak = os.path.join(BACKUPS, '%s__app.asar' % stamp)
    shutil.copy2(ASAR, bak)
    staged = ASAR + '.fr-new'
    shutil.copy2(dest, staged)
    try:
        os.replace(staged, ASAR)   # remplacement atomique
    except PermissionError:
        try:
            os.remove(staged)
        except OSError:
            pass
        log('')
        log('ECHEC : app.asar est verrouille par Reasonix Studio.')
        log('Ferme completement l\'application (zone de notification : Quitter),')
        log('puis relance ce script ou Francisation_2.47.bat.')
        raise SystemExit(2)
    log('app.asar remplace (sauvegarde : %s)' % os.path.basename(bak))

    # verification sur le fichier installe
    check = os.path.join(work, 'check')
    extract(ASAR, check)
    ok = 0
    for f, needle in [('starting.js', 'd\u00e9marre'), ('editmenu.js', '\u00c9dition'), ('tray.js', 'Rien en cours')]:
        s = open(os.path.join(check, 'src', f), encoding='utf-8').read()
        if needle in s:
            ok += 1
    log('verification installee : %d/3 marqueurs' % ok)
    if ok != 3:
        raise SystemExit('verification echouee')

if __name__ == '__main__':
    main()
