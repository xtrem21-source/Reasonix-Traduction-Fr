import io, os, re, shutil

V = r'J:\Reasonix Studio\resources\frontend-next\dist\voice-input.js'
s = io.open(V, encoding='utf-8').read()
orig = s

# 1. micro plus petit : 24 px, marge 4 px, icone 14 px
paires = [
    ("margin:0 0 0 8px;flex:0 1 auto;min-width:0", "margin:0 0 0 4px;flex:0 1 auto;min-width:0"),
    ("#ocVoiceAnchor .ocv-btn{width:32px;height:32px}", "#ocVoiceAnchor .ocv-btn{width:24px;height:24px}"),
    ("#ocVoiceAnchor .ocv-btn svg{width:16px;height:16px}", "#ocVoiceAnchor .ocv-btn svg{width:14px;height:14px}"),
]
for a, b in paires:
    if s.count(a) != 1:
        print('ECHEC ancre CSS :', a[:40], s.count(a)); raise SystemExit(1)
    s = s.replace(a, b)
print('1. micro reduit a 24 px (marge 4, icone 14)')

# 2. retirer le masquage : le micro reste visible pendant les tours
deb = s.find('    function tourEnCours() {')
fin = s.find('    }, 300);', deb)
if deb < 0 or fin < 0:
    print('ECHEC : bloc de masquage introuvable'); raise SystemExit(1)
fin = s.find('\n', fin) + 1
s = s[:deb] + s[fin:]
print('2. masquage supprime : le micro ne disparait plus')

shutil.copy2(V, V + '.avant-compact')
io.open(V, 'w', encoding='utf-8').write(s)
print('patch applique :', len(orig), '->', len(s), 'caracteres')
print('masquage encore present :', 'tourEnCours' in s)

for c in [
    r'C:\Users\Xtrem-21\Desktop\Reasonix-FR-2.52-winH\micro-winh\voice-input.js',
    r'C:\Users\Xtrem-21\Desktop\Reasonix-FR-2.52-winH\Reasonix-Voice-Input-publish\src\voice-input.20261026-groq-winh.js',
    r'C:\Users\Xtrem-21\Desktop\Pack-Micro-20261026\module\voice-input.js',
]:
    if os.path.isdir(os.path.dirname(c)):
        shutil.copy2(V, c)
        print('   copie ->', os.path.basename(c))
