"""Inject the French dictionary into Reasonix Studio 2.46.0.

Bundle structure in 2.46.0 (changed from 2.40.0):

  _={zh:{},en:{...}}          # dictionaries
  v=`zh`, y=_.zh, b=`rx-lang` # current language, active dict, storage key
  function x(){...}           # boot: v=S(localStorage.getItem(b)), y=_[v], <html lang>
  function S(e){...}          # resolve: only accepts zh/en
  function C(){...}           # machine: w(locale) ? zh : en
  function w(e){...}          # isChinese
  function E(e){...}          # adopt (switch language + reload)
  function D(e,t){...}        # translate: y[e]
  function O(...)             # plural form

Patches (each anchor asserted once):

  R1  D consults globalThis.__FR when the language is `fr`
  R2  S accepts `fr`
  R3  <html lang> handles `fr`
  R4  E does not overwrite an explicit `fr` choice (the kernel would reset it)
  R5  C detects a French machine
  APP globalThis.__FR = {...}  and  _.fr = globalThis.__FR

Plus, in Settings-*.js, add the [`fr`,`Français`] option.

Usage: python3 scripts/inject_fr_246.py [--dry-run] [--restore] [dict.json]
"""
import os, re, sys, glob, json, shutil, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

RES = paths.app_assets()
BACKUP_DIR = paths.BACKUP
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DICT = paths.FR_DICT

BT = '`'  # backtick, for readable anchors


def patches():
    return [
        ('R1_translate',
         'function D(e,t){let n=y[e]??e;',
         f'function D(e,t){{let n=(v==={BT}fr{BT}?globalThis.__FR?.[e]:void 0)??y[e]??e;'),
        ('R2_resolve',
         f'return t==={BT}zh{BT}||t==={BT}en{BT}?t:C()}}',
         f'return t==={BT}zh{BT}||t==={BT}en{BT}||t==={BT}fr{BT}?t:C()}}'),
        ('R3_lang',
         f'document.documentElement.lang=v==={BT}zh{BT}?{BT}zh-CN{BT}:{BT}en{BT}',
         f'document.documentElement.lang=v==={BT}zh{BT}?{BT}zh-CN{BT}:v==={BT}fr{BT}?{BT}fr{BT}:{BT}en{BT}'),
        ('R4_adopt',
         f'function E(e){{let t=(e??{BT}{BT}).trim().toLowerCase(),n=localStorage.getItem(b);',
         f'function E(e){{if((localStorage.getItem(b)||{BT}{BT}).trim().toLowerCase()==={BT}fr{BT})return !1;let t=(e??{BT}{BT}).trim().toLowerCase(),n=localStorage.getItem(b);'),
        ('R5_machine',
         f'function C(){{return w(navigator.languages?.[0]??navigator.language??{BT}{BT})?{BT}zh{BT}:{BT}en{BT}}}',
         f'function C(){{let L=navigator.languages?.[0]??navigator.language??{BT}{BT};return w(L)?{BT}zh{BT}:F(L)?{BT}fr{BT}:{BT}en{BT}}}function F(e){{return e.toLowerCase().startsWith({BT}fr{BT})}}'),
    ]


def find(glob_pat):
    hits = [p for p in glob.glob(os.path.join(RES, glob_pat))]
    if len(hits) != 1:
        raise SystemExit(f'expected 1 file for {glob_pat}, found {len(hits)}: {hits}')
    return hits[0]


def backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    dest = os.path.join(BACKUP_DIR, f'{stamp}__{os.path.basename(path)}')
    shutil.copy2(path, dest)
    return dest


def apply(path, reps, dry):
    s = open(path, encoding='utf-8').read()
    orig = s
    for name, old, new in reps:
        if s.count(new) == 1:
            print(f'  ok {name} (already applied)')
            continue
        c = s.count(old)
        if c != 1:
            print(f'  !! {name}: {c} occurrence(s) of {old[:50]!r} -> SKIPPED')
            continue
        s = s.replace(old, new, 1)
        print(f'  ok {name}')
    if s == orig:
        print('  (no change)')
        return False
    if not dry:
        b = backup(path)
        open(path, 'w', encoding='utf-8').write(s)
        print('  backup:', os.path.basename(b))
    return True


def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    restore = '--restore' in args
    dict_path = DEFAULT_DICT
    for a in args:
        if a.endswith('.json'):
            dict_path = a

    i18n = find('i18n-*.js')
    settings = find('Settings-*.js')

    if restore:
        for p in (i18n, settings):
            name = os.path.basename(p)
            baks = sorted([b for b in os.listdir(BACKUP_DIR) if b.endswith('__' + name)])
            if not baks:
                print('  no backup for', name)
                continue
            src = os.path.join(BACKUP_DIR, baks[-1])
            shutil.copy2(src, p)
            print(f'  restored {name} from {baks[-1]}')
        return

    fr = {}
    if os.path.isfile(dict_path):
        fr = json.load(open(dict_path, encoding='utf-8'))
    print(f'dictionary: {os.path.basename(dict_path)} -> {len(fr)} entries')
    if not fr:
        print('  (empty dictionary: the mechanism is patched, nothing is translated)')

    print('\n== i18n bundle ==', os.path.basename(i18n))
    reps = patches()
    changed = apply(i18n, reps, dry)
    if not dry:
        s = open(i18n, encoding='utf-8').read()
        # Reliable marker: R1 already contains "globalThis.__FR", but never ";globalThis.__FR=".
        if ';globalThis.__FR=' not in s:
            js = json.dumps(fr, ensure_ascii=False)
            s = s + f'\n;globalThis.__FR={js};_.fr=globalThis.__FR;\n'
            open(i18n, 'w', encoding='utf-8').write(s)
            print('  ok APP: globalThis.__FR + _.fr added')
        else:
            new_code = ';globalThis.__FR=' + json.dumps(fr, ensure_ascii=False) + ';_.fr=globalThis.__FR;'
            s2 = re.sub(r';globalThis\.__FR=\{.*?\};_\.fr=globalThis\.__FR;',
                        lambda m: new_code, s, count=1, flags=re.S)
            open(i18n, 'w', encoding='utf-8').write(s2)
            print('  ok APP: dictionary updated')

    print('\n== Settings bundle ==', os.path.basename(settings))
    sel_fr = f'[{BT}fr{BT},{BT}Français{BT}]'
    s = open(settings, encoding='utf-8').read()
    if sel_fr in s:
        print('  French option already present, nothing to do')
    else:
        old_sel = f'[{BT}zh{BT},{BT}中文{BT}],[{BT}en{BT},{BT}英文{BT}]'
        new_sel = f'[{BT}zh{BT},{BT}中文{BT}],[{BT}en{BT},{BT}英文{BT}],{sel_fr}'
        apply(settings, [('R6_selector', old_sel, new_sel)], dry)

    print('\nDone.' + (' (dry-run: nothing written)' if dry else ''))


if __name__ == '__main__':
    main()
