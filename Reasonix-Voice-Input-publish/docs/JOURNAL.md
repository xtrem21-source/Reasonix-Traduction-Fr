# Journal — Reasonix Voice Input

> **Ajout seul.** Une ligne par événement. On ne réécrit pas une entrée passée ; un fait
> nouveau s'ajoute à la date du jour. Les décisions et les problèmes rencontrés restent ici.

## 2026-10-18

- **Origine** — projet issu d'AiTron Voice Input (base testée sur Open Cowork, puis adaptée à
  AionUi 2.2.2). Le module Reasonix reprend la base v5 d'AionUi (ancrage, observateur,
  anti-auto-ancrage, clé/test, arrêt robuste) et l'adapte aux sélecteurs de Reasonix Studio.
- **Inspection** — Reasonix Studio **2.40.0** : coquille Electron (`app.asar` 520 Ko) + UI
  plain dans `resources\frontend-next\dist`, servie par `reasonix-studio-host.exe` sur
  `http://127.0.0.1:<port>/`. Pas de `app.asar.unpacked`. Aucune voix existante
  (`MediaRecorder`/`SpeechRecognition` absents du frontend).
- **Sélecteurs relevés** — composeur
  `textarea[data-action-keydown="session.send"][role="combobox"]` ; envoi
  `button.btn.send[data-action="session.send"]` ; stop `button.btn.stop[data-action="session.stop"]` ;
  actions de file `queue.send-now|cancel|edit|pause|retry`.
