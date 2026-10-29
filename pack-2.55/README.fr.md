# Reasonix-Traduction-Vault

[![Version](https://img.shields.io/badge/reasonix%20studio-2.55.0-2f81f7)](#versions-couvertes)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%20amd64-0078D4)](#prerequis)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](LICENSE)
[![Statut](https://img.shields.io/badge/statut-non%20officiel-orange)](#non-affiliation)

**Francisation, micro et coffre à clés chiffré pour Reasonix Studio — en un double-clic.**

Ce pack traduit en français l'interface de **Reasonix Studio** (l'application de bureau du projet
[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)), ajoute un bouton de dictée
avec trois fournisseurs de transcription, et sort les clés API d'un fichier en clair pour les
confier à un coffre chiffré par Windows.

> **Projet non officiel.** Non affilié au projet DeepSeek-Reasonix ni à ses mainteneurs, sans
> approbation ni parrainage de leur part. L'installeur remplace `resources\frontend-next\` et
> `app.asar` ; ce pack répare les deux après chaque mise à jour. Voir [Non-affiliation](#non-affiliation).

---

## Sommaire

- [Ce que fait le pack](#ce-que-fait-le-pack)
- [Pourquoi un coffre](#pourquoi-un-coffre)
- [Comment ça marche](#comment-ça-marche)
- [Prérequis](#prerequis)
- [Installation et usage](#installation-et-usage)
- [Le micro](#le-micro)
- [Sécurité des clés](#securite-des-cles)
- [Entretien : le patch suit l'application](#entretien-le-patch-suit-lapplication)
- [Limites connues](#limites-connues)
- [Contenu du dépôt](#contenu-du-depot)
- [Non-affiliation](#non-affiliation)
- [Licence](#licence)

---

## Ce que fait le pack

| Couche | Ce que le pack fait |
|---|---|
| **Interface** | Injecte un dictionnaire français de 5 243 entrées dans le bundle réellement chargé, et réécrit les textes écrits en dur dans les bundles (libellés, états, infobulles, messages) |
| **Chaînes natives** | Repatche `app.asar` : écran de démarrage, dialogues, zone de notification, **menu contextuel**, et le pont qui lit le coffre |
| **Micro** | Installe `voice-input.js` et sa balise `<script>` : dictée avec **Gemini**, **Groq** ou **ElevenLabs**, un seul champ de clé visible à la fois |
| **Skills** | Traduit la `description` de chaque skill installé dans `<home>\skills` (frontmatter seulement, contenu intact) |
| **Clés** | Déplace `GEMINI_API_KEY`, `GROQ_API_KEY` et `ELEVENLABS_API_KEY` de `.env` vers `mic-keys.bin`, chiffré par Windows (DPAPI) |
| **Vérification** | Contrôle que toutes les chaînes du build rendent du français, puis relit l'empreinte de chaque fichier installé |
| **Retour arrière** | `restaurer.bat` remet chaque fichier dans son état d'avant, depuis une sauvegarde datée |

Mesuré sur Reasonix Studio 2.55.0 : **5 205 / 5 205 chaînes couvertes, 0 erreur**, aucun libellé
codé en dur laissé sans traduction.

## Pourquoi un coffre

Le micro a besoin de clés API. La façon évidente de les ranger est un fichier — et un fichier est
lu par quiconque accède au dossier, copié par n'importe quel client de synchronisation, et laissé
dans les sauvegardes.

Ce pack fait ce que l'application fait pour ses propres secrets : il demande à Windows de les
chiffrer, puis retire les lignes en clair de `.env`. Ce qu'il **ne** fait **pas**, c'est rendre
les clés inoffensives — voir [Sécurité des clés](#securite-des-cles) pour la limite exacte.

## Comment ça marche

```
mettre-a-jour.bat
   │
   ├── 1. ferme Reasonix Studio, retient les fichiers qu'il va toucher
   ├── 2. dictionnaire   → dict/fr.json injecté dans le bundle i18n vivant
   ├── 3. libellés durs  → tools/patch_literals.py réécrit les bundles chargés
   ├── 4. micro          → Reasonix-Voice-Input-publish/scripts/apply-patch.ps1
   ├── 5. chaînes natives→ tools/patch_asar252.py (menu, démarrage, tray, pont du coffre)
   ├── 6. skills         → tools/patch_skills.py (descriptions du frontmatter)
   └── 7. vérification   → tools/verify.mjs balaie toutes les chaînes du build
```

Chaque étape est idempotente : la rejouer ne réécrit rien. Chaque étape pose une sauvegarde
datée avant de toucher un fichier (`.avant-*`, `backups/<horodatage>/`, `index.html.bak`).

## Prérequis

- **Windows 10/11, amd64.**
- **Reasonix Studio 2.55.0**, installé en dossier simple (portable ou `%LOCALAPPDATA%\Programs`).
- **Python 3** — le moteur est un script Python. Le lanceur cherche `py -3`, `%LOCALAPPDATA%\Programs\Python\Python313`, `C:\Python313`, ou ce que dit `config.bat`.
- **Node.js** — facultatif ; le binaire de Reasonix Studio peut servir de Node (`ELECTRON_RUN_AS_NODE=1`).

## Installation et usage

1. Écrivez vos clés dans `J:\Reasonix Studio\data\home\.env` :

   ```ini
   GEMINI_API_KEY=AIza...
   GROQ_API_KEY=gsk_...
   ELEVENLABS_API_KEY=sk_...
   ```

   Une clé suffit pour dicter ; trois clés font trois chances.

2. Fermez complètement Reasonix Studio (icône de la zone de notification → Quitter).

3. Double-cliquez sur **`mettre-a-jour.bat`**. Il ferme l'application si besoin, extrait le
   catalogue, le compare au dictionnaire, applique, puis vérifie.

4. Rouvrez l'application, puis double-cliquez sur **`verifier-cles.bat`** : il doit annoncer
   **trois entrées** et un `.env` propre.

Après le premier démarrage, les clés vivent dans `data\home\mic-keys.bin` et les lignes
disparaissent de `.env`. Pour changer une clé plus tard : réécrivez-la dans `.env`, redémarrez
une fois.

## Le micro

Clic droit sur le bouton micro du composeur pour ouvrir le panneau de réglages.

| Fournisseur | Modèle | Clé | Transport | Quand le choisir |
|---|---|---|---|---|
| **Gemini** | `gemini-3.5-flash-lite` (modifiable) | `AIza…` | `generateContent` | par défaut ; reformule et ponctue bien |
| **Groq** | `whisper-large-v3-turbo` | `gsk_…` | `POST /openai/v1/audio/transcriptions` | rapide, quota gratuit généreux |
| **ElevenLabs** | `scribe_v2` (imposé) | `sk_…` | `POST /v1/speech-to-text` (batch) | le meilleur sur une parole française bruitée |

Le bouton **Tester la clé API** ne teste que le fournisseur sélectionné : `GET /v1/user` pour
ElevenLabs (aucun crédit consommé, aucun audio), une génération d'un mot pour Gemini, la liste
des modèles pour Groq.

La dictée enregistre, convertit en WAV 16 kHz mono, envoie, puis insère le texte dans le
composeur — ou envoie le message directement si *envoi automatique* est coché.

## Sécurité des clés

**Ce qui est fait.** Les trois clés sont chiffrées par le `safeStorage` d'Electron, qui est DPAPI
sous Windows : le chiffré est lié à votre compte Windows et à cette machine, et rangé dans
`data\home\mic-keys.bin`. Les lignes en clair sont retirées de `.env`, et la page ne reçoit
jamais une clé — le déchiffrement a lieu dans le processus principal, derrière une liste blanche
de trois noms.

**Ce que ça apporte.** Une copie du dossier, un client de synchronisation, une sauvegarde, une
image de disque volée ne contiennent plus de clé utilisable. Avant ce pack, lire `.env` dans le
Bloc-notes suffisait.

**Ce que ça n'apporte pas — à lire.** Le coffre n'est **pas** du chiffrement de bout en bout et
**pas** un gestionnaire de mots de passe :

| Limite | Pourquoi |
|---|---|
| Même compte Windows, même machine | Tout processus lancé sous votre compte peut demander à DPAPI de déchiffrer le fichier, exactement comme le fait l'application |
| Mémoire | Tant que l'application tourne, les clés sont en clair dans la mémoire du processus principal |
| Aucun mot de passe maître | Il n'y a pas de second facteur : le compte **est** le secret |
| Itinérance | Copiez `mic-keys.bin` sur une autre machine ou un autre compte : il ne se déchiffrera pas — les clés sont perdues, pas compromises. Réécrivez-les dans `.env` |
| Saisie dans le panneau | Une clé tapée dans le panneau reste en mémoire pour la session ; elle n'est jamais écrite sur disque |
| Amont | Le pont vit dans `app.asar`. Une mise à jour de Reasonix Studio le supprime jusqu'à ce que le pack soit réappliqué — pendant cette fenêtre, le micro ne peut pas lire le coffre |

En résumé : le pack ferme le trou « fichier en clair sur le disque », qui était le vrai. Il ne
rend pas une session volée, déverrouillée et connectée inoffensive.

## Entretien : le patch suit l'application

Mises à jour de Reasonix Studio remplacent `resources\frontend-next\` et `app.asar`. C'est
attendu : après chaque mise à jour, l'interface repasse en anglais, le micro disparaît et les
clés deviennent illisibles jusqu'à ce que le pack soit réappliqué.

La méthode ne contient aucun numéro de version : elle **lit** la version dans
`Reasonix Studio.exe` (`FileVersion`), extrait le catalogue des bundles réellement chargés, et le
compare au dictionnaire. Quand la version amont ajoute des chaînes, le moteur refuse d'appliquer
quoi que ce soit, écrit `a-traduire.tsv` et attend. Remplissez la colonne `francais`, relancez :
rien d'autre à apprendre.

C'est aussi pourquoi ce dépôt continuera d'évoluer : chaque version amont peut renommer des
bundles, ajouter des chaînes ou déplacer une ancre de menu. Le pack est fait pour être relancé,
pas figé.

## Limites connues

| Limite | Détail |
|---|---|
| Skills intégrés | Les neuf skills intégrés (*explore*, *locate*, *review*…) gardent leur description anglaise : elle est compilée dans `reasonix-studio-host.exe`, pas dans un fichier que ce pack peut réécrire |
| Pas de dictée en flux | ElevenLabs est utilisé en mode batch : le texte arrive après l'arrêt, pas pendant que vous parlez |
| Windows seulement | Le coffre repose sur DPAPI via Electron ; le reste du pipeline est portable en principe, mais non testé ailleurs |
| Fragilité amont | Une mise à jour peut casser une ancre (`main.js`, `preload.js`, menu). Le patcheur refuse d'installer un fichier cassé — il s'arrête et dit quelle ancre manque |
| Quota | Les paliers gratuits de Gemini, Groq et ElevenLabs ont des limites ; le pack ne les contourne pas |

## Contenu du dépôt

```
mettre-a-jour.bat              le double-clic : applique tout
restaurer.bat                  revient à l'état d'avant, depuis une sauvegarde datée
verifier-cles.bat              état du coffre, n'affiche jamais une clé
config.bat                     chemins et langue de repli
normaliser-crlf.ps1            remet les .bat en CRLF (un .bat en LF casse `goto` sans message)

dict/fr.json                   5 243 traductions (source chinoise → français)
dict/literals.json             règles du patcheur de libellés écrits en dur
dict/skills-fr.json            descriptions françaises des skills installés

tools/maj.py                   le moteur : extraire, comparer, appliquer, vérifier
tools/patch252.py              dictionnaire + langue par défaut + écran de démarrage
tools/patch_literals.py        textes écrits directement dans les bundles
tools/patch_asar252.py         chaînes natives, menu contextuel, pont du coffre
tools/patch_skills.py          descriptions des skills (frontmatter)
tools/asar_patches.json        ancres et remplacements exacts pour app.asar
tools/verify.mjs               balayage de toutes les chaînes du build
tools/selftest.py              auto-test sur une copie de l'application
tools/verifier-cles.py         état du coffre

Reasonix-Voice-Input-publish/  le module micro et son installeur
```

## Non-affiliation

Reasonix Studio est développé par le projet DeepSeek-Reasonix. Ce dépôt est un travail
indépendant et non officiel : il ne contient aucun code de l'application, seulement des correctifs
appliqués à une copie locale que l'utilisateur possède déjà. Les noms et marques appartiennent à
leurs titulaires.

## Licence

MIT — voir [LICENSE](LICENSE). L'application corrigée conserve sa propre licence.
