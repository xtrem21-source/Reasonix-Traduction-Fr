# Reasonix Voice Input

[![Release](https://img.shields.io/github/v/release/xtrem21-source/Reasonix-Voice-Input?display_name=tag&sort=semver)](https://github.com/xtrem21-source/Reasonix-Voice-Input/releases)
[![Licence : MIT](https://img.shields.io/github/license/xtrem21-source/Reasonix-Voice-Input)](LICENSE)
[![Plateforme : Windows](https://img.shields.io/badge/platform-Windows-0078D4)](#)
[![Non officiel](https://img.shields.io/badge/status-unofficial-orange)](#)
[![Gemini](https://img.shields.io/badge/transcription-Gemini-4285F4)](https://deepmind.google/technologies/gemini/)
[![Applications](https://img.shields.io/badge/apps-4-2f81f7)](docs/SUPPORTED-APPS.md)

> **Micro de dictée pour applications Electron :** Gemini transcrit, insère et envoie
> (auto ou manuel), avec pièces jointes, file d'attente et menu caché au clic droit. Porté
> sur Reasonix Studio, Cline Desktop, Open Cowork et AionUi.
>
> **Commence ici :** [Tutoriel (FR)](TUTORIEL.fr.md) · [Tutorial (EN)](TUTORIAL.md).

![Saisie vocale dans le composeur](docs/assets/voice-input-mockup.svg)

*Mockup — aucune donnée personnelle.*

| | |
|---|---|
| **Application** | Reasonix Studio **2.40.0** (Electron + hôte local) |
| **Interface patchée** | `resources\frontend-next\dist` — **dossier plain, aucun asar à réemballer** |
| **État** | validé en runtime sur 2.40.0 : micro, clé Gemini, envoi auto, file, ancrage multi-pane ; voir §10 |
> **Projet non officiel.** Non affilié à Reasonix Studio ni à DeepSeek. Le patch modifie une
> copie locale de l'interface ; il est fourni **tel quel**, sans garantie, et peut casser à
> chaque mise à jour. Aucune clé API n'est incluse : tu fournis la tienne.
>
> **Méthode portable.** Le même module et la même démarche en 8 étapes s'appliquent à d'autres
> applications Electron. Reasonix Studio est la cible actuelle ; AionUi 2.2.2 est couverte par
> [`AionUi-Voice-Input`](https://github.com/xtrem21-source/AionUi-Voice-Input) avec la même méthode.
> Voir §10 et [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) (EN) / [`docs/DEMARCHE.md`](docs/DEMARCHE.md) (FR).

---

## Signature — ce qui fait la particularité du programme

> **Le micro vit dans le chat, pas dans une autre application.** Clic gauche : enregistrer.
> **Clic droit : le menu caché des réglages.** Le reste, c'est l'envoi comme tu veux.

| Fonction | Comportement |
|---|---|
| **Clic gauche** | démarre l'enregistrement ; clique à nouveau pour arrêter et transcrire |
| **Clic droit** | ouvre le **menu caché** : clé Gemini, modèle, langue, insertion auto, envoi auto, mot-clé d'envoi |
| **Mode manuel** | le texte est inséré ; tu le relis, tu le modifies, tu envoies toi-même |
| **Envoi automatique** | à l'arrêt, le texte est inséré **et envoyé tout seul** ; une pièce jointe part avec |
| **Pièces jointes** | joins le fichier d'abord, puis dicte ; texte + fichier partent ensemble |
| **File d'attente** | si l'agent travaille, le message est **mis en file** ; plusieurs messages peuvent attendre |
| **Forcer / secours** | le module réessaie ~2 s ; si le bouton reste grisé, message d'erreur explicite + texte copié ; tu peux toujours cliquer envoyer/file |
| **Pas d'application séparée** | aucun serveur, aucun compte, aucune fenêtre en plus ; le module ajoute seulement le micro |

**Le point fort :** la transcription Gemini est nettement meilleure que la dictée Windows
(Win+H), et le couple envoi automatique / file / pièces jointes permet de dicter plusieurs
messages sans toucher la souris — tout en gardant le mode manuel pour relire.

## 0. Retour arrière — la garantie

> **Le patch ne touche jamais l'hôte ni `app.asar`.** Il ne modifie que deux fichiers de
> `frontend-next\dist` : `index.html` et `voice-input.js`. Le retour arrière est donc simple et
> ne dépend pas du démarrage de Reasonix Studio.

| Moment | Ce qui est créé | Où |
|---|---|---|
| **Avant le patch (optionnel)** | `PREPARER-SAUVEGARDE-MIC-REASONIX.bat` → copie vérifiée, sans modifier l'app | `index.html.bak`, `index.html.bak.sha256`, `old/index.html.<date>` |
| **Pendant le patch** | le patcher **vérifie la copie avant toute écriture** ; si elle ne correspond pas, il s'arrête | idem |
| **Retour arrière** | `RESTAURER-MIC-REASONIX.bat` (ou `apply-patch.ps1 -Rollback`) | restaure `index.html`, retire `voice-input.js`, vérifie l'empreinte |
| **L'app ne démarre plus** | ferme-la (gestionnaire de tâches si besoin), lance `RESTAURER-MIC-REASONIX.bat`, relance | la sauvegarde est sur disque, le script n'a pas besoin de l'app |
| **Le dossier du package est perdu** | copie `index.html.bak` sur `index.html`, puis supprime `voice-input.js` | tout est dans `resources\frontend-next\dist` |
| **La sauvegarde elle-même est suspecte** | `index.html.bak.sha256` permet de la contrôler ; une archive datée est dans `old/` ; la copie d'origine n'est **pas livrée** dans le dépôt public (voir `docs/reference/README.md`) | vérification manuelle possible |

Commandes manuelles de secours :

```powershell
$fe = "$env:LOCALAPPDATA\Programs\Reasonix Studio\resources\frontend-next\dist"
Copy-Item "$fe\index.html.bak" "$fe\index.html" -Force
Remove-Item "$fe\voice-input.js" -Force -ErrorAction SilentlyContinue
```

`index.html.bak` et son `.sha256` sont **conservés** après un rollback : on peut recommencer.
Le patcher refuse d'écrire si la copie de sauvegarde ne correspond pas à l'original.

---

## 1. Pourquoi ce dossier

Reasonix Studio est une coquille Electron dont l'interface est servie depuis un dossier de
fichiers statiques. Une mise à jour de l'application remplace ce dossier : le patch disparaît.
Ce dossier garde :

- le **module** adapté aux sélecteurs de Reasonix ;
- le **patcher** qui sauvegarde `index.html`, copie le module et injecte une balise `<script>` ;
- les **scripts de mise à jour et de retour arrière** ;
- la **méthode de ré-inspection** et le **journal** des problèmes/solutions.

Aucun `app.asar` n'est modifié. Aucun repack. Le risque est donc bien plus faible que pour
AionUi.

---

## 2. Installation

1. Ferme ou laisse ouvert Reasonix Studio — **le script ne le ferme pas**.
2. **Recommandé** : double-clique **`PREPARER-SAUVEGARDE-MIC-REASONIX.bat`** — il crée et
   vérifie `index.html.bak` + `.sha256` **sans modifier l'application**.
3. Double-clique **`INSTALLER-MIC-REASONIX.bat`** (le patcher revérifie la sauvegarde avant
   toute écriture).
4. **Recharge la page (`Ctrl+R`) ou relance Reasonix Studio.**
5. Le micro apparaît à côté du bouton d'envoi.
6. **Clic droit** sur le micro → colle ta clé Gemini (`AIza…`) → **Enregistrer** →
   **Tester la clé Gemini**.

En ligne de commande :

```powershell
.\scripts\apply-patch.ps1 -ScriptPath .\src\voice-input.reasonix.js -Force
```

---

## 3. Après une mise à jour de Reasonix Studio

Le dossier `frontend-next\dist` est remplacé → le patch disparaît.

1. Double-clique **`REAPPLIQUER-MIC-REASONIX.bat`**.
2. Recharge / relance Reasonix Studio.
3. Vérifie avec **`VERIFIER-MIC-REASONIX.bat`** (lecture seule) :
   `html tagged = True, voice-input.js present = True, hash matches source = True,
   backup present = True, backup sha256 = True`.
4. Si les sélecteurs ont changé, voir [`docs/DEMARCHE.md`](docs/DEMARCHE.md) et
   [`docs/INSPECTION-2026-10-18.md`](docs/INSPECTION-2026-10-18.md).

---

## 4. Retour arrière

Double-clique **`RESTAURER-MIC-REASONIX.bat`** (ou **`DESINSTALLER-MIC-REASONIX.bat`**, ou la
commande ci-dessous) :

```powershell
.\scripts\apply-patch.ps1 -Rollback
```

`index.html` est restauré depuis `index.html.bak`, son empreinte est vérifiée, et
`voice-input.js` est retiré. La sauvegarde et son `.sha256` sont conservés. Le script
fonctionne **même si Reasonix Studio ne démarre plus**.

---

## 5. Ce que le patch modifie exactement

| Fichier | Modification |
|---|---|
| `...\resources\frontend-next\dist\voice-input.js` | **ajouté** (copie de `src/voice-input.reasonix.js`) |
| `...\resources\frontend-next\dist\index.html` | **une ligne** : `<script src="./voice-input.js"></script>` avant `</body>` |
| `...\resources\frontend-next\dist\index.html.bak` | **sauvegarde** de l'original |

Rien d'autre. Pas d'asar, pas de `app.asar.unpacked`, pas de binaire.

---

## 6. Sélecteurs Reasonix (version 2.40.0)

| Élément | Sélecteur |
|---|---|
| Composeur | `textarea[data-action-keydown="session.send"][role="combobox"]` |
| Bouton d'envoi | `button.btn.send[data-action="session.send"]` |
| Bouton d'arrêt | `button.btn.stop[data-action="session.stop"]` (exclu) |
| File native | actions `queue.send-now`, `queue.cancel`, `queue.edit`, `queue.pause`, `queue.retry` |
| Pendant la génération | le bouton d'envoi reçoit `data-running` et devient « 插话 » (interjection) |

Les sélecteurs sont basés sur `data-action`/classes : **indépendants de la langue** (zh/en).

---

## 7. Stockage de la clé

L'origine de Reasonix change de port à chaque lancement ; son preload ne persiste sur disque
que les clés `localStorage` qui commencent par **`rx-`**. Le module utilise donc :

```
rx-ocVoice.geminiKey
rx-ocVoice.model
rx-ocVoice.lang
rx-ocVoice.autoInsert
rx-ocVoice.sendKeyword
rx-ocVoice.log
```

La clé survit ainsi aux redémarrages (restaurée par `prefs:load`).

---

## 8. Limites et points à valider

| Point | Statut |
|---|---|
| **CSP / en-têtes de l'hôte** | pas de CSP dans `index.html` ; les en-têtes de l'hôte local ne sont pas confirmés → tester le `fetch` Gemini après installation |
| **Permission micro** | `getUserMedia` dans le renderer sandboxé : à tester au premier clic |
| **Envoi pendant une génération** | le bouton `session.send` devient « interjection » ; comportement file/interjection à valider |
| **Pièce jointe + envoi auto** | la pièce jointe reste dans le composeur ; l'envoi auto clique `session.send` après ~2 s de tentatives |
| **Mises à jour** | `frontend-next` est remplacé ; relancer `REAPPLIQUER-MIC-REASONIX.bat` |
| **Clé Gemini** | aucune détection automatique de la clé de Reasonix : saisie dans le panneau |

---

## 9. Traçabilité

| Fichier | Rôle |
|---|---|
| [`docs/INSPECTION-2026-10-18.md`](docs/INSPECTION-2026-10-18.md) | ce qui a été inspecté, sélecteurs, risques — [English](docs/INSPECTION-2026-10-18.en.md) |
| [`docs/DEMARCHE.md`](docs/DEMARCHE.md) | méthode de ré-inspection et de réapplication après update — [English](docs/METHODOLOGY.md) |
| [`docs/JOURNAL.md`](docs/JOURNAL.md) | journal **en ajout seul** : dates, constats, décisions — [English mirror](docs/JOURNAL.en.md) |
| [`docs/VERSION-REASONIX.md`](docs/VERSION-REASONIX.md) | empreintes de la version 2.40.0 (index.html, bundle) — [English](docs/VERSION-REASONIX.en.md) |
| [`docs/PROBLEMS-SOLUTIONS.md`](docs/PROBLEMS-SOLUTIONS.md) | problèmes → solutions — [English](docs/PROBLEMS-SOLUTIONS.en.md) |
| [`CHANGELOG.md`](CHANGELOG.md) | versions du package — [Français](CHANGELOG.fr.md) |
| [`SECURITY.md`](SECURITY.md) | clé Gemini, données, signalement — FR/EN |
| [`docs/PUBLICATION.md`](docs/PUBLICATION.md) | checklist de publication — FR/EN |
| `docs/reference/` | comment recréer localement l'`index.html` d'origine (non livré) |

**Méthode** : après chaque mise à jour de Reasonix, comparer l'`index.html` local avec le
nouveau, revérifier les sélecteurs, puis réappliquer. Le journal garde la trace de ce qui a
été essayé et pourquoi.

---

## 10. Portabilité — même méthode, autres applications

Le module est **agnostique de l'application** : seuls les sélecteurs, les clés de stockage et
les API du preload changent. La démarche en 8 étapes est la même.

| Application | Interface | Type de patch | État |
|---|---|---|---|
| [Reasonix Studio 2.40.0](https://github.com/esengine/DeepSeek-Reasonix) | `frontend-next\dist` (plain) | copie + une balise `<script>` | **porté et validé** |
| [Cline Desktop](https://github.com/cline/cline) | application Electron | même module + sélecteurs | **porté** ; ancrage à ajuster |
| [Open Cowork](https://github.com/open-cowork/open-cowork) | application Electron | même module + sélecteurs | **porté** (base) |
| [AionUi 2.2.2](https://github.com/iOfficeAI/AionUi) | `resources\app.asar` | repack asar avec `--unpack` | **porté et validé** |

Les 8 étapes génériques sont dans [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) (EN) et
[`docs/DEMARCHE.md`](docs/DEMARCHE.md) (FR). En résumé :

1. Repérer le composeur, l'envoi et l'arrêt ; noter des sélecteurs stables.
2. Déterminer si l'interface est en fichiers plain ou dans un asar.
3. Plain : copier le module + une balise ; asar : extraire, préserver
   `app.asar.unpacked`, repacker avec `--unpack-dir` / `--unpack`, vérifier le manifeste.
4. Adapter les clés de stockage à la persistance de l'app (ex. `rx-` chez Reasonix).
5. Adapter les API du preload (liens externes, config/logs disponibles ou non).
6. Ancrer le micro dans la vraie barre d'actions ; jamais sur lui-même ; au-dessus si étroit.
7. Vérifier : pas de gel du renderer, micro cliquable, test de clé, enregistrement, insertion,
   envoi auto, file d'attente.
8. Garder un retour arrière vérifié (`.bak` + checksum, ou `app.asar.bak` + manifeste unpacked).

**Le gros avantage :** la transcription Gemini est nettement plus précise et mieux ponctuée
que la dictée Windows (**Win+H**), surtout pour les termes techniques et les messages longs.
C'est l'atout principal du module ; Windows reste un repli hors ligne / sans clé.

**Pour un agent :** [`FICHE-AGENT.fr.md`](FICHE-AGENT.fr.md) (FR) /
[`AGENT-PLAYBOOK.md`](AGENT-PLAYBOOK.md) (EN) est une feuille de route à copier-coller. Elle
couvre ~95 % du portage ; les 5 % restants sont les sélecteurs exacts et les mesures d'ancrage
— de petits réglages, pas une contrainte.

## Tags

`voice-input` · `speech-to-text` · `dictation` · `gemini` · `electron` · `reasonix-studio` ·
`cline-desktop` · `open-cowork` · `aionui` · `productivity` · `accessibility` · `windows`

## 11. Licence

MIT — voir [`LICENSE`](LICENSE). L'application Reasonix Studio n'est pas distribuée ici ; son
nom et ses marques appartiennent à leurs propriétaires. Ce dépôt est un projet **non officiel**.
