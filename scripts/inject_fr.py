"""Injecte un dictionnaire français dans l'app ReasonIX Studio installee.

Mecanisme (bundle i18n minifie) :
  var e={...EN...}, h={zh:{},en:{...e,...}}   // h = dictionnaires
  function T(e,t){let n=_[e]??e; ...}         // _ = h[g], g = langue courante
  function b(e){ ... t===`zh`||t===`en`?t:x() } // resolve : n'accepte que zh/en
  function x(){ ... }                          // machine()
  function w(e){ ... }                         // adopt()

Patchs appliques (5 remplacements + 1 append), tous asserts uniques :
  R1  T consulte globalThis.__FR quand la langue est `fr`
  R2  b() accepte `fr`
  R3  <html lang> gere `fr`
  R4  w() ne reecrase pas un choix `fr` (sinon le kernel le remet a en/zh)
  R5  x() detecte une machine française
  APP globalThis.__FR = {...}  et  h.fr = globalThis.__FR
Plus, dans Settings-*.js, ajout de l'option [`fr`,`Français`].

Usage : python3 inject_fr.py [--dry-run] [--restore] [dict.json]
"""
import os, re, sys, glob, json, shutil, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

RES = paths.app_assets()
BACKUP_DIR = paths.BACKUP
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DICT = paths.FR_DICT

BT = '`'  # backtick, pour lisibilite des motifs

# (nom, ancien, nouveau, obligatoire)
def patches():
    return [
        ('R1_T',
         'function T(e,t){let n=_[e]??e;',
         f'function T(e,t){{let n=(g==={BT}fr{BT}?globalThis.__FR?.[e]:void 0)??_[e]??e;'),
        ('R2_b',
         f't==={BT}zh{BT}||t==={BT}en{BT}?t:x()',
         f't==={BT}zh{BT}||t==={BT}en{BT}||t==={BT}fr{BT}?t:x()'),
        ('R3_lang',
         f'document.documentElement.lang=g==={BT}zh{BT}?{BT}zh-CN{BT}:{BT}en{BT}',
         f'document.documentElement.lang=g==={BT}zh{BT}?{BT}zh-CN{BT}:g==={BT}fr{BT}?{BT}fr{BT}:{BT}en{BT}'),
        ('R4_w',
         'function w(e){let t=',
         f'function w(e){{if((localStorage.getItem(v)||{BT}{BT}).trim().toLowerCase()==={BT}fr{BT})return !1;let t='),
        ('R5_x',
         f'function x(){{return S(navigator.languages?.[0]??navigator.language??{BT}{BT})?{BT}zh{BT}:{BT}en{BT}}}',
         f'function x(){{let L=navigator.languages?.[0]??navigator.language??{BT}{BT};return S(L)?{BT}zh{BT}:F(L)?{BT}fr{BT}:{BT}en{BT}}}function F(e){{return e.toLowerCase().startsWith({BT}fr{BT})}}'),
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
        c = s.count(old)
        if c != 1:
            print(f'  !! {name}: {c} occurrence(s) de {old[:40]!r} -> ignore')
            continue
        s = s.replace(old, new, 1)
        print(f'  ok {name}')
    if s == orig:
        print('  (aucun changement)')
        return False
    if not dry:
        b = backup(path)
        open(path, 'w', encoding='utf-8').write(s)
        print('  sauvegarde:', b)
    return True

def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    dict_path = DEFAULT_DICT
    for a in args:
        if a.endswith('.json'):
            dict_path = a

    fr = {}
    if os.path.isfile(dict_path):
        fr = json.load(open(dict_path, encoding='utf-8'))
    print(f'Dictionnaire: {dict_path} -> {len(fr)} entrees')
    if not fr:
        print('  (dictionnaire vide : le mecanisme sera patche mais rien ne sera traduit)')

    i18n = find('i18n-*.js')
    print('\n== bundle i18n ==', os.path.basename(i18n))
    reps = patches()
    # APP : dictionnaire + rattachement a h
    app_old = None  # append a la fin du fichier
    changed = apply(i18n, reps, dry)
    if not dry:
        s = open(i18n, encoding='utf-8').read()
        # Marqueur fiable : R1 contient deja "globalThis.__FR" mais jamais ";globalThis.__FR=".
        if ';globalThis.__FR=' not in s:
            js = json.dumps(fr, ensure_ascii=False)
            s = s + f'\n;globalThis.__FR={js};h.fr=globalThis.__FR;\n'
            open(i18n, 'w', encoding='utf-8').write(s)
            print('  ok APP: globalThis.__FR + h.fr ajoutes')
        else:
            # mettre a jour le dictionnaire existant (lambda : le JSON ne doit pas
            # etre interprete comme un motif de remplacement \1, \g<..> ...)
            new_code = ';globalThis.__FR=' + json.dumps(fr, ensure_ascii=False) + ';h.fr=globalThis.__FR;'
            s2 = re.sub(r';globalThis\.__FR=\{.*?\};h\.fr=globalThis\.__FR;',
                        lambda m: new_code, s, count=1, flags=re.S)
            open(i18n, 'w', encoding='utf-8').write(s2)
            print('  ok APP: dictionnaire mis a jour')

    settings = find('Settings-*.js')
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

if __name__ == '__main__':
    main()
