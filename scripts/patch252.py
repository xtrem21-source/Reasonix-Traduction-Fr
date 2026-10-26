"""Apply the language patch to an installed Reasonix Studio 2.52.

Usage:
  python scripts/patch252.py --dry-run
  python scripts/patch252.py
  python scripts/patch252.py --restore
  python scripts/patch252.py --default-lang fr|en|auto

What it does:
  1. reads index.html to find the i18n bundle that is really loaded;
  2. patches that bundle (5 anchors specific to the 2.52 build + the FR dictionary);
  3. adds the target language to the language selector of the Settings bundle;
  4. patches index.html (boot screen language);
  5. replaces English labels that are hard-coded in the loaded bundles;
  6. checks the syntax BEFORE writing, then checks the markers.

Why the anchors differ from 2.49: build 2.52 rewrote its language logic
(b = { zh: {}, en: {...} }, S = b[x], A(e,t) = S[e] ?? e). The six 2.49 anchors
no longer exist.

--default-lang (or REASONIX_UI_DEFAULT) decides what the interface falls back to
when no language is saved. It is NOT hard-coded to French: the pipeline stays
generic, and the French preset simply sets fr. Values:
  fr    the interface opens in French unless a language is explicitly saved
  en    the interface opens in English unless a language is explicitly saved
  auto  follow the machine locale (2.52's original behaviour, French still
        recognised when the system is French)

Idempotent: a bundle that already carries globalThis.__FR only gets its
dictionary refreshed, plus any later default-language change.
"""
import os, sys, re, json, glob, shutil, datetime, subprocess, tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import paths

HERE = os.path.dirname(os.path.abspath(__file__))
APP = paths.require_app()
DIST = os.path.join(APP, 'resources', 'frontend-next', 'dist')
ASSETS = os.path.join(DIST, 'assets')
DICT = paths.FR_DICT
BACKUPS = paths.BACKUP
TEMP_ROOT = os.environ.get('REASONIX_TEMP') or r'G:\Temp'

DRY = '--dry-run' in sys.argv
RESTORE = '--restore' in sys.argv
BT = '`'

def option(name, default):
    for i, a in enumerate(sys.argv):
        if a == '--' + name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if a.startswith('--' + name + '='):
            return a.split('=', 1)[1]
    return default

DEFAULT_LANG = (option('default-lang', os.environ.get('REASONIX_UI_DEFAULT') or 'fr')).strip().lower()
if DEFAULT_LANG not in ('fr', 'en', 'auto'):
    raise SystemExit('--default-lang : fr, en ou auto attendu (recu : %r)' % DEFAULT_LANG)

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
    exe = os.environ.get('REASONIX_NODE')
    if exe and os.path.isfile(exe):
        return exe, {}
    found = shutil.which('node')
    if found:
        return found, {}
    electron = os.path.join(APP, 'Reasonix Studio.exe')
    if os.path.isfile(electron):
        return electron, {'ELECTRON_RUN_AS_NODE': '1'}
    raise SystemExit('node not found: install Node.js, or keep Reasonix Studio installed '
                     '(its Electron binary runs as node).')

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
        raise SystemExit('i18n bundle not found in index.html')
    return os.path.join(ASSETS, m.group(1))

def live_main():
    html = read(os.path.join(DIST, 'index.html'))
    m = re.search(r'/(index-[A-Za-z0-9_\-]+\.js)', html)
    return os.path.join(ASSETS, m.group(1)) if m else None

def selector_old():
    return '[[%s%s,%s],[%s,%s],[%s,%s]]' % (
        BT, BT, BT + '跟随系统' + BT,
        BT + 'zh' + BT, BT + '中文' + BT,
        BT + 'en' + BT, BT + '英文' + BT)

def selector_new():
    return '[[%s%s,%s],[%s,%s],[%s,%s],[%s,%s]]' % (
        BT, BT, BT + '跟随系统' + BT,
        BT + 'zh' + BT, BT + '中文' + BT,
        BT + 'en' + BT, BT + '英文' + BT,
        BT + 'fr' + BT, BT + 'Français' + BT)

def live_settings():
    want, done = selector_old(), selector_new()
    hits = []
    for p in glob.glob(os.path.join(ASSETS, 'Settings-*.js')):
        s = read(p)
        if want in s or done in s:
            hits.append(p)
    if not hits:
        raise SystemExit('language selector not found in the Settings bundles')
    main = live_main()
    if main and os.path.isfile(main):
        for ref in re.findall(r'(Settings-[A-Za-z0-9_\-]+\.js)', read(main)):
            p = os.path.join(ASSETS, ref)
            if p in hits:
                log('  Settings : %s (loaded by %s)' % (ref, os.path.basename(main)))
                return p
    hits.sort(key=os.path.getmtime, reverse=True)
    log('  Settings : %s (most recent)' % os.path.basename(hits[0]))
    return hits[0]

