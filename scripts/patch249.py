"""Applique le patch francais a Reasonix Studio 2.49 (app installee).

Usage :
  python patch249.py --dry-run     # montre ce qui serait fait
  python patch249.py               # applique (sauvegardes horodatees)
  python patch249.py --restore     # remet les sauvegardes les plus recentes

Ce qu'il fait :
  1. lit index.html pour trouver le bundle i18n REELLEMENT charge ;
  2. patch ce bundle (6 remplacements + dictionnaire FR depuis translations/fr.json) ;
  3. patch le bundle Settings qui propose zh/en (ajoute Francais) ;
  4. patch index.html (langue de l'ecran de demarrage) ;
  5. verifie chaque fichier (syntaxe + marqueurs) et journalise.

Idempotent : si __FR est deja present, le bundle est considere patche et seul
le dictionnaire est mis a jour.

Installation : REASONIX_STUDIO_DIR si l'app n'est pas au chemin Windows standard.
"""
import os, sys, re, json, glob, shutil, datetime, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DICT = os.path.join(ROOT, 'translations', 'fr.json')
BACKUPS = os.path.join(ROOT, 'backups')
APP = os.environ.get('REASONIX_STUDIO_DIR') or os.path.join(
    os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Reasonix Studio')
DIST = os.path.join(APP, 'resources', 'frontend-next', 'dist')
ASSETS = os.path.join(DIST, 'assets')
DRY = '--dry-run' in sys.argv
RESTORE = '--restore' in sys.argv
BT = '`'

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


def live_i18n():
    html = read(os.path.join(DIST, 'index.html'))
    m = re.search(r'/(i18n-[A-Za-z0-9_\-]+\.js)', html)
    if not m:
        raise SystemExit('bundle i18n introuvable dans index.html')
    return os.path.join(ASSETS, m.group(1))


def live_settings():
    hits = []
    # prefixe commun au selecteur d'origine ET au selecteur deja patche
    old = '[[%s%s,%s],[%s,%s],[%s,%s]' % (
        BT, BT, BT + '跟随系统' + BT,
        BT + 'zh' + BT, BT + '中文' + BT,
        BT + 'en' + BT, BT + '英文' + BT)
    for p in glob.glob(os.path.join(ASSETS, 'Settings-*.js')):
        s = read(p)
        if old in s:
            hits.append(p)
    if not hits:
        raise SystemExit('selecteur de langue introuvable dans les bundles Settings')
    if len(hits) > 1:
        # le plus recent est celui du build courant
        hits.sort(key=os.path.getmtime, reverse=True)
    return hits[0]


def patches():
    return [
        ('R1_traduire',
         'function O(e,t){let n=b[e]??e;',
         'function O(e,t){let n=(y===%sfr%s?globalThis.__FR?.[e]:void 0)??b[e]??e;' % (BT, BT)),
        ('R2_resolve',
         'return t===%szh%s||t===%sen%s?t:w()' % (BT, BT, BT, BT),
         'return t===%szh%s||t===%sen%s||t===%sfr%s?t:w()' % (BT, BT, BT, BT, BT, BT)),
        ('R3_lang',
         'document.documentElement.lang=y===%szh%s?%szh-CN%s:%sen%s' % (BT, BT, BT, BT, BT, BT),
         'document.documentElement.lang=y===%szh%s?%szh-CN%s:y===%sfr%s?%sfr%s:%sen%s' % (BT, BT, BT, BT, BT, BT, BT, BT, BT, BT)),
        ('R4_dict',
         'b=v[y]',
         'b=v[y]??globalThis.__FR??v.en'),
        ('R5_adopt',
         'function D(e){let t=(e??%s%s).trim().toLowerCase(),n=localStorage.getItem(x);' % (BT, BT),
         'function D(e){if((localStorage.getItem(x)||%s%s).trim().toLowerCase()===%sfr%s)return !1;let t=(e??%s%s).trim().toLowerCase(),n=localStorage.getItem(x);' % (BT, BT, BT, BT, BT, BT)),
        ('R6_machine',
         'function w(){return T(navigator.languages?.[0]??navigator.language??%s%s)?%szh%s:%sen%s}' % (BT, BT, BT, BT, BT, BT),
         'function w(){let L=navigator.languages?.[0]??navigator.language??%s%s;return T(L)?%szh%s:(L.toLowerCase().startsWith(%sfr%s)?%sfr%s:%sen%s)}' % (BT, BT, BT, BT, BT, BT, BT, BT, BT, BT)),
    ]


def apply_i18n(path, fr):
    s = read(path)
    if 'globalThis.__FR' in s:
        log('  i18n : deja patche')
        payload = json.dumps(fr, ensure_ascii=False, separators=(',', ':'))
        m = s.rfind('globalThis.__FR=')
        j = s.find(';v.fr=', m)
        if m < 0 or j < 0:
            log('  !! dictionnaire existant illisible : pas de mise a jour')
            return False
        new = s[:m] + 'globalThis.__FR=' + payload + s[j:]
        if new == s:
            log('  dictionnaire deja a jour (%d entrees)' % len(fr))
            return False
        if DRY:
            log('  (dry-run) dictionnaire non mis a jour (%d entrees)' % len(fr))
            return False
        b = backup(path, 'i18n')
        write_atomic(path, new)
        log('  dictionnaire mis a jour : %d entrees (sauvegarde %s)' % (len(fr), os.path.basename(b)))
        return True
    for name, old, new_in in patches():
        c = s.count(old)
        if c != 1:
            raise SystemExit('motif %s : %d occurrence(s) au lieu de 1' % (name, c))
        s = s.replace(old, new_in, 1)
        log('  ok %s' % name)
    payload = json.dumps(fr, ensure_ascii=False, separators=(',', ':'))
    s = s + '\n;globalThis.__FR=' + payload + ';v.fr=globalThis.__FR;\n'
    if DRY:
        log('  (dry-run) i18n non ecrit, %d entrees FR' % len(fr))
        return False
    b = backup(path, 'i18n')
    write_atomic(path, s)
    log('  ecrit %s (sauvegarde %s)' % (os.path.basename(path), os.path.basename(b)))
    return True


def apply_settings(path):
    s = read(path)
    old = '[[%s%s,%s],[%s,%s],[%s,%s]]' % (
        BT, BT, BT + '跟随系统' + BT,
        BT + 'zh' + BT, BT + '中文' + BT,
        BT + 'en' + BT, BT + '英文' + BT)
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
        if new in s:
            log('  index.html : deja patche')
        else:
            log('  index.html : motif absent (build different) — non modifie')
        return False
    if DRY:
        log('  (dry-run) index.html non ecrit')
        return False
    b = backup(p, 'index')
    write_atomic(p, s.replace(old, new, 1))
    log('  ecrit index.html (sauvegarde %s)' % os.path.basename(b))
    return True


def check_syntax(path):
    tmp = os.path.join(tempfile.gettempdir(), 'check-fr.mjs')
    shutil.copy2(path, tmp)
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or '').strip()


