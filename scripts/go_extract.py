"""Extrait les messages du catalogue Go (messages_en.go) et teste si le binaire
est modifiable (il peut etre verrouille par l'app en cours d'execution)."""
import json, os, re, urllib.request, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(paths.app_bin(), 'reasonix-studio-host.exe')
OUT = os.path.join(paths.WORK, 'go_messages_en.json')
URL = 'https://raw.githubusercontent.com/esengine/deepseek-reasonix/studio/internal/base/i18n/messages_en.go'

print('binaire Go :', os.path.isfile(BIN), f'{os.path.getsize(BIN):,} o' if os.path.isfile(BIN) else '')

# 1. le binaire est-il verrouille par l'app en cours d'execution ?
try:
    with open(BIN, 'r+b'):
        print('binaire modifiable : OUI')
except Exception as e:
    print('binaire modifiable : NON ->', type(e).__name__, e)

# 2. recuperer le catalogue anglais
raw = urllib.request.urlopen(
    urllib.request.Request(URL, headers={'User-Agent': 'probe'}), timeout=30
).read().decode('utf-8', 'replace')
print('messages_en.go :', len(raw), 'octets')

# 3. parser les champs du struct Messages (concatenations gerees)
fields, cur = [], None
for line in raw.splitlines():
    m = re.match(r'^\t([A-Za-z0-9_]+):\s*"', line)
    if m:
        cur = {'field': m.group(1), 'value': ''}
        fields.append(cur)
    if cur is not None:
        for lit in re.findall(r'"((?:[^"\\]|\\.)*)"', line):
            cur['value'] += lit.replace('\\n', '\n').replace('\\t', '\t')
        if not line.rstrip().endswith('+'):
            cur = None

json.dump(fields, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('champs extraits :', len(fields))
print('avec format %   :', sum(1 for f in fields if '%' in f['value']))
for f in fields[:6]:
    print('   ', f['field'], '=', repr(f['value'][:50]))
