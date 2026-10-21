# Changelog (français)

Les changements notables de ce package sont documentés ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/).

## [0.1.4] — 2026-10-19

### Corrigé
- **Micro ancrée dans le mauvais chat.** Avec deux chats/panes ouverts, le module prenait le
  premier bouton `session.send` de la page. Quand le chat actif passait en génération, son
  bouton d'envoi était remplacé par `session.stop` : la micro disparaissait du chat actif (ou
  restait dans l'autre). La recherche est désormais limitée au composeur actif/visible, la
  micro s'ancre sur `session.stop` pendant la génération, suit le changement de pane au focus
  et reste visible pendant la transition envoi → stop. Validé sur une réplique DOM à deux
  panes et dans Reasonix Studio 2.40.0.

## [0.1.3] — 2026-10-18

### Ajouté
- **Feuille de route agent FR/EN** : `FICHE-AGENT.fr.md` / `AGENT-PLAYBOOK.md` — 8 phases,
  prompt de départ à copier-coller, checklist 95 %, critères d'acceptation, pièges connus.
- **Cline Desktop** listé comme porté (petits réglages d'ancrage, pas une contrainte).
- **Contrat de fonctionnalités** dans README/tutoriel/fiche agent : mode manuel vs envoi
  automatique, pièces jointes, file d'attente, forçage/secours, menu caché au clic droit.
- **Comparaison Gemini / Windows Win+H** : précision, ponctuation, langues, hors ligne, coût.
  Gemini est le principal avantage qualité ; Windows reste le repli hors ligne / sans clé.

### Modifié
- README, tutoriel et applications supportées mis à jour pour les quatre ports.

## [0.1.2] — 2026-10-18

### Ajouté
- `LICENSE` MIT et avertissement « projet non officiel » dans les deux README.
- Documentation **FR/EN** : inspection, méthode, problèmes/solutions, version, journal,
  changelog, sécurité, publication, applications supportées.
- Méthode **portable en 8 étapes** : le même module s'adapte à d'autres applications Electron
  (AionUi 2.2.2, Open Cowork) ; seuls les sélecteurs, le stockage et le preload changent.

### Modifié
- `docs/INSPECTION-2026-10-18.md` : chemin d'installation masqué
  (`%LOCALAPPDATA%\Programs\Reasonix Studio`).
- `docs/reference/README.md` : l'`index.html` de l'application n'est **pas livré** dans le
  dépôt public ; procédure pour le recréer localement.
- `.gitignore` : ignore la copie locale `docs/reference/ReasonixStudio-*.html`.

### Retiré
- L'`index.html` de Reasonix Studio n'est plus versionné dans l'export public (fichier tiers,
  licence de l'app non documentée).

## [0.1.1] — 2026-10-18

### Ajouté
- **Point de retour garanti** : `PREPARER-SAUVEGARDE-MIC-REASONIX.bat` (`-BackupOnly`) crée
  `index.html.bak` + `index.html.bak.sha256` + une archive datée dans `old/`, **sans patcher**.
- `RESTAURER-MIC-REASONIX.bat` (`-Rollback`) restaure `index.html`, retire `voice-input.js`,
  vérifie l'empreinte, et fonctionne même si Reasonix Studio ne démarre plus.
- Le patcher **vérifie la copie avant toute écriture** et s'arrête en cas de mismatch.
- `-Check` exige désormais une sauvegarde présente et vérifiée.

## [0.1.0] — 2026-10-18

### Ajouté
- Package initial pour **Reasonix Studio 2.40.0**.
- `src/voice-input.reasonix.js` — adaptation d'AiTron Voice Input v5 :
  sélecteurs Reasonix, clés `rx-*`, `reasonixHost.openExternal`, exclusion de `session.stop`,
  composeur `readOnly` accepté, 5 tentatives d'envoi sur ~2 s, ancrage à côté du stop pendant
  une génération.
- `scripts/apply-patch.ps1` — patcher de dossier plain : sauvegarde, injection, hash,
  `-Force`, `-Rollback`, `-Check`. L'application n'est jamais fermée.
- Scripts `.bat`, README FR/EN, inspection, démarche, journal, empreintes, copie de référence.
