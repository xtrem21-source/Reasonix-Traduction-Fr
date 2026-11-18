# Reasonix Studio — correctifs français

Correctifs appliqués à **Reasonix Studio 2.61** (Windows x64) : interface française,
dictée vocale, collage des pièces jointes, et pont OpenCode.

Ce dépôt ne contient **aucun binaire** et **aucune donnée personnelle**. Il contient
les scripts qui appliquent les correctifs sur une archive officielle que vous
téléchargez vous-même.

---

## Ce que corrigent ces scripts

| # | Correctif | Ce que ça change |
|---|---|---|
| 1 | **Francisation** | interface et menus en français (dictionnaire `dict/`) |
| 2 | **Dictée vocale** | bouton micro ; les clés sont lues dans `data/home/.env` en priorité, avec le coffre chiffré en secours |
| 3 | **Collage des pièces jointes** | une capture d'écran collée (Ctrl+V) n'est plus refusée : on fabrique une extension à partir du type MIME |
| 4 | **Pont OpenCode** | `data/dev/opencode-bridge/`, expose les modèles gratuits OpenCode en fournisseur local |

---

## Prérequis

- Windows 10/11 x64
- **Node.js 18 ou plus** (`node --version`)
- L'archive officielle **`ReasonixStudio-windows-amd64.zip`**, version **2.61**

Téléchargez-la depuis les releases du projet amont. Les correctifs sont écrits
pour cette version : sur une autre, les ancres de remplacement ne correspondront
pas, et les scripts s'arrêteront sans rien écrire.

---

## Procédure

```bat
REM 1. Extraire l'archive officielle dans un dossier de travail
REM    (obtenu : Reasonix-Studio-2.61/ avec Reasonix Studio.exe, resources/, ...)

REM 2. Se placer dans le dossier des scripts
cd tools

REM 3. Appliquer les correctifs, dans cet ordre
node patch-lang.mjs   "..\Reasonix-Studio-2.61"
node patch-asar.mjs   "..\Reasonix-Studio-2.61"
node micro.mjs        "..\Reasonix-Studio-2.61\resources\frontend-next\dist" "..\dist"
node pont-micro.mjs   "..\Reasonix-Studio-2.61"
node patch-collage.mjs "..\Reasonix-Studio-2.61"

REM 4. Copier le pont OpenCode
xcopy /E /I /Y "..\opencode-bridge" "..\Reasonix-Studio-2.61\data\dev\opencode-bridge"

REM 5. Recompresser le dossier Reasonix-Studio-2.61 en .zip
```

Chaque script est **idempotent** : relancé sur un dossier déjà corrigé, il ne
réécrit rien et le signale. Une ancre absente ou ambiguë le fait échouer sans
rien modifier.

---

## Ce que ces correctifs ne font pas

- Ils ne modifient **ni** `en.json` **ni** les fichiers de traduction de l'amont :
  la francisation passe par le dictionnaire et les remplacements ciblés.
- Ils ne touchent **jamais** aux données personnelles (`data/home/.env`,
  `data/home/projects`, `data/home/memory`).
- Ils ne contournent aucune protection : si un fichier est en lecture seule ou
  verrouillé, le script échoue et le dit.

---

## Clés API

La dictée vocale utilise une clé Groq (`GROQ_API_KEY`) et, selon la
configuration, Gemini ou ElevenLabs. Deux façons de la fournir :

1. **Dans `data/home/.env`** — recommandé, c'est ce que lit le correctif en premier ;
2. dans le coffre chiffré `data/home/mic-keys.bin`, créé par les versions
   précédentes du pont (conservé en secours pour ne rien perdre).

Le coffre est chiffré par Electron (`safeStorage`, DPAPI sous Windows) : il n'est
lisible que par votre compte Windows, sur cette machine.

---

## Crédits et licence

- Reasonix Studio est développé par **esengine**, distribué sous licence **MIT**.
  Ce dépôt n'est affilié ni à l'auteur ni au projet amont.
- Les correctifs sont fournis tels quels, sans garantie. Testez-les sur une
  installation de test avant de les appliquer à votre installation principale.