# --- Fallback language -------------------------------------------------------
# The page calls E() when nothing is saved. Build 2.52 wrote:
#   function E(){return D(navigator.languages?.[0]??navigator.language??``)?`zh`:`en`}
# After the patch it returns the chosen default instead of `en`.
def _machine_call():
    return 'navigator.languages?.[0]??navigator.language??%s%s' % (BT, BT)

PRISTINE_E = 'function E(){return D(%s)?%szh%s:%sen%s}' % ('navigator.languages?.[0]??navigator.language??' + BT + BT, BT, BT, BT, BT)

def default_e(lang):
    if lang == 'fr':
        return 'function E(){let L=%s;return D(L)?%szh%s:%sfr%s}' % (_machine_call(), BT, BT, BT, BT)
    if lang == 'en':
        return 'function E(){let L=%s;return D(L)?%szh%s:%sen%s}' % (_machine_call(), BT, BT, BT, BT)
    return ('function E(){let L=%s;return D(L)?%szh%s:L.toLowerCase().startsWith(%sfr%s)?%sfr%s:%sen%s}'
            % (_machine_call(), BT, BT, BT, BT, BT, BT, BT, BT))

# Every form a previously patched bundle may carry, so the default can change.
def known_e_forms():
    return [default_e('auto'), default_e('fr'), default_e('en')]

def patches():
    return [
        ('R1_translate',
         'function A(e,t){let n=S[e]??e;',
         'function A(e,t){let n=(x===%sfr%s?globalThis.__FR?.[e]:void 0)??S[e]??e;' % (BT, BT)),
        ('R2_resolve',
         'return t===%szh%s||t===%sen%s?t:E()' % (BT, BT, BT, BT),
         'return t===%szh%s||t===%sen%s||t===%sfr%s?t:E()' % (BT, BT, BT, BT, BT, BT)),
        ('R3_lang',
         'document.documentElement.lang=x===%szh%s?%szh-CN%s:%sen%s' % (BT, BT, BT, BT, BT, BT),
         'document.documentElement.lang=x===%szh%s?%szh-CN%s:x===%sfr%s?%sfr%s:%sen%s'
         % (BT, BT, BT, BT, BT, BT, BT, BT, BT, BT)),
        ('R4_dict',
         'S=b[x],document.documentElement.lang',
         'S=b[x]??globalThis.__FR??b.en,document.documentElement.lang'),
        ('R5_machine', PRISTINE_E, default_e(DEFAULT_LANG)),
    ]

def apply_i18n(path, fr):
    s = read(path)
    payload = json.dumps(fr, ensure_ascii=False, separators=(',', ':'))

    if 'globalThis.__FR' in s:
        log('  i18n : already patched')
        m = s.rfind('globalThis.__FR=')
        # The dictionary is compact JSON (no newline), so the first ";\n" after
        # it closes the statement. Searching a bare ';' used to stop inside a
        # translation that contained one.
        j = s.find(';\n', m)
        if m < 0 or j < 0:
            log('  !! existing dictionary unreadable: not updating')
            return False
        new = s[:m] + 'globalThis.__FR=' + payload + s[j:]
        target = default_e(DEFAULT_LANG)
        for form in known_e_forms():
            if form == target:
                continue
            if new.count(form) == 1:
                new = new.replace(form, target, 1)
                log('  default language -> %s' % DEFAULT_LANG)
                break
        if new == s:
            log('  dictionary already up to date (%d entries)' % len(fr))
            return False
        ok, err = check_syntax_text(new)
        log('  i18n syntax (before writing) : %s' % ('OK' if ok else 'FAILED'))
        if not ok:
            log(err[:400])
            raise SystemExit(1)
        if DRY:
            log('  (dry-run) dictionary not written (%d entries)' % len(fr))
            return False
        b = backup(path, 'i18n')
        write_atomic(path, new)
        log('  dictionary updated: %d entries (backup %s)' % (len(fr), os.path.basename(b)))
        return True

    for name, old, new in patches():
        c = s.count(old)
        if c != 1:
            raise SystemExit('anchor %s: %d occurrence(s) instead of 1' % (name, c))
        s = s.replace(old, new, 1)
        log('  ok %s' % name)
    s = s + '\n;globalThis.__FR=' + payload + ';\n'

    ok, err = check_syntax_text(s)
    log('  i18n syntax (before writing) : %s' % ('OK' if ok else 'FAILED'))
    if not ok:
        log(err[:400])
        raise SystemExit(1)
    if DRY:
        log('  (dry-run) i18n not written, %d FR entries' % len(fr))
        return False
    b = backup(path, 'i18n')
    write_atomic(path, s)
    log('  wrote %s (backup %s)' % (os.path.basename(path), os.path.basename(b)))
    return True

def apply_settings(path):
    s = read(path)
    old, new = selector_old(), selector_new()
    if s.count(old) == 1:
        if DRY:
            log('  (dry-run) Settings not written')
            return False
        b = backup(path, 'settings')
        write_atomic(path, s.replace(old, new, 1))
        log('  wrote %s (backup %s)' % (os.path.basename(path), os.path.basename(b)))
        return True
    if s.count(new) == 1:
        log('  Settings : already patched')
        return False
    raise SystemExit('Settings selector: anchor not found (%d original, %d patched)'
                     % (s.count(old), s.count(new)))