- **Décision** — patcher le **dossier plain** `frontend-next\dist` (pas l'asar) : copie de
  `voice-input.js` + une balise `<script>` dans `index.html`. Sauvegarde `.bak`, archive dans
  `old/`, rollback. Le patcher **ne ferme pas** Reasonix Studio (reload/relaunch).
- **Décision** — clés de stockage en **`rx-ocVoice.*`** : l'origine change de port à chaque
  lancement et le preload Reasonix ne persiste que les clés `rx-*`.
- **Décision** — lien vers AI Studio via `reasonixHost.openExternal` ; pas d'API logs/config
  dans le preload, donc journal dans `localStorage['rx-ocVoice.log']`.
- **Décision** — envoi auto : clic sur `button.btn.send` (session.send), avec **5 tentatives
  sur ~2 s** si le bouton est encore grisé (upload/rendu React) ; pas de clic sur un bouton
  `queue.*` dont la sémantique n'est pas connue. Le comportement « interjection » pendant une
  génération reste à valider.
- **Production** — package 0.1.0 créé : module, patcher PowerShell, 4 scripts `.bat`, README
  FR/EN, inspection, démarche, journal, empreintes, copie de référence de l'`index.html`
  2.40.0.
- **Tests patcher** — sur une **copie** de `index.html` (jamais l'installation réelle) :
  `apply-patch.ps1 -Force` → exit 0, tag présent, `voice-input.js` identique à la source,
  `index.html.bak` identique à l'original ; `-Check` → exit 0 ; `-Rollback` → exit 0,
  `index.html` restauré (hash identique) et `voice-input.js` retiré ; `-Check` après rollback →
  exit 1 ; réapplication `-Force` → exit 0. Le dossier de test et l'archive `old/` de test ont
  été supprimés. L'application **n'a pas été modifiée** (hash `index.html` live = référence).
- **Décision** — pendant une génération, si `session.send` disparaît au profit de
  `session.stop`, le micro s'ancre **à côté du bouton d'arrêt** (même groupe `.go`) ; il ne
  clique jamais stop. Quand l'envoi revient, il se ré-ancre à côté de l'envoi.
- **Décision — retour arrière garanti** : `PREPARER-SAUVEGARDE-MIC-REASONIX.bat` (`-BackupOnly`)
  crée `index.html.bak` + `index.html.bak.sha256` + archive `old/` **sans patcher** ; le patcher
  vérifie la copie **avant toute écriture** et s'arrête si elle ne correspond pas ;
  `RESTAURER-MIC-REASONIX.bat` (`-Rollback`) restaure et vérifie l'empreinte, même si
  l'application ne démarre plus. `-Check` exige désormais une sauvegarde vérifiée.
- **Tests sauvegarde** — sur une copie : `-BackupOnly` crée `.bak` + `.sha256` sans tag ;
  apply → check avec `backup present=True, backup sha256=True` ; rollback → hash restauré ;
  check après rollback → exit 1. Le dossier de test et l'archive de test ont été supprimés.
- **Sauvegarde réelle créée (avant patch)** — `apply-patch.ps1 -BackupOnly` exécuté sur
  l'installation réelle à 03:55:07 : `index.html.bak` + `.sha256` créés dans
  `resources\frontend-next\dist`, archive `old/index.html.20261018-035508`. Vérifié :
  `index.html.bak` = `index.html` (hash `27343223…4C9DDE`), aucun `voice-input.js`, aucune
  balise injectée. **Le patch n'a pas été appliqué** ; l'application est intacte.
- **Publication** — nom de dépôt **`Reasonix-Voice-Input`** ; licence **MIT** ; documentation
  FR/EN (tutoriel, inspection, méthode, problèmes/solutions, version, journal, changelog,
  sécurité, publication, applications supportées) ; l'`index.html` de l'application n'est
  **pas livré** (fichier tiers, licence de l'app non documentée) ; chemin personnel masqué ;
  export propre depuis l'arbre de travail, sans l'HTML de l'app dans l'historique.
- **Tutoriel** — `TUTORIEL.fr.md` / `TUTORIAL.md` : ce que c'est, à quoi ça sert, installation,
  clé Gemini, usage, dépannage, variante Windows/locale, portabilité.
- **Documentation / portage** — ajout de **Cline Desktop** aux applications portées, aux côtés
  de Reasonix Studio, Open Cowork et AionUi. Seuls **quelques petits réglages d'ancrage** dans
  la fenêtre de chat sont nécessaires ; ce n'est pas une contrainte. Ajout d'une comparaison
  **Gemini / Windows Win+H** (précision, ponctuation, langues, hors ligne, coût) : Gemini est
  le principal avantage qualité. Ajout de la **fiche agent FR/EN** (`FICHE-AGENT.fr.md` /
  `AGENT-PLAYBOOK.md`) : 8 phases, prompt de départ, checklist 95 %, critères d'acceptation.
- **À valider dans l'application** — CSP/en-têtes de l'hôte, permission micro, `fetch` Gemini,
  placement réel du micro, envoi pendant génération (interjection/file), pièce jointe +
  envoi auto. Reasonix Studio n'a pas été relancé pendant l'inspection.

## 2026-10-19

- **Symptôme** — dans un chat actif, la micro disparaît dès qu'une question est envoyée ;
  elle reste visible dans l'autre chat (« est-ce qu'on peut parler 2 »).
- **Cause** — le module cherchait le **premier** `button[data-action="session.send"]` de la
  page. Pendant une génération, le bouton d'envoi du chat actif est remplacé par
  `session.stop` ; le script s'ancrait donc sur le bouton d'envoi de l'autre chat, ou se
  masquait si aucun bouton n'était visible.
- **Correctif** — `activeComposer()` + `composerRoot()` : la recherche est limitée au
  composeur visible/focalisé ; `findSubmitButton(root)` et `findStopButton(root)` utilisent
  ce périmètre ; un écouteur `focusin` suit le changement de pane ; si le bouton d'envoi
  disparaît avant que `session.stop` soit rendu, la micro reste visible au lieu d'être
  masquée.
- **Tests** — `node --check` OK ; réplique DOM à deux panes : l'ancien module ancre sur le
  pane A alors que le pane B a le focus, le nouveau ancre sur le bouton stop du pane B ; le
  passage du focus A → B déplace la micro ; un fixture AionUi (avec et sans focus) ancre
  toujours sur `send-button-custom`. Validé dans Reasonix Studio 2.40.0 après relance.
