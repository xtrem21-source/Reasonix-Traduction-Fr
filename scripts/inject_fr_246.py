"""Injecte le dictionnaire francais dans l'app Reasonix Studio v2.46.0.

Structure du bundle v2.46.0 (different de la v2.40) :
  _={zh:{},en:{...}}          // dictionnaires
  v=`zh`, y=_.zh, b=`rx-lang` // langue courante, dict actif, cle de stockage
  function x(){...}           // boot : v=S(localStorage.getItem(b)), y=_[v], <html lang>
  function S(e){...}          // resolve : n'accepte que zh/en
  function C(){...}           // machine : w(locale) ? zh : en
  function w(e){...}          // isChinese
  function E(e){...}          // adopt (change de langue + reload)
  function D(e,t){...}        // translate : y[e]
  function O(...)             // forme plurielle

Patchs (asserts uniques) :
  R1  D consulte globalThis.__FR quand la langue est `fr`
  R2  S accepte `fr`
  R3  <html lang> gere `fr`
  R4  E ne reecrit pas un choix `fr` (sinon le kernel le remet a en/zh)
  R5  C detecte une machine francaise
  APP globalThis.__FR = {...}  et  _.fr = globalThis.__FR
Plus, dans Settings-*.js, ajout de l'option [`fr`,`Français`].

Usage : python3 inject_fr_246.py [--dry-run] [--restore] [dict.json]
"""
import os, re, sys, glob, json, shutil, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
from log_246 import log

RES = paths.app_assets()
BACKUP_DIR = paths.BACKUP
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DICT = os.path.join(HERE, 'fr_dict_246.json')

BT = '`'  # backtick, pour lisibilite des motifs


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
        raise SystemExit(f'attendu 1 fichier pour {glob_pat}, trouve {len(hits)}: {hits}')
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
            print(f'  ok {name} (deja applique)')
            continue
        c = s.count(old)
        if c != 1:
            print(f'  !! {name}: {c} occurrence(s) de {old[:50]!r} -> IGNORE')
            continue
        s = s.replace(old, new, 1)
        print(f'  ok {name}')
    if s == orig:
        print('  (aucun changement)')
        return False
    if not dry:
        b = backup(path)
        open(path, 'w', encoding='utf-8').write(s)
        print('  sauvegarde:', os.path.basename(b))
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
        # Restaure les deux bundles depuis la plus recente sauvegarde qui les concerne.
        for p in (i18n, settings):
            name = os.path.basename(p)
            baks = sorted([b for b in os.listdir(BACKUP_DIR) if b.endswith('__' + name)])
            if not baks:
                print('  aucune sauvegarde pour', name)
                continue
            src = os.path.join(BACKUP_DIR, baks[-1])
            shutil.copy2(src, p)
            print(f'  restaure {name} depuis {baks[-1]}')
        return

    fr = {}
    if os.path.isfile(dict_path):
        fr = json.load(open(dict_path, encoding='utf-8'))
    print(f'Dictionnaire: {os.path.basename(dict_path)} -> {len(fr)} entrees')
    if not fr:
        print('  (dictionnaire vide : le mecanisme sera patche mais rien ne sera traduit)')

    print('\n== bundle i18n ==', os.path.basename(i18n))
    reps = patches()
    changed = apply(i18n, reps, dry)
    if not dry:
        s = open(i18n, encoding='utf-8').read()
        # Marqueur fiable : R1 contient deja "globalThis.__FR" mais jamais ";globalThis.__FR=".
        if ';globalThis.__FR=' not in s:
            js = json.dumps(fr, ensure_ascii=False)
            s = s + f'\n;globalThis.__FR={js};_.fr=globalThis.__FR;\n'
            open(i18n, 'w', encoding='utf-8').write(s)
            print('  ok APP: globalThis.__FR + _.fr ajoutes')
        else:
            new_code = ';globalThis.__FR=' + json.dumps(fr, ensure_ascii=False) + ';_.fr=globalThis.__FR;'
            s2 = re.sub(r';globalThis\.__FR=\{.*?\};_\.fr=globalThis\.__FR;',
                        lambda m: new_code, s, count=1, flags=re.S)
            open(i18n, 'w', encoding='utf-8').write(s2)
            print('  ok APP: dictionnaire mis a jour')

    print('\n== bundle Settings ==', os.path.basename(settings))
    # Idempotent : on n'ajoute l'option que si elle n'y est pas deja.
    sel_fr = f'[{BT}fr{BT},{BT}Français{BT}]'
    s = open(settings, encoding='utf-8').read()
    if sel_fr in s:
        print('  option Français deja presente, rien a faire')
    else:
        old_sel = f'[{BT}zh{BT},{BT}中文{BT}],[{BT}en{BT},{BT}英文{BT}]'
        new_sel = f'[{BT}zh{BT},{BT}中文{BT}],[{BT}en{BT},{BT}英文{BT}],{sel_fr}'
        apply(settings, [('R6_selector', old_sel, new_sel)], dry)

    print('\nTermine.' + (' (dry-run : rien ecrit)' if dry else ''))
    log('dictionnaire', f'{len(fr)} entrees' + (' (dry-run)' if dry else ''))


if __name__ == '__main__':
    main()
