"""Force la langue automatique a 'fr'.

Apres le patch, la detection automatique ressemble a :
    function T(){let L=navigator.languages?.[0]??navigator.language??``;
                 return E(L)?`zh`:(L.toLowerCase().startsWith(`fr`)?`fr`:`en`)}

On remplace la branche francaise/anglaise par un `fr` inconditionnel :
l'application efface rx-lang et retombe en auto ; l'auto repondra donc fr.

La branche chinoise (E(L) vrai) est conservee : un systeme chinois reste en chinois.
"""
import io, os, shutil, datetime

BT = '`'
CIBLE = r"J:\Reasonix Studio\resources\frontend-next\dist\assets\i18n-a81XocSl.js"

OLD = "(L.toLowerCase().startsWith(" + BT + "fr" + BT + ")?" + BT + "fr" + BT + ":" + BT + "en" + BT + ")"
NEW = BT + "fr" + BT

if not os.path.exists(CIBLE):
    raise SystemExit("bundle introuvable : " + CIBLE)

s = io.open(CIBLE, encoding="utf-8").read()

n = s.count(OLD)
print("motif trouve :", n, "occurrence(s)")
if n != 1:
    # etat deja force ?
    if "(L.toLowerCase().startsWith(" + BT + "fr" + BT + ")" not in s and "return E(L)?" + BT + "zh" + BT + ":" + BT + "fr" + BT in s:
        print("deja force : rien a faire")
        raise SystemExit(0)
    raise SystemExit("motif inattendu — aucune ecriture")

stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
bak = os.path.join(r"J:\Reasonix\dev\Reasonix-FR-2.50\backups",
                   stamp + "__i18n__auto-fr__" + os.path.basename(CIBLE))
os.makedirs(os.path.dirname(bak), exist_ok=True)
shutil.copy2(CIBLE, bak)
print("sauvegarde :", os.path.basename(bak))

s2 = s.replace(OLD, NEW, 1)
io.open(CIBLE, "w", encoding="utf-8", newline="").write(s2)

# verification
s3 = io.open(CIBLE, encoding="utf-8").read()
ok = ("return E(L)?" + BT + "zh" + BT + ":" + BT + "fr" + BT) in s3
print("verification :", "OK" if ok else "ECHEC")
print("taille :", len(s3), "octets")