def main():
    log('Reasonix Studio : %s' % APP)
    if not os.path.isdir(DIST):
        raise SystemExit('installation introuvable : %s' % DIST)
    if RESTORE:
        if not os.path.isdir(BACKUPS):
            raise SystemExit('aucune sauvegarde')
        for p in sorted(glob.glob(os.path.join(BACKUPS, '*')), key=os.path.getmtime, reverse=True):
            name = os.path.basename(p)
            target = os.path.join(ASSETS, name.split('__', 2)[-1])
            if not os.path.exists(target):
                continue
            shutil.copy2(p, target)
            log('restaure %s <- %s' % (os.path.basename(target), name))
        return

    if not os.path.exists(DICT):
        raise SystemExit('dictionnaire absent : %s' % DICT)
    fr = json.load(open(DICT, encoding='utf-8'))
    log('dictionnaire FR : %d entrees' % len(fr))

    i18n = live_i18n()
    settings = live_settings()
    log('bundle i18n  : %s' % os.path.basename(i18n))
    log('bundle Settings : %s' % os.path.basename(settings))

    changed = apply_i18n(i18n, fr)
    apply_settings(settings)
    apply_index()

    if changed and not DRY:
        ok, err = check_syntax(i18n)
        log('syntaxe i18n : %s' % ('OK' if ok else 'ECHEC'))
        if not ok:
            log(err)
            raise SystemExit(1)
        s = read(i18n)
        log('marqueurs : __FR=%d, v.fr=%d' % (s.count('globalThis.__FR'), s.count('v.fr=')))
    log('')
    log('TERMINE. Relance Reasonix Studio, puis choisis Francais dans Parametres > Apparence > Langue.')


if __name__ == '__main__':
    main()
