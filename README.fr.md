# Reasonix-Traduction-Fr

**Traduisez l'interface de Reasonix Studio dans votre langue.**

Reasonix-Traduction-Fr est une petite chaîne d'outils lisible qui permet de traduire
l'interface de **Reasonix Studio** — l'application desktop du projet
[**DeepSeek-Reasonix**](https://github.com/esengine/DeepSeek-Reasonix) — dans
n'importe quelle langue, sans recompiler l'application et sans son code source.

Le français est fourni comme démonstration complète et fonctionnelle. L'outil
n'est pas spécifique au français : c'est une chaîne générique
(extraire → traduire → injecter → vérifier) que chacun peut diriger vers une
autre langue.

> **Non officiel.** Ce projet n'est ni affilié à, ni approuvé par, ni sponsorisé
> par le projet DeepSeek-Reasonix (Reasonix Studio) ni par ses mainteneurs.
> Voir [Non-affiliation](#non-affiliation).

---

## Sommaire

- [Pourquoi ce projet existe](#pourquoi-ce-projet-existe)
- [Comment ça marche](#comment-ça-marche)
- [Prérequis](#prérequis)
- [Installer et utiliser (français, en 3 étapes)](#installer-et-utiliser-français-en-3-étapes)
- [Ajouter une nouvelle langue](#ajouter-une-nouvelle-langue)
- [Versions supportées](#versions-supportées)
- [Limites connues](#limites-connues)
- [Structure du dépôt](#structure-du-dépôt)
- [Non-affiliation](#non-affiliation)
- [Crédits](#crédits)
- [Licence](#licence)

---

## Pourquoi ce projet existe

Reasonix Studio ne propose son interface qu'en chinois et en anglais. Toute
personne qui ne parle ni l'une ni l'autre en est exclue — non pas parce que le
logiciel est fermé, mais parce que ses traductions sont compilées dans
l'application et qu'il n'existe aucun moyen public d'en ajouter une.

Reasonix-Traduction-Fr comble ce manque. Il lit les catalogues de chaînes de
l'interface — les sources de traduction de l'application — pour que vous puissiez
traduire les parties que vous voyez réellement, dans un simple fichier texte,
puis les appliquer localement. Aucun code Reasonix n'est redistribué : les
catalogues sont téléchargés sur votre machine, et la traduction est appliquée à
votre propre installation.

L'objectif est de rendre ce logiciel utilisable par des personnes qu'il exclut
aujourd'hui.

---

## Comment ça marche

Reasonix Studio est une application Electron. Le texte de son interface vit à
deux endroits :

1. **Interface web** — des bundles JavaScript minifiés servis à la fenêtre.
   Chaque phrase visible est une paire clé/valeur dans un dictionnaire situé dans
   le bundle `i18n-*.js`. Les clés sont les chaînes chinoises d'origine ; les
   valeurs sont la traduction anglaise. Injecter un nouveau dictionnaire donne à
   l'interface une nouvelle langue.
2. **Coque native** — le processus principal Electron (`app.asar`) : la page de
   démarrage, le menu clic droit, les dialogues d'erreur et le menu du tray.

L'outillage traite les deux :

```
extract  →  translate  →  merge  →  inject  →  verify
 (lire)      (vous)       (vérifier) (appliquer) (prouver)
```

- **extract** extrait les clés des catalogues amont — les sources i18n de
  l'application, récupérées localement et jamais republiées.
- **translate** est *votre* étape : toute méthode convient — à la main, un tableur,
  ou un modèle d'IA. Un utilitaire de traduction par lots (API DeepSeek) est
  fourni, mais il est optionnel.
- **merge** rassemble vos morceaux traduits et les contrôle (clés manquantes, clés
  inconnues, `{placeholders}` cassés).
- **inject** applique le résultat à votre installation.
- **verify** recharge le bundle patché et confirme qu'il traduit réellement.

Chaque étape est un petit script Python que vous pouvez lire de bout en bout.

---

## Prérequis

| Besoin | Pourquoi |
|---|---|
| **Reasonix Studio installé** | L'outil patche votre propre installation. |
| **Python 3.8+** | Tous les scripts sont en Python pur, bibliothèque standard seulement. |
| **Node.js** | Uniquement pour lire/écrire `app.asar` (outil `asar`). |
| **Windows** | Voir [Limites connues](#limites-connues) — les scripts actuels supposent Windows. |

Aucune compilation, aucun compilateur, pas d'internet (sauf pour l'étape
optionnelle de traduction par IA et la récupération des chaînes sources).

---

## Installer et utiliser (français, en 3 étapes)

> Sauvegardez avant de commencer. L'injecteur écrit dans votre application
> installée. Il conserve des sauvegardes datées de chaque fichier remplacé, sous
> `work/backup/`, mais une copie du dossier d'installation n'est jamais inutile.

```bash
git clone https://github.com/xtrem21-source/Reasonix-Traduction-Fr.git
cd Reasonix-Traduction-Fr
```

**1. Récupérer et extraire les chaînes**

```bash
python3 scripts/fetch_sources.py   # télécharge les catalogues de chaînes amont
python3 scripts/extract_i18n.py    # en extrait les clés à traduire
```

Les catalogues sont les sources i18n de l'application. Ils sont téléchargés dans
`sources/` (jamais committé) et transformés en un fichier JSON par groupe d'écrans
dans `work/extracted/`.

**2. Traduire**

Soit vous déposez une traduction existante dans `translations/<code>.json` (voir
[Ajouter une nouvelle langue](#ajouter-une-nouvelle-langue)), soit vous partez de
zéro avec l'utilitaire par lots :

```bash
python3 scripts/next_batch.py 60          # affiche les 60 chaînes suivantes à traduire
python3 scripts/check_placeholders.py     # vérifie que les {placeholders} sont intacts
```

La traduction française, `translations/fr.json`, est complète et peut servir de
référence pour le format et le ton.

**3. Injecter et vérifier**

```bash
python3 scripts/inject_fr.py              # applique le dictionnaire + patche les bundles
python3 scripts/verify_installed.py       # prouve que le bundle installé traduit
```

Redémarrez Reasonix Studio. Dans **Paramètres → Langue**, choisissez **Français**.

---

## Dictée vocale (en option)

Cette version intègre aussi un **module de dictée vocale optionnel** : un bouton
micro dans la barre du chat, qui utilise l'API Web Speech pour la capture et
Gemini pour la transcription (BYOK — vous fournissez votre clé).

Le lanceur unifié `MENU-REASONIX.bat` propose **trois modes**, pour n'appliquer
qu'une partie si vous le souhaitez :

| Choix | Ce qui est patché |
|---|---|
| `1` — Français | Interface web + menu contextuel natif, rien d'autre |
| `2` — Micro | Bouton de dictée uniquement |
| `3` — Les deux | Français **et** dictée |
| `4` — Quitter | Rien |

En ligne de commande : `MENU-REASONIX.bat fr`, `MENU-REASONIX.bat mic` ou
`MENU-REASONIX.bat both` (utile pour les scripts et la CI).

Le module vit dans `Reasonix-Voice-Input-publish/` et reste **indépendant de la
traduction** : il peut s'installer seul sur un Reasonix Studio non traduit, ou
avec le pack français. Chaque action est journalisée dans `logs/`, et les
fichiers patchés sont sauvegardés avec un horodatage.

---

## Ajouter une nouvelle langue

Le flux est identique pour toutes les langues. Remplacez `xx` par le code de votre
langue (par exemple `es`, `de`, `ja`).

1. **Extraire les chaînes sources.** `python3 scripts/extract_i18n.py` les écrit
   dans `work/extracted/`. Ces clés sont le texte chinois d'origine et ne doivent
   **pas** être modifiées — ce sont les clés de recherche.

2. **Créer votre dictionnaire.** Copiez `translations/fr.json` vers
   `translations/xx.json`, puis remplacez les valeurs (gardez les clés). Le
   fichier est un objet JSON plat :

   ```json
   {
     "重命名聊天": "Rename the conversation",
     "聊天标题": "Chat title"
   }
   ```

   - Clés : **chaînes chinoises d'origine — ne les traduisez pas, ne les modifiez pas.**
   - Valeurs : **votre langue.**
   - Conservez chaque `{placeholder}` exactement tel quel (`{n}`, `{name}`,
     `{alt}`…). `scripts/check_placeholders.py` le vérifie pour vous.

3. **Contrôler votre travail.** `python3 scripts/merge_fr.py` signale les clés
   manquantes, les clés inconnues et (via `check_placeholders.py`) les placeholders
   cassés.

4. **Injecter et vérifier.**
   ```bash
   python3 scripts/inject_fr.py
   python3 scripts/verify_installed.py
   ```

5. **Partager.** Ouvrez une pull request ajoutant `translations/xx.json`. Vous
   n'avez pas besoin de traduire les ~3 900 chaînes pour être utile — un
   dictionnaire partiel se dégrade proprement : toute chaîne absente s'affiche
   dans son chinois d'origine, jamais comme un vide.

Un guide plus détaillé se trouve dans [`docs/WORKFLOW-TRANSLATE.md`](docs/WORKFLOW-TRANSLATE.md).

---

## Versions supportées

Les bundles de l'interface sont **minifiés et hachés par contenu**, et les chaînes
sont patchées en recherchant des ancres dans ce code minifié. Par conséquent, cet
outil est **lié à une version précise de Reasonix Studio**.

| Composant | Version |
|---|---|
| Reasonix Studio | **2.50.0** — la version sur laquelle l'outil a été développé et testé |
| Release amont | `studio-v2.50.0` (2026-10-23) |
| Bundles de l'interface | `i18n-a81XocSl.js`, `Settings-PYycLyo5.js` (les noms changent à chaque version) |

**Vérifiez votre version avant d'appliquer.** Ouvrez le panneau *À propos* de
l'application, ou lisez le champ `version` de `resources/app.asar` dans le dossier
d'installation. (Les sources amont déclarent `0.0.0` et injectent la vraie version
à la compilation : le binaire installé est le seul endroit où ce numéro existe.)

- **`2.50.0` est la version sur laquelle les ancres ont été vérifiées.**
  Reasonix Studio publie fréquemment ; une version plus récente peut déplacer
  les ancres. Au moment de la rédaction, la version amont était `2.50.0`.
- Sur une **autre version**, l'extraction fonctionne en général encore (elle lit
  les catalogues de chaînes, pas le bundle compilé), mais **l'injection peut
  échouer** : les ancres peuvent avoir bougé. L'injecteur signale alors les motifs
  introuvables au lieu de corrompre quoi que ce soit.
- Les scripts ne s'appliquent **jamais** à l'aveugle : chaque patch est vérifié
  comme correspondant exactement une fois ; une correspondance ratée est signalée
  et ignorée.
- Quand une version plus récente casse les ancres, il suffit de mettre à jour les
  motifs dans `scripts/patch250.py` (les scripts 2.46.0 et 2.47.0 sont conservés
  dans `scripts/` pour qui reste sur ces versions). Les contributions pour les
  versions plus récentes sont bienvenues.

---

## Limites connues

Liste honnête, pour que personne ne soit surpris :

- **Orienté Windows.** Les chemins passent par `%LOCALAPPDATA%`. La logique est
  facile à porter, mais macOS/Linux ne sont pas testés et demanderaient de
  petites modifications dans `scripts/paths.py`.
- **Application desktop Electron uniquement.** Le backend Go (CLI, texte du tray,
  notifications) embarque ses chaînes **compilées dans un binaire** et sort du
  périmètre. Seule une petite portion de quelques surfaces natives est concernée.
  Voir `docs/LIMITATIONS.md`.
- **Lié à Reasonix Studio 2.50.0** pour l'injection — vérifiez votre version
  avant d'appliquer (voir ci-dessus).
- **La 2.50.0 n'est prise en charge que pour l'interface web.** L'étape native
  `app.asar` (`scripts/patch_asar247.py`) n'a pas encore été portée : en 2.49,
  l'interface est entièrement traduite, les surfaces natives ne le sont pas.
- **Le français est la seule traduction complète** fournie. Les autres langues
  sont des contributions de la communauté.
- **Les traductions partielles sont attendues et sûres.** Une clé manquante
  retombe sur le chinois, pas sur un vide ni une erreur.
- **L'étape `asar` exige Node.** Sans Node, la traduction de l'interface web
  fonctionne quand même ; seules les surfaces natives (page de démarrage, menu
  clic droit, tray) sont ignorées.
- **L'injection modifie votre installation.** Désinstaller ou mettre à jour
  Reasonix Studio remplace les fichiers patchés ; relancez l'injecteur ensuite.
  Les fichiers d'origine sont conservés sous `work/backup/`.

---

## Structure du dépôt

```
Reasonix-Traduction-Fr/
├── README.md                  # ce fichier (anglais)
├── README.fr.md               # version française
├── LICENSE                    # MIT — pour ce projet
├── LICENSE-REASONIX.md        # MIT — la licence d'origine de DeepSeek-Reasonix
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitattributes             # normalise les fins de ligne selon la plateforme
├── .gitignore
├── scripts/                   # l'outillage
│   ├── paths.py               #   résout tous les chemins (portable)
│   ├── fetch_sources.py       #   télécharger les catalogues de chaînes amont
│   ├── extract_i18n.py        #   extraire les clés traduisibles
│   ├── next_batch.py          #   afficher les prochaines chaînes à traduire
│   ├── translate_api.py       #   optionnel : traduction par lots via API IA
│   ├── merge_fr.py            #   assembler + contrôler les morceaux traduits
│   ├── check_placeholders.py  #   vérifier que les {placeholders} survivent
│   ├── inject_fr.py           #   appliquer le dictionnaire aux bundles
│   ├── patch_asar.py          #   traduire les chaînes natives Electron
│   ├── repack_asar.py         #   reconstruire app.asar
│   ├── install_asar.py        #   l'installer (avec sauvegarde)
│   ├── setup_asar_orig.py     #   obtenir un app.asar d'origine comme référence
│   ├── vendor_asar.py         #   embarquer l'outil asar dans work/tools
│   ├── scan_repo.py           #   détecter ce qui ne doit pas être publié
│   ├── go_extract.py          #   diagnostic : le backend Go est hors périmètre
│   ├── probe_api.py           #   optionnel : vérifier qu'une clé API est dispo
│   └── verify_*.py, verify_i18n.mjs   # prouver le résultat
├── translations/
│   └── fr.json                # le dictionnaire français (complet)
├── docs/
│   ├── STRUCTURE.md
│   ├── WORKFLOW-TRANSLATE.md
│   ├── LIMITATIONS.md
│   ├── PRE-PUBLISH-CHECKLIST.md
│   └── LAUNCH/                # brouillons d'annonces
└── work/                      # généré à l'exécution — jamais committé
```

---

## Non-affiliation

C'est un projet **indépendant et non officiel**. Il n'est **ni affilié à, ni
approuvé par, ni sponsorisé par** le projet
[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)
(Reasonix Studio), son mainteneur, ni ses contributeurs.

- Il ne contient **aucun code source de DeepSeek-Reasonix** — ni `app.asar`, ni
  bundles JavaScript, ni binaire Go. Il opère sur *votre* copie installée, sur
  votre machine.
- « DeepSeek-Reasonix » et « Reasonix Studio » désignent le projet d'origine, qui
  appartient à ses auteurs. Tous les droits sur ces noms et ce logiciel leur
  restent acquis.
- Le DeepSeek-Reasonix d'origine est sous licence MIT ; une copie est conservée
  dans [`LICENSE-REASONIX.md`](LICENSE-REASONIX.md).

---

## Crédits

- **[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)** — le
  projet que cet outil sert — et les personnes qui le construisent :
  - **Huahui Yu** — mainteneur.
  - Les [contributeurs de DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix/graphs/contributors) —
    pour l'application, son texte d'interface et les catalogues de langue que cet outil lit.
- Le texte de la licence MIT de DeepSeek-Reasonix est reproduit dans
  [`LICENSE-REASONIX.md`](LICENSE-REASONIX.md), comme ses termes l'exigent.
- L'outil `asar` (embarqué, ou installé à la demande) — MIT, par le projet
  Electron.
- Traduction française : contribuée par les auteurs de ce projet.

---

## Licence

**MIT** — voir [`LICENSE`](LICENSE).

Vous pouvez utiliser, modifier et redistribuer cet outil et les traductions qu'il
contient, à condition de conserver la mention de copyright et la notice de licence
de Reasonix.