def apply_index():
    p = os.path.join(DIST, 'index.html')
    s = read(p)
    old_zh = 'var zh = p === "zh" || (p !== "en" && /^(zh|yue|cmn)/i.test(navigator.language || ""));'
    new_fr = ('var fr = p === "fr" || (p !== "zh" && p !== "en" && /^fr/i.test(navigator.language || ""));\n'
              '          var zh = !fr && (p === "zh" || (p !== "en" && /^(zh|yue|cmn)/i.test(navigator.language || "")));')
    old_lang = 'document.documentElement.lang = zh ? "zh-CN" : "en";'
    new_lang = 'document.documentElement.lang = p === "fr" ? "fr" : zh ? "zh-CN" : "en";'

    if new_lang in s:
        log('  index.html : already patched')
        return False
    if s.count(old_zh) != 1 or s.count(old_lang) != 1:
        raise SystemExit('index.html: anchors not found (%d / %d)' % (s.count(old_zh), s.count(old_lang)))
    if DRY:
        log('  (dry-run) index.html not written')
        return False
    s = s.replace(old_zh, new_fr, 1).replace(old_lang, new_lang, 1)
    b = backup(p, 'index')
    write_atomic(p, s)
    log('  wrote index.html (backup %s)' % os.path.basename(b))
    return True

# English labels wired straight into the bundles: the dictionary cannot reach
# them, because they never go through the translation function.
LABELS = [
    ('settings', 'children:%sAPI Key%s' % (BT, BT), 'children:%sClé API%s' % (BT, BT), 1),
    ('settings', 'children:%sTokens%s' % (BT, BT), 'children:%sJetons%s' % (BT, BT), 2),
    ('settings', 'children:%sTurns%s' % (BT, BT), 'children:%sTours%s' % (BT, BT), 1),
    ('main', 'children:%sMODEL CONNECTION%s' % (BT, BT), 'children:%sCONNEXION AU MODÈLE%s' % (BT, BT), 1),
    ('main', 'children:%scoding agent%s' % (BT, BT), 'children:%sagent de code%s' % (BT, BT), 1),
]

def apply_labels(bundles):
    changed = 0
    for which, old, new, expected in LABELS:
        path = bundles.get(which)
        if not path or not os.path.isfile(path):
            log('  label %-26s bundle %s missing' % (old, which))
            continue
        s = read(path)
        n_old, n_new = s.count(old), s.count(new)
        if n_old == 0:
            log('  label %-26s %s' % (old, 'already replaced' if n_new else 'anchor absent'))
            continue
        if n_old != expected:
            raise SystemExit('label %s: %d occurrence(s) instead of %d' % (old, n_old, expected))
        if DRY:
            log('  (dry-run) label %-26s -> %s' % (old, new))
            continue
        b = backup(path, 'labels')
        write_atomic(path, s.replace(old, new))
        changed += 1
        log('  label %-26s -> %s (backup %s)' % (old, new, os.path.basename(b)))
    return changed

def main():
    log('Reasonix Studio : %s' % APP)
    log('Default language: %s' % DEFAULT_LANG)
    if not os.path.isdir(DIST):
        raise SystemExit('installation not found: %s' % DIST)

    if RESTORE:
        if not os.path.isdir(BACKUPS):
            raise SystemExit('no backups')
        done = set()
        for p in sorted(glob.glob(os.path.join(BACKUPS, '*')), key=os.path.getmtime, reverse=True):
            name = os.path.basename(p)
            target_name = name.split('__', 2)[-1]
            target = os.path.join(ASSETS, target_name)
            if target_name in done or not os.path.exists(target):
                continue
            shutil.copy2(p, target)
            done.add(target_name)
            log('restored %s <- %s' % (target_name, name))
        return

    if not os.path.exists(DICT):
        raise SystemExit('dictionary missing: %s' % DICT)
    fr = json.load(open(DICT, encoding='utf-8'))
    log('FR dictionary   : %d entries' % len(fr))

    i18n = live_i18n()
    settings = live_settings()
    log('i18n bundle     : %s' % os.path.basename(i18n))
    log('Settings bundle : %s' % os.path.basename(settings))

    changed = apply_i18n(i18n, fr)
    apply_settings(settings)
    apply_index()
    apply_labels({'main': live_main(), 'settings': settings})

    if changed and not DRY:
        ok, err = check_syntax_text(read(i18n))
        log('i18n syntax (installed file) : %s' % ('OK' if ok else 'FAILED'))
        if not ok:
            log(err[:400])
            raise SystemExit(1)
        log('markers: __FR=%d' % read(i18n).count('globalThis.__FR'))
    log('')
    if DRY:
        log("DRY-RUN DONE. Nothing was written to Reasonix Studio.")
    else:
        log('DONE. Restart Reasonix Studio.')

if __name__ == '__main__':
    main()
