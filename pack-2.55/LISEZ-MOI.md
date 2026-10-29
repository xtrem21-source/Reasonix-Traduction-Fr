# Reasonix — traduction automatique

> Met à jour la traduction française de Reasonix Studio **après chaque mise à jour de l'application**, sans intervention de l'assistant.
> Un double-clic. Il fait le travail mécanique et ne s'arrête que s'il manque du sens.

## Utilisation

```text
1. Fermer complètement Reasonix Studio
   (icône de la zone de notification → Quitter)
2. Double-cliquer mettre-a-jour.bat
3. Remplir a-traduire.tsv s'il le demande, puis relancer
4. Rouvrir Reasonix Studio
```

Au démarrage, il vous dit où il en est :

| Ce qu'il affiche | Ce que ça veut dire |
|---|---|
| `OK - tout est conforme` puis une question | rien ne manque ; **Entrée** applique, **Q** quitte |
| `N nouvelle(s) chaine(s) a traduire` | il a écrit `a-traduire.tsv` et `a-traduire.txt`, et **n'a rien appliqué** |
| `format non valide` / `correspondance non valide` / `traduction refusee` | le fichier est refusé, ligne par ligne ; **rien n'est écrit** |
| `ECHEC` | le journal (`logs\journal.log`) dit où |

## Fermeture de Studio

Le `.bat` s'en occupe — inutile de penser à la zone de notification :

| Étape | Ce qui se passe |
|---|---|
| 1 | demande de **fermeture propre** (WM_CLOSE), puis 6 s d'attente |
| 2 | si le processus est encore là : **compte à rebours de 5 s** (Ctrl+C pour annuler), puis fermeture forcée de **Studio seul** |
| 3 | le noyau (`reasonix-studio-host.exe`) est **laissé sortir seul** ; il n'est forcé qu'après 6 s s'il s'accroche |

Un arrêt forcé peut afficher au démarrage suivant « *Le noyau s'est arrêté de façon inattendue* » : c'est un avertissement, pas une perte. Sessions, réglages et mémoire sont sur disque.

Deux modes de test, qui ne ferment **ni n'appliquent** rien :

```text
mettre-a-jour.bat --test          montre la détection et s'arrête
set REASONIX_ONLY_CLOSE=1         ferme seulement, n'applique rien
```

## Python

Le moteur est un script Python : sans Python 3, rien ne peut être appliqué.
Le `.bat` le vérifie **avant** de fermer Studio, puis le cherche dans cet ordre :

| Étape | Quoi |
|---|---|
| 1 | `%PY%` de `config.bat` |
| 2 | le lanceur officiel `py -3` |
| 3 | `%LOCALAPPDATA%\Programs\Python\Python313` → `310`, puis `%ProgramFiles%` |
| 4 | `C:\Python313`, `C:\Python312` |

