"""Applique le patch francais a Reasonix Studio 2.49 (app installee).

Usage :
  python patch249.py --dry-run     # montre ce qui serait fait
  python patch249.py               # applique (sauvegardes horodatees)
  python patch249.py --restore     # remet les sauvegardes les plus recentes

Chemins : lus dans config.bat (REASONIX_APP, REASONIX_TEMP) avec les valeurs
par defaut J:\\Reasonix Studio et G:\\Temp. Aucun temporaire sur C:.

Ce qu'il fait :
  1. lit index.html pour trouver le bundle i18n REELLEMENT charge ;
  2. patch ce bundle (6 remplacements + dictionnaire FR 2.49) ;
  3. patch le bundle Settings qui propose zh/en (ajoute Francais) ;
  4. patch index.html (langue de l'ecran de demarrage) ;
  5. verifie la syntaxe avant d'ecrire, puis les marqueurs.

Idempotent : si __FR est deja present, le bundle est considere patche.
"""
import os, sys, re, json, glob, shutil, datetime, subprocess, tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DICT = os.path.join(ROOT, 'dict', 'fr_dict_249.json')
BACKUPS = os.path.join(ROOT, 'backups')
APP = os.environ.get('REASONIX_APP') or r'J:\Reasonix Studio'
TEMP_ROOT = os.environ.get('REASONIX_TEMP') or r'G:\Temp'
DIST = os.path.join(APP, 'resources', 'frontend-next', 'dist')
ASSETS = os.path.join(DIST, 'assets')
DRY = '--dry-run' in sys.argv
RESTORE = '--restore' in sys.argv
BT = '`'

os.makedirs(TEMP_ROOT, exist_ok=True)
tempfile.tempdir = TEMP_ROOT

log_lines = []
def log(msg):
    print(msg, flush=True)
    log_lines.append(msg)

def stamp():
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

def backup(path, tag):
    os.makedirs(BACKUPS, exist_ok=True)
    dest = os.path.join(BACKUPS, '%s__%s__%s' % (stamp(), tag, os.path.basename(path)))
    shutil.copy2(path, dest)
    return dest

def read(p):
    return open(p, encoding='utf-8').read()

def write_atomic(p, s):
    tmp = p + '.tmp-fr'
    open(tmp, 'w', encoding='utf-8', newline='').write(s)
    os.replace(tmp, p)

def find_node():
    """node.exe du PATH, sinon l'Electron de Studio en mode Node."""
    exe = os.environ.get('REASONIX_NODE')
    if exe and os.path.isfile(exe):
        return exe, {}
    found = shutil.which('node')
    if found:
        return found, {}
    electron = os.path.join(APP, 'Reasonix Studio.exe')
    if os.path.isfile(electron):
        return electron, {'ELECTRON_RUN_AS_NODE': '1'}
    raise SystemExit('node introuvable : installe Node.js, ou garde Reasonix Studio installe (son Electron sert de node).')

def check_syntax_text(text):
    node, extra = find_node()
    tmp = os.path.join(tempfile.gettempdir(), 'check-fr-%d.mjs' % os.getpid())
    open(tmp, 'w', encoding='utf-8', newline='').write(text)
    env = os.environ.copy()
    env.update(extra)
    try:
        r = subprocess.run([node, '--check', tmp], capture_output=True, text=True, env=env)
        return r.returncode == 0, (r.stderr or '').strip()
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass

def live_i18n():
    html = read(os.path.join(DIST, 'index.html'))
    m = re.search(r'/(i18n-[A-Za-z0-9_\-]+\.js)', html)
    if not m:
        raise SystemExit('bundle i18n introuvable dans index.html')
    return os.path.join(ASSETS, m.group(1))

def live_main():
    html = read(os.path.join(DIST, 'index.html'))
    m = re.search(r'/(index-[A-Za-z0-9_\-]+\.js)', html)
    if not m:
        return None
    return os.path.join(ASSETS, m.group(1))

def selector_prefix():
    # prefixe commun au selecteur d'origine ET au selecteur deja patche
    return '[[%s%s,%s],[%s,%s],[%s,%s]' % (
        BT, BT, BT + '跟随系统' + BT,
        BT + 'zh' + BT, BT + '中文' + BT,
        BT + 'en' + BT, BT + '英文' + BT)

def live_settings():
    old = selector_prefix()
    hits = []
    for p in glob.glob(os.path.join(ASSETS, 'Settings-*.js')):
        if old in read(p):
            hits.append(p)
    if not hits:
        raise SystemExit('selecteur de langue introuvable dans les bundles Settings')

    # l'installation garde plusieurs builds dans assets : preferer celui que le bundle
    # principal charge vraiment, sinon le plus recent.
    main = live_main()
    if main and os.path.isfile(main):
        refs = re.findall(r'(Settings-[A-Za-z0-9_\-]+\.js)', read(main))
        for ref in refs:
            p = os.path.join(ASSETS, ref)
            if p in hits:
                log('  Settings : %s (charge par %s)' % (ref, os.path.basename(main)))
                return p
    hits.sort(key=os.path.getmtime, reverse=True)
    log('  Settings : %s (le plus recent)' % os.path.basename(hits[0]))
    return hits[0]

