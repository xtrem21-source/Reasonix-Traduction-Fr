# Contribuer

Ce pack répare une application tierce après ses mises à jour. Les contributions sont bienvenues
tant qu'elles tiennent les deux règles qui le rendent lisible : **tout est bilingue**, et **rien
n'est deviné**.

## Ce qui est utile

- **Une casse amont** : une version de Reasonix Studio qui change un nom de bundle, une ancre dans
  `main.js`, `preload.js` ou le menu contextuel. Donnez la version (`FileVersion`) et le message
  exact de `mettre-a-jour.bat`.
- **Une traduction manquante** : le moteur écrit `a-traduire.tsv` et n'applique rien. Remplissez la
  colonne `francais` et ouvrez une *pull request* avec le `dict/fr.json` mis à jour.
- **Un problème de micro** : fournisseur, modèle, message d'erreur, et si « Tester la clé API » est
  passé.
- **Une chaîne française fautive** : dites quel écran, citez l'anglais, proposez le français.

## Ce qui n'est pas accepté

- **Une traduction devinée.** Une chaîne manquante arrête le passage ; ne la remplissez pas avec une
  supposition automatique.
- **Un numéro de version dans un script.** La version est lue dans `Reasonix Studio.exe`
  (`FileVersion`) ; rien n'est codé en dur.
- **Les fichiers générés** : `logs/`, `backups/`, `tools/node_modules/`, `dict/etat.json`,
  `dict/catalog.json`, `a-traduire.tsv`. Ils sont dans `.gitignore` pour cette raison.
- **Une clé, un `mic-keys.bin`, un `.env`.** Jamais dans une *issue*, un commit ou une capture.

## Avant d'ouvrir une pull request

1. `python tools/maj.py --no-apply` — doit finir par `OK - tout est conforme`.
2. `python tools/patch_skills.py --check` — doit finir par `a traduire : 0`, sauf si la *pull
   request* porte précisément sur ce point.
3. `python tools/selftest.py` — le pipeline rejoué sur une copie de l'application.
4. Si vous avez touché `tools/asar_patches.json` : `python tools/patch_asar252.py --dry-run` doit
   afficher `syntaxe : OK sur les 9 fichiers` et `verification du paquet : 4/4 marqueurs`.

## Style

- **Deux langues, même contenu.** `README.md` / `README.fr.md`, `CHANGELOG.md` /
  `CHANGELOG.fr.md`, `SECURITY.md` / `SECURITY.fr.md`. Une traduction, pas un résumé.
- **Messages de commit** : `type: ce qui change`, à l'impératif, une ligne de résumé puis un corps
  si nécessaire — `fix: le bloc read-env doit se terminer par son ancre`.
- **Les commentaires** expliquent *pourquoi*, en français, sans accents dans les chemins de code
  que PowerShell 5.1 lit en ANSI (les fichiers `.ps1`).
- **Les `.bat` restent en CRLF.** `cmd.exe` calcule la position des labels en supposant CRLF ; un
  fichier en LF fait sauter `goto` trop loin **sans aucun message**. `normaliser-crlf.ps1` remet
  tout un pack d'aplomb.

## Signaler un problème de sécurité

N'ouvrez pas d'*issue* publique. Décrivez-le dans les termes de `SECURITY.fr.md` (étape, version,
lignes de journal) et considérez que la limite du coffre est documentée : un processus lancé sous
le même compte Windows peut déchiffrer `mic-keys.bin`. C'est une limite connue, pas une faille.
