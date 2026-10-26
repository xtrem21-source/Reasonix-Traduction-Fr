# Journal des modifications

Toutes les évolutions notables de ce projet sont documentées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), et ce projet
respecte le [versionnage sémantique](https://semver.org/lang/fr/).

La version anglaise de ce fichier est [`CHANGELOG.md`](CHANGELOG.md).

---

## [2.52.0] — 2026-10-26

Prise en charge de **Reasonix Studio 2.52.0**. Cette version corrige un défaut
qui rendait le choix de langue impossible à conserver : sélectionner le français
rechargeait la fenêtre en anglais.

### Ajouté

- **`Francisation_2.52.bat`**, le lanceur de cette version.
- **`scripts/patch252.py`** : cinq ancres pour le build 2.52 (les six ancres de
  la 2.49 n'existent plus), plus le dictionnaire, le sélecteur de langue, l'écran
  de démarrage et les libellés anglais codés en dur.
- **`--default-lang fr|en|auto`** (ou `REASONIX_UI_DEFAULT`) : la langue sur
  laquelle l'interface retombe quand rien n'est enregistré. La chaîne reste
  générique — le français est un préréglage, pas une règle.
- **`Reasonix-FR-2.52.zip`** : paquet complet, construit **sans** `backups/`,
  contrairement à l'archive 2.50 qui embarquait des copies de code Reasonix
  (`app.asar`, bundles minifiés).
- **174 chaînes** traduites, et **9 entrées** restées en anglais corrigées
  (`Jetons`, `Compacter`, `Clé API`, `Tours`, `Message à envoyer`, `Rang {n}`…).

### Modifié

- **La logique de langue a été réécrite en amont.** La 2.52 stocke
  `b = { zh: {}, en: {…} }`, résout `S = b[x]`, et traduit via
  `A(e,t) = S[e] ?? e`. Les six ancres de la 2.49 ont disparu ; le patch en
  réécrit cinq.
- **Le dictionnaire couvre désormais 100 % du build** : 5 146 chaînes sur 5 146.

### Corrigé

- **Le choix de langue ne retombe plus en anglais.** Cause racine, établie en
  lisant le shell : `preload.js` restaure les préférences de la page depuis
  `window-prefs.json`, et `rx-lang` revient **vide** ; l'origine de la page change
  à chaque lancement (le noyau écoute sur un port local neuf), donc `localStorage`
  démarre vide ; sans valeur, le bundle retombait sur la langue de la machine —
  l'anglais sur une machine non francophone. Le `uilang.js` natif ne connaît que
  `zh` et `en`, il ne pouvait donc pas rétablir le français non plus. Avec cette
  version, une valeur vide résout vers le défaut configuré (`fr`).

### Problèmes connus

- Un choix explicite dépend encore de `rx-lang` enregistré ; si la valeur
  restaurée est vide après un redémarrage, c'est le défaut qui s'applique.
- L'étape native `app.asar` utilise toujours les ancres de la 2.49. Elles ont été
  recontrôlées sur la 2.52 (11/11 remplacements, 4/4 marqueurs) et s'appliquent
  sans modification, mais le lanceur de cette version ne l'exécute pas.

---

## [2.50.0] — 2026-10-24

Prise en charge de **Reasonix Studio 2.50.0**. Cette version a exigé de réécrire
tous les motifs : le minifieur de la 2.50 a fait tourner les noms de variables du
bundle i18n.

### Ajouté

- **`Francisation_2.50.bat`**, le lanceur de cette version, avec les mêmes
  variables et les mêmes gardes que ses prédécesseurs (`REASONIX_STUDIO_DIR`,
  repli Python, contrôle d'instance en cours d'exécution).
- **`scripts/patch250.py`** : même chaîne que la 2.49, avec les six motifs
  réécrits pour les nouveaux noms.
- **`scripts/force_auto_fr.py`** : force la détection automatique de la langue à
  répondre `fr`. Sans lui, le français ne tient pas en 2.50 — voir *Modifié*.
- **`Reasonix-FR-2.50.zip`** : paquet complet et autonome pour cette version.

### Modifié

- **Les noms de variables de l'i18n ont tourné en 2.50.** La langue courante passe
  de `y` à `b`, le dictionnaire courant de `b` à `x`, le recueil des dictionnaires
  de `v` à `y`, et la fonction de traduction de `O` à `k` (exportée en `o`). Les
  motifs de la 2.49 ne correspondent pas à cette build et échouent bruyamment au
  lieu d'écrire.
- **Le sélecteur de langue n'est plus persistant.** Reasonix Studio 2.50 remet son
  réglage de langue à vide au démarrage et retombe en détection automatique. Le
  français tient parce que la détection est forcée en `fr`, pas parce que le choix
  est respecté. Choisir l'anglais dans les réglages ne tiendra pas.

### Problèmes connus

- Deux libellés des réglages, `Ask` et `MCP · Skills`, ne sont pas traduits : leurs
  chaînes sources ont changé en 2.50 et ne correspondent plus au dictionnaire.
- La cause première de la remise à zéro de la langue — quel composant écrit la
  valeur vide — n'est pas identifiée. Elle se trouve probablement dans l'exécutable
  hôte.

---

## [2.49.0] — 2026-10-23

Prise en charge de **Reasonix Studio 2.49.0**. Le bundle web est désormais
`i18n-BR2QJ_aY.js` et le bundle des réglages `Settings-Bbgyi4OO.js`. La version
2.48.0 est volontairement sautée : aucun travail n'a été publié pour elle. Le tag
2.47.0 et sa release restent disponibles, inchangés.

### Ajouté

- **Prise en charge de Reasonix Studio 2.49.0** : `scripts/patch249.py` (interface
  web : bundle i18n, sélecteur de langue des réglages, langue de démarrage dans
  `index.html`) et son lanceur `Francisation_2.49.bat`.
- **77 nouvelles chaînes traduites**, portant `translations/fr.json` à
  **5 034 entrées** (4 957 reprises de la 2.47.0 + 77 nouvelles). Aucune
  traduction n'a été modifiée ni perdue : les 4 957 entrées précédentes sont
  identiques octet pour octet.
- `patch249.py` lit le dossier d'installation depuis `REASONIX_STUDIO_DIR`, si
  bien qu'une installation de Reasonix Studio hors de `%LOCALAPPDATA%\Programs`
  (par exemple `J:\Reasonix Studio`) est patchée correctement.

### Modifié

- `README.md` / `README.fr.md` / `LISEZ-MOI.md` : la version prise en charge est
  désormais **2.49.0** (bundles `i18n-BR2QJ_aY.js`, `Settings-Bbgyi4OO.js`).
- Les scripts 2.46.0 et 2.47.0 sont conservés dans `scripts/` pour ceux qui
  restent sur ces builds.
- `patch249.py` est idempotent : sur un bundle déjà patché, il rafraîchit le
  dictionnaire au lieu de réappliquer les ancres, et il refuse de patcher si un
  motif ne correspond plus exactement une fois.

### Limites connues

- Cible **Reasonix Studio 2.49.0**. Une version plus récente peut déplacer les
  ancres ; l'injection échoue visiblement (jamais silencieusement) quand cela
  arrive.
- **L'étape native `app.asar` n'est pas portée en 2.49.** Les utilisateurs de la
  2.49 obtiennent l'interface web entièrement traduite ; les surfaces natives
  (page de démarrage, menu contextuel, zone de notification) restent non
  traduites jusqu'à ce que `patch_asar249.py` existe.

---

## [2.47.0] — 2026-10-21

Prise en charge de **Reasonix Studio 2.47.0**. Le bundle web est désormais
`i18n-DS26LhWq.js` et le bundle des réglages `Settings-B_4tuZ4i.js` ; les ancres
natives de `app.asar` ont été revérifiées. Le tag 2.46.0 et sa release restent
disponibles, inchangés.

### Ajouté

- **Prise en charge de Reasonix Studio 2.47.0** : `scripts/patch247.py` (interface
  web : bundle i18n, sélecteur de langue des réglages, langue de démarrage dans
  `index.html`) et `scripts/patch_asar247.py` (8 fichiers natifs : `uilang.js`,
  `starting.js`, `editmenu.js`, `hostexit.js`, `shelllog.js`, `packagegrants.js`,
  `main.js`, `tray.js`), piloté par `scripts/asar_patches.json`.
- **160 nouvelles chaînes traduites**, portant `translations/fr.json` à
  **4 957 entrées** (4 797 reprises de la 2.46.0 + 160 nouvelles).
- Un module de dictée optionnel est livré dans `Reasonix-Voice-Input-publish/`,
  piloté par `MENU-REASONIX.bat`, qui propose trois modes : **français seul**,
  **micro seul**, ou **les deux**. Le module est indépendant de la traduction et
  peut être installé seul, à côté du pack français, ou pas du tout.

### Modifié

- `README.md` / `README.fr.md` : la version prise en charge est désormais
  **2.47.0** (bundles `i18n-DS26LhWq.js`, `Settings-B_4tuZ4i.js`).
- Les scripts 2.46.0 et 2.40.0 sont conservés dans `scripts/` pour ceux qui
  restent sur ces builds.
- Les deux patches sont idempotents : une réexécution détecte un bundle déjà
  patché et le signale au lieu de réécrire.

### Limites connues

- Cible **Reasonix Studio 2.47.0**. Une version plus récente peut déplacer les
  ancres ; l'injection échoue visiblement (jamais silencieusement) quand cela
  arrive.

---

## [2.46.0] — 2026-10-20

Prise en charge de **Reasonix Studio 2.46.0**. C'est la version majeure : le
bundle de l'interface a changé de forme, 946 nouvelles chaînes ont été ajoutées,
et les ancres natives ont été revérifiées. Elle remplace le tag `v0.2.0`, de
courte durée, qui pointait vers le même contenu sous l'ancienne numérotation.

### Ajouté

- **Prise en charge de Reasonix Studio 2.46.0** : le bundle de l'interface a
  changé de forme depuis la 2.40.0 (dictionnaires et fonctions renommés : `h` →
  `_`, `T` → `D`, `x` → `C`, `w` → `E`). De nouveaux injecteurs correspondent aux
  ancres de la 2.46.0 : `scripts/inject_fr_246.py` (interface web) et
  `scripts/asar_246.py` (surfaces natives), avec `scripts/setup_asar_orig_246.py`
  et `scripts/verify_asar_246.py`.
- **946 nouvelles chaînes traduites**, portant `translations/fr.json` à
  **4 797 entrées** (3 866 reprises de la 0.1.0 + 946 nouvelles).
- `scripts/check_placeholders.py` valide désormais directement le dictionnaire
  final (`translations/fr.json`), et non les fichiers de travail intermédiaires.

### Modifié

- `README.md` / `README.fr.md` : la version prise en charge est désormais
  **2.46.0** (bundles `i18n-BBt-pvJM.js`, `Settings-DVNS8HMO.js`).
- Les scripts 2.40.0 sont conservés dans `scripts/` pour ceux qui restent sur ce
  build.

### Limites connues

- Cible **Reasonix Studio 2.46.0**. Une version plus récente peut déplacer les
  ancres ; l'injection échoue visiblement (jamais silencieusement) quand cela
  arrive.

---

## [0.1.0] — 2026-10-16

Première version publique.

### Ajouté

- **Chaîne de traduction générique** pour Reasonix Studio, en cinq étapes :
  `extract` → `translate` → `merge` → `inject` → `verify`.
- **Extraction** des chaînes de l'interface depuis une copie installée de
  Reasonix Studio (`scripts/extract_i18n.py`), y compris le dictionnaire à clés
  chinoises contenu dans les bundles minifiés de l'interface.
- **Injection du dictionnaire** (`scripts/inject_fr.py`) : ajoute le dictionnaire
  traduit au bundle de l'interface, apprend le nouveau code au résolveur de
  langue, et ajoute la langue au sélecteur de langue de l'application.
- **Traduction des surfaces natives** (`scripts/patch_asar.py`,
  `scripts/repack_asar.py`, `scripts/install_asar.py`) : page de démarrage, menu
  contextuel, boîtes d'erreur, dialogue d'installation héritée, et menu de la zone
  de notification.
- **Vérification** (`scripts/verify_installed.py`,
  `scripts/verify_asar_installed.py`) : charge le bundle *installé* et prouve
  qu'il traduit, au lieu de le supposer.
- **Sécurité des jetons de format** (`scripts/check_placeholders.py`) : échoue si
  un `{placeholder}` est perdu, renommé ou ajouté dans une traduction.
- **Outils de travail par lots** : `scripts/next_batch.py` (affiche les chaînes
  suivantes à traduire) et `scripts/translate_api.py` (traduction par lots
  optionnelle via l'API DeepSeek).
- **Traduction française complète** : `translations/fr.json`, 3 866 chaînes.
- **Résolution de chemins portable** (`scripts/paths.py`) : le projet peut être
  cloné, copié ou déplacé n'importe où ; il localise Reasonix Studio depuis
  l'environnement et ne code jamais un chemin en dur.
- **Sauvegardes automatiques** : chaque fichier que l'injecteur remplace est copié
  dans un dossier daté sous `work/backup/` avant d'être écrasé.
- **Documentation** : `README.md` (anglais), `README.fr.md` (français),
  `docs/STRUCTURE.md`, `docs/WORKFLOW-TRANSLATE.md`, `docs/LIMITATIONS.md`,
  `docs/PRE-PUBLISH-CHECKLIST.md`, et des brouillons d'annonce sous
  `docs/LAUNCH/`.

### Limites connues

- Cible **Reasonix Studio 2.40.0**. Les bundles de l'interface sont minifiés et
  portent une empreinte de contenu ; une version différente peut déplacer les
  ancres. L'injection échoue visiblement (jamais silencieusement) quand cela
  arrive.
- **Gestion des chemins orientée Windows.** macOS et Linux ne sont pas testés.
- **Interface web et coque Electron uniquement.** Le backend Go (CLI, texte
  d'état de la zone de notification, notifications) compile ses chaînes dans un
  binaire et sort du périmètre.
- **Le français est la seule traduction complète** livrée.

### Sécurité et vie privée

- Aucun code de DeepSeek-Reasonix n'est redistribué. L'outil agit sur
  l'installation de l'utilisateur.
- L'outil de traduction par API est **optionnel** et envoie des chaînes de
  l'interface au fournisseur configuré (DeepSeek par défaut). Aucune autre étape
  ne touche au réseau.

### Crédits

- **[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)** — maintenu
  par **Huahui Yu** et ses contributeurs — pour l'application que cet outil sert.
  Sous licence MIT ; voir [`LICENSE-REASONIX.md`](LICENSE-REASONIX.md).
- Non officiel et sans affiliation avec l'amont.

[2.46.0]: https://github.com/xtrem21-source/Reasonix-Traduction-Fr/releases/tag/v2.46.0
[0.1.0]: https://github.com/xtrem21-source/Reasonix-Traduction-Fr/releases/tag/v0.1.0
