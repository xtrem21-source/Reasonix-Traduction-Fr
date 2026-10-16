"""Traduit le catalogue i18n (chinois -> français) via l'API DeepSeek.

- Lit build/extracted/*.json ({key: chinois, value: anglais})
- Envoie des lots a l'API, en donnant le chinois source ET l'anglais de reference
- Preserve strictement les placeholders {nom} et la ponctuation technique
- Ecrit build/fr_parts/<nom>.json (tableau de traductions, meme ordre)

Usage:
  python3 translate_api.py                # tout ce qui reste
  python3 translate_api.py --file en_usage.json
  python3 translate_api.py --limit 120    # borne le nombre de chaines
  python3 translate_api.py --batch 30     # taille de lot
"""
import os, sys, json, glob, time, urllib.request, urllib.error, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACTED = paths.EXTRACTED
PARTS = paths.FR_PARTS
ENV = paths.reasonix_env_file()

os.makedirs(PARTS, exist_ok=True)

# --- cle API ---
def load_key():
    for line in open(ENV, encoding='utf-8', errors='replace'):
        line = line.strip()
        if line.startswith('DEEPSEEK_API_KEY'):
            return line.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('DEEPSEEK_API_KEY introuvable dans .env')

KEY = load_key()
URL = 'https://api.deepseek.com/chat/completions'

SYSTEM = (
    "Tu es un traducteur professionnel specialise dans les interfaces logicielles. "
    "On te donne des fragments d'interface en chinois, avec leur traduction anglaise de reference. "
    "Traduis chaque fragment en FRANÇAIS naturel et concis, tel qu'un logiciel francais l'afficherait. "
    "REGLES STRICTES : "
    "1) Conserve EXACTEMENT les placeholders entre accolades ({n}, {name}, {count}, {alt}...), sans les traduire ni changer leur nom. "
    "2) Conserve la ponctuation technique, les URLs, les noms de touches et de fichiers. "
    "3) Ne traduis PAS les noms propres de produits (Reasonix, WeChat, Alipay, Douyin, QQ, GitHub, VS Code...). "
    "4) Pour une chaine vide, renvoie une chaine vide. "
    "5) Reste concis : c'est du texte d'interface, pas de la prose. "
    "Reponds UNIQUEMENT par un objet JSON {\"t\": [ ... ]} ou le tableau contient exactement une traduction par entree, dans le meme ordre."
)

def call(model, items):
    """items: liste de {zh, en}. Renvoie la liste des traductions FR."""
    lines = []
    for i, it in enumerate(items):
        lines.append(f'{i+1}. zh={it["zh"]}  |  en={it["en"]}')
    user = "Traduis ces fragments :\n" + "\n".join(lines)
    body = json.dumps({
        'model': model,
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': user},
        ],
        'temperature': 0,
        'max_tokens': 8000,
        'response_format': {'type': 'json_object'},
    }).encode('utf-8')
    req = urllib.request.Request(URL, data=body, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {KEY}',
    })
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    content = resp['choices'][0]['message']['content']
    usage = resp.get('usage', {})
    obj = json.loads(content)
    t = obj.get('t') or obj.get('translations')
    if not isinstance(t, list) or len(t) != len(items):
        raise ValueError(f'reponse mal formee ({len(t) if isinstance(t,list) else "?"} vs {len(items)})')
    return t, usage

def main():
    args = sys.argv[1:]
    only = None
    limit = None
    batch = 30
    model = 'deepseek-chat'
    for i, a in enumerate(args):
        if a == '--file':
            only = args[i+1]
        elif a.startswith('--file='):
            only = a.split('=', 1)[1]
        elif a == '--limit':
            limit = int(args[i+1])
        elif a.startswith('--limit='):
            limit = int(a.split('=', 1)[1])
        elif a == '--batch':
            batch = int(args[i+1])
        elif a.startswith('--batch='):
            batch = int(a.split('=', 1)[1])
        elif a == '--model':
            model = args[i+1]
        elif a.startswith('--model='):
            model = a.split('=', 1)[1]

    files = sorted(glob.glob(os.path.join(EXTRACTED, '*.json')))
    if only:
        files = [f for f in files if os.path.basename(f) == only]

    grand = {'in': 0, 'out': 0, 'done': 0, 'fail': 0}
    for f in files:
        name = os.path.basename(f)
        rows = json.load(open(f, encoding='utf-8'))
        out_path = os.path.join(PARTS, name)
        # reprise : tableau deja commence
        done_list = []
        if os.path.isfile(out_path):
            d = json.load(open(out_path, encoding='utf-8'))
            if isinstance(d, list):
                done_list = d
        start = len(done_list)
        if start >= len(rows):
            print(f'{name}: deja complete ({len(rows)})')
            continue
        todo = rows[start:]
        if limit:
            todo = todo[:max(0, limit - grand['done'])]
        print(f'\n### {name}: {len(todo)} a traduire (deja {start})')
        result = list(done_list)
        for i in range(0, len(todo), batch):
            chunk = todo[i:i+batch]
            items = [{'zh': e['key'], 'en': e['value']} for e in chunk]
            for attempt in range(3):
                try:
                    t, usage = call(model, items)
                    break
                except Exception as e:
                    print(f'  lot {i//batch+1} essai {attempt+1} echec: {e}')
                    time.sleep(2 * (attempt + 1))
            else:
                grand['fail'] += len(chunk)
                print(f'  !! lot {i//batch+1} ABANDONNE ({len(chunk)} chaines)')
                break
            result.extend(t)
            grand['in'] += usage.get('prompt_tokens', 0)
            grand['out'] += usage.get('completion_tokens', 0)
            grand['done'] += len(chunk)
            json.dump(result, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(f'  lot {i//batch+1}/{(len(todo)+batch-1)//batch} ok  (+{len(chunk)})  total={len(result)}')
        if limit and grand['done'] >= limit:
            print('\nlimite atteinte')
            break

    print(f"\n=== BILAN === traduites: {grand['done']}, echecs: {grand['fail']}")
    print(f"tokens entree: {grand['in']}, sortie: {grand['out']}")

if __name__ == '__main__':
    main()
