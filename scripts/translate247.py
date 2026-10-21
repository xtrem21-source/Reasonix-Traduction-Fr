"""Traduit les chaines 2.47 absentes du dictionnaire 2.46 (chinois -> francais).

Source   : dict/en_dict_247.json   {chinois: anglais}
Reference: dict/fr_dict_246.json   {chinois: francais}  (3 850 communes)
Sortie   : dict/parts/batch_NNNN.json  et dict/fr_dict_247.json

Reprise : un lot deja ecrit n'est pas refait.
"""
import os, sys, json, time, urllib.request, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DICT = os.path.join(ROOT, 'dict')
PARTS = os.path.join(DICT, 'parts')
os.makedirs(PARTS, exist_ok=True)

EN = json.load(open(os.path.join(DICT, 'en_dict_247.json'), encoding='utf-8'))
FR_OLD = json.load(open(os.path.join(DICT, 'fr_dict_246.json'), encoding='utf-8'))
BATCH = 30

def key():
    env = os.path.join(os.environ['APPDATA'], 'reasonix', '.env')
    for line in open(env, encoding='utf-8', errors='replace'):
        line = line.strip()
        if line.startswith('DEEPSEEK_API_KEY'):
            return line.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('DEEPSEEK_API_KEY introuvable')

KEY = key()
URL = 'https://api.deepseek.com/chat/completions'

SYSTEM = (
    "Tu es un traducteur professionnel specialise dans les interfaces logicielles. "
    "On te donne des fragments d'interface en chinois, avec leur traduction anglaise de reference. "
    "Traduis chaque fragment en FRANCAIS naturel et concis, tel qu'un logiciel francais l'afficherait. "
    "REGLES STRICTES : "
    "1) Conserve EXACTEMENT les placeholders entre accolades ({n}, {name}, {count}, {alt}, {v}, {tool}...), sans les traduire ni changer leur nom. "
    "2) Conserve la ponctuation technique, les URLs, les noms de touches et de fichiers. "
    "3) Ne traduis PAS les noms propres de produits (Reasonix, WeChat, Alipay, Douyin, QQ, GitHub, VS Code, DeepSeek, OpenAI, Claude...). "
    "4) Pour une chaine vide, renvoie une chaine vide. "
    "5) Reste concis : c'est du texte d'interface, pas de la prose. "
    "6) Les fragments sont numerotes ; reponds UNIQUEMENT par un objet JSON {\"t\": [ ... ]} contenant exactement une traduction par entree, dans le meme ordre."
)

def call(items):
    lines = []
    for i, (zh, en) in enumerate(items):
        lines.append('%d. zh=%s  |  en=%s' % (i + 1, zh, en))
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': 'Traduis ces fragments :\n' + '\n'.join(lines)},
        ],
        'temperature': 0,
        'max_tokens': 8000,
        'response_format': {'type': 'json_object'},
    }).encode('utf-8')
    req = urllib.request.Request(URL, data=body, headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + KEY,
    })
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.load(r)
    obj = json.loads(resp['choices'][0]['message']['content'])
    t = obj.get('t') or obj.get('translations')
    if not isinstance(t, list) or len(t) != len(items):
        raise ValueError('reponse mal formee : %s vs %s' % (len(t) if isinstance(t, list) else '?', len(items)))
    return t, resp.get('usage', {})

missing = [k for k in EN if k not in FR_OLD]
missing.sort()
print('a traduire :', len(missing), flush=True)

done = 0
for start in range(0, len(missing), BATCH):
    n = start // BATCH
    out = os.path.join(PARTS, 'batch_%04d.json' % n)
    if os.path.exists(out):
        done += len(json.load(open(out, encoding='utf-8')))
        continue
    chunk = missing[start:start + BATCH]
    items = [(k, EN[k]) for k in chunk]
    for attempt in range(3):
        try:
            tr, usage = call(items)
            break
        except Exception as e:
            print('  lot', n, 'tentative', attempt + 1, 'echec:', e, flush=True)
            time.sleep(3)
    else:
        print('  lot', n, 'ABANDONNE', flush=True)
        continue
    json.dump({k: v for k, v in zip(chunk, tr)}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    done += len(chunk)
    print('  lot %d : %d/%d  (in=%s out=%s)' % (n, done, len(missing), usage.get('prompt_tokens'), usage.get('completion_tokens')), flush=True)

# fusion
merged = dict(FR_OLD)
for p in sorted(glob.glob(os.path.join(PARTS, 'batch_*.json'))):
    merged.update(json.load(open(p, encoding='utf-8')))
json.dump(merged, open(os.path.join(DICT, 'fr_dict_247.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('dictionnaire final :', len(merged), 'entrees', flush=True)