S'il ne trouve rien, il propose d'installer Python 3.13 par `winget`. **Sans accord explicite, il n'installe rien.** Un `python` non installé du Microsoft Store est refusé : le test est l'exécution réelle, pas la présence dans le `PATH` (ce raccourci répond par un code d'erreur).

## Fins de ligne

Tous les `.bat` sont en **CRLF**. Ce n'est pas cosmétique : `cmd.exe` calcule la position des labels en supposant CRLF ; en LF pur, un `goto` saute trop loin **sans aucun message d'erreur**. Constaté le 2026-10-28 sur `mettre-a-jour.bat`.

`normaliser-crlf.ps1` reconvertit tout le pack, sauvegarde comprise :

```text
powershell -NoProfile -ExecutionPolicy Bypass -File normaliser-crlf.ps1
```

Il est idempotent et n'écrase jamais une sauvegarde existante.

## Le fichier de traduction

`a-traduire.tsv` — trois colonnes, tabulations, ouvrable dans Excel ou LibreOffice :

| Colonne | Contenu |
|---|---|
| `id` | identifiant technique — **ne pas y toucher** |
| `anglais` | le texte à traduire (la base anglaise est plus lisible que le chinois d'origine) |
| `francais` | **la seule colonne à remplir** |

`a-traduire.txt` contient les mêmes phrases numérotées, pour les coller dans un traducteur en ligne. Le rapprochement se fait par `id`, jamais par position : un décalage de ligne ne casse rien.

Ce qui est **refusé**, avec le numéro de ligne :

| Contrôle | Message |
|---|---|
| 3 colonnes par ligne | `format non valide` |
| pas de tabulation dans le texte | `format non valide` |
| chaque `id` attendu, une seule fois | `correspondance non valide` |
| pas d'`id` inconnu | `correspondance non valide` |
| traduction non vide | `incomplet` |
| placeholders identiques (`{n}`, `{name}`…) | `traduction refusee` |
| aucun caractère chinois | `traduction refusee` |

## Ce qu'il applique

| Étape | Effet |
|---|---|
| Interface | dictionnaire FR injecté dans le bundle réellement chargé ; sélecteur de langue |
| Libellés en dur | les textes chinois écrits directement dans les bundles (menus de réglages, libellés d'état, prestataires, infobulles, descriptions) sont réécrits en français — ils ne passent pas par le dictionnaire |
| Langue par défaut | sans langue enregistrée, l'interface s'ouvre en français (réglable) |
| Écran de démarrage | « Connexion au noyau… » en français ; sans ça, un document en `lang=fr` affichait le chinois |
| Bouton d'arrêt | rond et rouge avec un « S », à la place du rectangle « Arrêter » qui débordait |
| Coffre des clés | les trois clés du module micro (`GEMINI_API_KEY`, `GROQ_API_KEY`, `ELEVENLABS_API_KEY`) sont chiffrées par Windows (Electron `safeStorage` = DPAPI) dans `data\home\mic-keys.bin` ; les lignes correspondantes sont retirées de `.env` au premier démarrage |
| Micro | bouton de dictée réinstallé (`voice-input.js` + balise dans `index.html`) |
| Chaînes natives | menu contextuel, tray, écran de démarrage, dialogues de plantage |
| Vérification | **toutes** les chaînes du build doivent rendre du français, sinon échec ; les libellés en dur sont comptés à part |

## Réglages

Tout est dans `config.bat` :

| Variable | Défaut | Rôle |
|---|---|---|
| `REASONIX_APP` | `J:\Reasonix Studio` | **premier essai** : le lanceur cherche ailleurs si ce dossier ne répond pas |
| `REASONIX_UI_DEFAULT` | `fr` | langue de repli : `fr`, `en` ou `auto` |
| `PY` | Python 3.13, sinon `python` | interpréteur |
| `REASONIX_NODE` | vide | Node facultatif ; l'Electron de Studio sert de repli |

## Portable : où est Studio ?

Le pack n'est plus lié à un disque. Au lancement, dans cet ordre :

| Étape | Quoi |
|---|---|
| 1 | le chemin de `config.bat` (ou de `config.local.bat` s'il existe) |
| 2 | `%LOCALAPPDATA%\Programs\Reasonix Studio`, `%ProgramFiles%`, `%ProgramFiles(x86)%` |
| 3 | le registre de désinstallation (entrée dont le nom contient « Reasonix Studio ») |
| 4 | la racine de chaque disque monté (`X:\Reasonix Studio`) |
| 5 | **une fenêtre** : on choisit le dossier à la main (3 essais) |

Un dossier n'est accepté que s'il contient `Reasonix Studio.exe` **et**
`resources\frontend-next\dist\index.html`. La réponse est mémorisée dans
`config.local.bat`, qui n'est jamais livré avec le pack — donc une mise à jour
du pack ne l'efface pas.

Ce qui est réécrit à l'application, et pas seulement `config.bat` :

| Élément | Pourquoi |
|---|---|
| pont `shell:send-key` dans `main.js` | il contient le chemin absolu de `winh.ps1` ; il est réécrit avec le dossier réel |
| `winh.ps1` + `dicter.bat` | le pack les **embarque** (`tools\voix-winh\`) et les pose dans `<app>\data\dev\voix-winh\` s'ils manquent |
| journal de `winh.ps1` | calculé depuis le dossier du script, plus de `J:` figé |

Sans ces trois points, le micro marcherait mais **Win+H pointerait dans le vide,
sans message**.

## Reprendre la main

| Situation | Geste |
|---|---|
| **Revenir en arrière** | double-clique `restaurer.bat` : il liste les sauvegardes disponibles, demande confirmation, et remet chaque fichier dans son état d'avant. Garde-fou : l'état actuel est sauvegardé avant d'être écrasé |
| Voir sans rien toucher | `restaurer.bat --liste` |
| `app.asar` cassé | aucune sauvegarde de l'asar n'est conservée : la sortie est de **réinstaller Studio** (l'installeur remet le paquet d'origine) |
| Doute sur l'état | `python tools\maj.py --app "J:\Reasonix Studio" --no-apply` — rapport seul, rien d'écrit |
| Vérifier le pack lui-même | `python tools\selftest.py` — 23 contrôles, aucun ne touche à l'application réelle |

## Ce qu'il ne fait pas

- Il **ne traduit pas** : il prépare le fichier, vous apportez le sens.
- Il **ne devine pas** une case vide : il s'arrête.
- Il ne touche ni à `config.toml`, ni aux réglages, ni aux sessions.
- Il n'efface rien : chaque fichier remplacé est sauvegardé avant.

## Contenu

```text
mettre-a-jour.bat          le double-clic
restaurer.bat              revenir a l'etat d'avant (double-clic, demande confirmation)
verifier-cles.bat          etat du coffre des cles, sans jamais en afficher une
config.bat                 chemins et langue de repli
config.local.bat           cree par le lanceur : dossier de Studio (jamais livre)
normaliser-crlf.ps1        remet les .bat en CRLF, avec sauvegarde
tools\maj.py               le moteur (extraction, ecart, controles, application)
tools\patch252.py          patch de l'interface (i18n, selecteur, ecran de demarrage)
tools\patch_literals.py    libelles ecrits en dur dans les bundles (props, filtres, etats)
tools\ui-fr.css            retouches d'apparence (bouton d'arret rond et rouge)
tools\verifier-cles.py     etat du coffre (present, entrees, .env propre)
tools\patch_asar252.py     chaines natives
tools\trouver-studio.ps1   ou est installe Studio (config, registre, disques, fenetre)
tools\voix-winh\           winh.ps1 + dicter.bat, poses dans <app>\data\dev\voix-winh
tools\extract.mjs          extraction du catalogue du build
tools\verify.mjs           verification en execution (toutes les chaines)
tools\selftest.py          23 tests, sur une copie de l'application
dict\fr.json               dictionnaire courant (chinois -> francais)
dict\literals.json         reglages du patcheur de libelles (props evitees, noms propres)
dict\catalog.json          catalogue anglais du dernier passage
dict\etat.json             version et empreinte du dernier passage
dict\ids.json              cree avec a-traduire.tsv
a-relire.md                recapitulatif du dernier passage (regenere a chaque fois)
logs\journal.log           historique, ajout seul
logs\libelles-sans-traduction.txt   libelles restes en chinois (si le patcheur en trouve)
Reasonix-Voice-Input-publish\   module micro
```

## Deux couches, deux mecanismes

| Ce qui est traduit | Comment | Ou |
|---|---|---|
| Le texte qui passe par la fonction de traduction | dictionnaire chinois -> francais injecte dans le bundle | `dict\fr.json`, `tools\patch252.py` |
| Le texte ecrit en dur (props JSX, champs d'objet, filtres, libelles d'etat) | reecriture directe de la source du bundle charge | `tools\patch_literals.py`, `dict\literals.json` |

Le second ne peut pas etre couvert par le premier : ces chaines n'appellent jamais la fonction de traduction. Un dictionnaire complet a 100 % laissait donc encore du chinois a l'ecran — c'est exactement ce qui restait apres la 2.54.

Le patcheur de libelles resout le graphe des modules depuis `index.html` : aucun nom de fichier n'est fige, une mise a jour de Studio ne le casse pas. Une chaine sans traduction n'est jamais devinee : elle est listee dans `logs\libelles-sans-traduction.txt` et laissee telle quelle.

## Ce que le pack applique maintenant (mise a jour du 2026-10-27)

| Element | Detail |
|---|---|
| Francisation du dictionnaire | `dict/fr.json`, 5 concatenations de chaines, langue par defaut |
| Textes natifs de l'application | demarrage, dialogues d'erreur, ancienne version, menu du tray |
| **Menu clic droit en francais** | bloc `fr:` ajoute **et** bloc `en:` francise : le menu est traduit quelle que soit la langue demandee. Marque *facultatif* — si l'`app.asar` est deja francise, le motif est ignore au lieu d'annuler tout le patch |
| **Micro — trois fournisseurs** | module `voice-input.js` (Gemini, Groq `whisper-large-v3-turbo`, ElevenLabs `scribe_v2` ; trois cles conservees separement, bouton « Tester la cle API ») |
| **Micro — dictee Windows** | case a cocher, touche `Win+H` via `winh.ps1`, `SCANCODE + EXTENDEDKEY`, un envoi toutes les 3 s |
| **Pont `shell:send-key`** | ajoute dans `main.js` et `preload.js` de l'`app.asar` : `detached: false` (indispensable — en mode detache PowerShell n'execute pas le script), chemin absolu, journal dans `sendkey.log` |

### Ce qu'il faut savoir

- Le module micro est copie par `Reasonix-Voice-Input-publish/scripts/apply-patch.ps1`, qui ajoute une balise `<script>` dans `index.html`. Rien a faire a la main.
- `winh.ps1` et `dicter.bat` doivent rester dans `J:\Reasonix Studio\data\dev\voix-winh\` : le pont de l'`app.asar` les appelle par ce chemin absolu.
- Le motif du menu est **facultatif** : sur une installation neuve il s'applique ; sur une installation deja francisse a la main, il est ignore et le patch continue.
- Verification faite le 27/10 : **12 motifs appliques**, menu ignore proprement, syntaxe OK sur 9 fichiers, paquet reconstruit et **4/4 marqueurs** valides.

## Mise à jour du 2026-10-29 — ElevenLabs dans le micro

| Element | Detail |
|---|---|
| Troisieme fournisseur | ElevenLabs **Scribe v2**, choisi dans le panneau du micro (clic droit), a cote de Gemini et Groq |
| Mode | batch : `POST https://api.elevenlabs.io/v1/speech-to-text`, `model_id=scribe_v2`, `language_code`, `tag_audio_events=false`, en-tete `xi-api-key` ; le WAV 16 kHz deja produit part tel quel |
| Test de la cle | bouton « Tester la cle API » -> `GET /v1/user`, sans credit consomme et sans audio |
| Coffre | `ELEVENLABS_API_KEY` ajoute a la liste close du pont `reasonix:read-env` ; `verifier-cles.py` lit les trois entrees |
| Migration corrigee | le pont **fusionne** desormais avec le coffre existant au lieu de le remplacer : ajouter une cle n'efface plus Gemini ni Groq |
| Poser la cle | ecrire `ELEVENLABS_API_KEY=...` dans `data\home\.env`, demarrer Studio une fois : la cle passe dans `mic-keys.bin` et la ligne quitte `.env`. Une cle saisie dans le panneau ne vaut que pour la session |

Ce qui n'est **pas** fait : pas de streaming. OpenBot affiche le texte pendant qu'on parle, mais son
micro passe par le processus principal (Electron), seul endroit ou l'en-tete `xi-api-key` peut etre
fixe sur un WebSocket ; cote page il faudrait un jeton a usage unique et un pipeline PCM complet —
chantier separe.
