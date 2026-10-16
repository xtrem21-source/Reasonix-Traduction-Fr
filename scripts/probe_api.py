"""Verifie si une cle API est disponible pour traduire en masse.

- Lit AppData/Roaming/reasonix/.env
- Affiche SEULEMENT les NOMS des variables (jamais les valeurs)
- Si DEEPSEEK_API_KEY existe, fait un appel de test minimal
"""
import os, json, urllib.request, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ENV = paths.reasonix_env_file()
print('fichier .env:', os.path.isfile(ENV))

names = []
values = {}
if os.path.isfile(ENV):
    for line in open(ENV, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        names.append(k)
        values[k] = v

print('variables presentes:', names)

key = values.get('DEEPSEEK_API_KEY')
if not key:
    print('\nPas de DEEPSEEK_API_KEY -> traduction par API impossible avec cette cle.')
    raise SystemExit(0)

print(f'\nDEEPSEEK_API_KEY presente (longueur {len(key)}), test d\'un appel...')

body = json.dumps({
    'model': 'deepseek-chat',
    'messages': [
        {'role': 'system', 'content': 'You are a translator. Reply with the translation only.'},
        {'role': 'user', 'content': 'Translate to French: "Bar chart"'},
    ],
    'max_tokens': 20,
    'temperature': 0,
}).encode('utf-8')

req = urllib.request.Request(
    'https://api.deepseek.com/chat/completions',
    data=body,
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'},
)
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        resp = json.load(r)
    out = resp['choices'][0]['message']['content']
    print('REPONSE:', out.strip())
    print('usage:', resp.get('usage'))
    print('\nVERDICT: cle operationnelle, traduction par API possible')
except Exception as e:
    print('ERREUR:', type(e).__name__, e)
    try:
        print('corps:', e.read().decode('utf-8', 'replace')[:400])
    except Exception:
        pass