def patches():
    return [
        ('R1_traduire',
         'function k(e,t){let n=x[e]??e;',
         'function k(e,t){let n=(b===%sfr%s?globalThis.__FR?.[e]:void 0)??x[e]??e;' % (BT, BT)),
        ('R2_resolve',
         'return t===%szh%s||t===%sen%s?t:T()' % (BT, BT, BT, BT),
         'return t===%szh%s||t===%sen%s||t===%sfr%s?t:T()' % (BT, BT, BT, BT, BT, BT)),
        ('R3_lang',
         'document.documentElement.lang=b===%szh%s?%szh-CN%s:%sen%s' % (BT, BT, BT, BT, BT, BT),
         'document.documentElement.lang=b===%szh%s?%szh-CN%s:b===%sfr%s?%sfr%s:%sen%s' % (BT, BT, BT, BT, BT, BT, BT, BT, BT, BT)),
        ('R4_dict',
         'x=y[b]',
         'x=y[b]??globalThis.__FR??y.en'),
        ('R6_machine',
         'function T(){return E(navigator.languages?.[0]??navigator.language??%s%s)?%szh%s:%sen%s}' % (BT, BT, BT, BT, BT, BT),
         'function T(){let L=navigator.languages?.[0]??navigator.language??%s%s;return E(L)?%szh%s:(L.toLowerCase().startsWith(%sfr%s)?%sfr%s:%sen%s)}' % (BT, BT, BT, BT, BT, BT, BT, BT, BT, BT)),
    ]

def apply_i18n(path, fr):
    s = read(path)
    if 'globalThis.__FR' in s:
        log('  i18n : deja patche')
        payload = json.dumps(fr, ensure_ascii=False, separators=(',', ':'))
        m = s.rfind('globalThis.__FR=')
        j = s.find(';y.fr=', m)
        if m < 0 or j < 0:
            log('  !! dictionnaire existant illisible : pas de mise a jour')
            return False
        new = s[:m] + 'globalThis.__FR=' + payload + s[j:]
        if new == s:
            log('  dictionnaire deja a jour (%d entrees)' % len(fr))
            return False
        ok, err = check_syntax_text(new)
        log('  syntaxe i18n (avant ecriture) : %s' % ('OK' if ok else 'ECHEC'))
        if not ok:
            log(err)
            raise SystemExit(1)
        if DRY:
            log('  (dry-run) dictionnaire non mis a jour (%d entrees)' % len(fr))
            return False
        b = backup(path, 'i18n')
        write_atomic(path, new)
        log('  dictionnaire mis a jour : %d entrees (sauvegarde %s)' % (len(fr), os.path.basename(b)))
        return True

    for name, old, new in patches():
        c = s.count(old)
        if c != 1:
            raise SystemExit('motif %s : %d occurrence(s) au lieu de 1' % (name, c))
        s = s.replace(old, new, 1)
        log('  ok %s' % name)
    payload = json.dumps(fr, ensure_ascii=False, separators=(',', ':'))
    s = s + '\n;globalThis.__FR=' + payload + ';y.fr=globalThis.__FR;\n'

    ok, err = check_syntax_text(s)
    log('  syntaxe i18n (avant ecriture) : %s' % ('OK' if ok else 'ECHEC'))
    if not ok:
        log(err)
        raise SystemExit(1)
    if DRY:
        log('  (dry-run) i18n non ecrit, %d entrees FR' % len(fr))
        return False
    b = backup(path, 'i18n')
    write_atomic(path, s)
    log('  ecrit %s (sauvegarde %s)' % (os.path.basename(path), os.path.basename(b)))
    return True

def apply_settings(path):
    s = read(path)
    old = selector_prefix() + ']'
    new = '[[%s%s,%s],[%s,%s],[%s,%s],[%s,%s]]' % (
        BT, BT, BT + '跟随系统' + BT,
        BT + 'zh' + BT, BT + '中文' + BT,
        BT + 'en' + BT, BT + '英文' + BT,
        BT + 'fr' + BT, BT + 'Français' + BT)
    if s.count(old) != 1:
        if s.count(new) == 1:
            log('  Settings : deja patche')
            return False
        raise SystemExit('selecteur Settings : motif introuvable')
    if DRY:
        log('  (dry-run) Settings non ecrit')
        return False
    b = backup(path, 'settings')
    write_atomic(path, s.replace(old, new, 1))
    log('  ecrit %s (sauvegarde %s)' % (os.path.basename(path), os.path.basename(b)))
    return True

def apply_index():
    p = os.path.join(DIST, 'index.html')
    s = read(p)
    old = 'document.documentElement.lang = zh ? "zh-CN" : "en";'
    new = 'document.documentElement.lang = p === "fr" ? "fr" : (zh ? "zh-CN" : "en");'
    if old not in s:
        log('  index.html : motif absent (deja patche ou build different)')
        return False
    if DRY:
        log('  (dry-run) index.html non ecrit')
        return False
    b = backup(p, 'index')
    write_atomic(p, s.replace(old, new, 1))
    log('  ecrit index.html (sauvegarde %s)' % os.path.basename(b))
    return True


# Libelles anglais cables en dur : ils ne passent pas par la fonction de
# traduction, donc le dictionnaire ne peut pas les couvrir. On remplace le
# litteral par sa version francaise (aucun appel ajoute : pas de risque de
# portee). (bundle logique, motif attendu, remplacement, occurrences attendues)
LABELS = [
    ('settings', 'children:`API Key`', 'children:`Clé API`', 1),
    ('settings', 'children:`Tokens`', 'children:`Jetons`', 2),
    ('settings', 'children:`Turns`', 'children:`Tours`', 1),
    ('main', 'label:`Ask`', 'label:`Demander`', 1),
    ('main', 'title:`Claude Code mod`', 'title:`Module Claude Code`', 1),
    ('main', 'children:`MCP · Skills`', 'children:`MCP · Compétences`', 1),
]


def apply_labels(bundles):
    """Remplace les libelles anglais codes en dur dans les bundles charges."""
    changed = 0
    for which, old, new, expected in LABELS:
        path = bundles.get(which)
        if not path or not os.path.isfile(path):
            log('  libelle %-24s bundle %s introuvable' % (old, which))
            continue
        s = read(path)
        n_old = s.count(old)
        n_new = s.count(new)
        if n_old == 0:
            if n_new:
                log('  libelle %-24s deja remplace' % old)
            else:
                log('  libelle %-24s motif absent' % old)
            continue
        if n_old != expected:
            raise SystemExit('libelle %s : %d occurrence(s) au lieu de %d' % (old, n_old, expected))
        if DRY:
            log('  (dry-run) libelle %-24s -> %s' % (old, new))
            continue
        b = backup(path, 'labels')
        write_atomic(path, s.replace(old, new))
        changed += 1
        log('  libelle %-24s -> %s (sauvegarde %s)' % (old, new, os.path.basename(b)))
    return changed


def main():
    log('Reasonix Studio : %s' % APP)
    log('Temporaire      : %s' % TEMP_ROOT)
    if not os.path.isdir(DIST):
        raise SystemExit('installation introuvable : %s' % DIST)

    if RESTORE:
        if not os.path.isdir(BACKUPS):
            raise SystemExit('aucune sauvegarde')
        done = set()
        for p in sorted(glob.glob(os.path.join(BACKUPS, '*')), key=os.path.getmtime, reverse=True):
            name = os.path.basename(p)
            target_name = name.split('__', 2)[-1]
            target = os.path.join(ASSETS, target_name)
            if target_name in done or not os.path.exists(target):
                continue
            shutil.copy2(p, target)
            done.add(target_name)
            log('restaure %s <- %s' % (target_name, name))
        return

    if not os.path.exists(DICT):
        raise SystemExit('dictionnaire absent : %s' % DICT)
    fr = json.load(open(DICT, encoding='utf-8'))
    log('dictionnaire FR : %d entrees' % len(fr))

    i18n = live_i18n()
    settings = live_settings()
    log('bundle i18n     : %s' % os.path.basename(i18n))
    log('bundle Settings : %s' % os.path.basename(settings))

    changed = apply_i18n(i18n, fr)
    apply_settings(settings)
    apply_index()
    apply_labels({'main': live_main(), 'settings': settings})

    if changed and not DRY:
        ok, err = check_syntax_text(read(i18n))
        log('syntaxe i18n (fichier installe) : %s' % ('OK' if ok else 'ECHEC'))
        if not ok:
            log(err)
            raise SystemExit(1)
        s = read(i18n)
        log('marqueurs : __FR=%d, v.fr=%d' % (s.count('globalThis.__FR'), s.count('v.fr=')))
    log('')
    if DRY:
        log('DRY-RUN TERMINE. Rien n\'a ete ecrit dans Reasonix Studio.')
    else:
        log('TERMINE. Relance Reasonix Studio, puis choisis Francais dans Parametres > Apparence > Langue.')

if __name__ == '__main__':
    main()

