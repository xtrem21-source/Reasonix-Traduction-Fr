# Problèmes rencontrés et solutions

> Table de référence, mise à jour au fil des versions. Les détails et les preuves sont dans
> [`JOURNAL.md`](JOURNAL.md) et [`INSPECTION-2026-10-18.md`](INSPECTION-2026-10-18.md).

## Hérités de la base AiTron / AionUi

| Problème | Cause | Solution retenue |
|---|---|---|
| Renderer figé après le patch | le micro devenait son propre « bouton d'envoi » ; boucle `MutationObserver` | exclure `#ocVoiceAnchor`/`#ocVoiceRoot` (`isOwnNode`), débouncer 80 ms, `takeRecords()` |
| Micro sur la flèche dans un ancien fil | flèche enveloppée dans un tooltip de 32 px `overflow:hidden` | `anchorTarget()` remonte l'enveloppe et insère après elle dans la vraie barre |
| Micro qui saute à gauche pendant la génération | le bouton d'envoi disparaît, l'heuristique choisissait un bouton d'outils à gauche | exclure le groupe d'outils de gauche et le bouton stop ; Reasonix : ancrer à côté de `session.stop` si `session.send` disparaît |
| Micro mal placé en barre étroite | pas de place à côté | micro flottant 6 px au-dessus, `position:fixed` dans `<body>` (cliquable) |
| Clé Gemini perdue au redémarrage | l'origine change de port ; le preload ne persiste que `rx-*` | clés `rx-ocVoice.*` |
| Envoi auto impossible quand l'agent travaille | le bouton d'envoi est désactivé | AionUi : cliquer le bouton brouillon/file ; Reasonix : retenter ~2 s, sinon copie + erreur explicite |
| Message qui reste dans le composeur | bouton grisé au moment du clic (upload/rendu) | 5 tentatives sur ~2 s avant d'abandonner |
| Pas d'API logs/config dans le preload | le module ne peut pas lire la config de l'app | panneau de clé + `localStorage['rx-ocVoice.log']` + test de clé réel |
| Aucun point de retour avant patch | risque de ne pas pouvoir revenir si l'app casse | `PREPARER-SAUVEGARDE...` (`-BackupOnly`) + `.bak` + `.sha256` + `old/` + `docs/reference` ; `RESTAURER...` (`-Rollback`) ; vérification avant écriture |
| Panneau de réglages hors écran | fenêtre basse, panneau positionné au-dessus du micro | afficher avant de mesurer, `max-height: calc(100vh - 24px)`, `ensurePanelVisible()` |

## Propres à Reasonix Studio 2.40.0

| Problème | Cause | Solution / statut |
|---|---|---|
| Aucun asar exploitable pour l'UI | l'UI est dans `frontend-next\dist` (plain), pas dans `app.asar` | patcher le dossier plain : copie + balise `<script>` |
| Sélecteurs inconnus | UI zh/en, classes générées | `data-action` : `session.send`, `session.stop` ; composeur `data-action-keydown="session.send"` |
| Le composeur est `readOnly` pendant la génération | état React | `isVisible()` accepte `readOnly` pour garder le micro ancré |
| CSP / en-têtes de l'hôte | non confirmés | **à tester** : `fetch` Gemini depuis la console |
| Permission micro | renderer sandboxé | **à tester** : `getUserMedia` au premier clic |
| Envoi pendant génération | `session.send` devient « 插话 » (interjection) | **à tester** : interjection vs file (`queue.*`) |
| Mise à jour de l'app | `frontend-next` remplacé | `REAPPLIQUER-MIC-REASONIX.bat` + `VERIFIER-MIC-REASONIX.bat` + journal |
| Micro qui disparaît dans le chat actif | le script prenait le premier `session.send` de la page ; avec deux chats, il s'ancrait sur l'autre ; pendant une génération, le bouton d'envoi du chat actif est remplacé par `session.stop` | recherche limitée au composeur actif/visible, `focusin` pour suivre le pane, ancre sur `session.stop`, micro maintenue visible pendant la transition (0.1.4) |

## Règle de mise à jour

Quand un nouveau problème est trouvé :

1. l'ajouter ici avec sa cause et la solution ;
2. ajouter une entrée datée dans `JOURNAL.md` ;
3. mettre à jour `README.fr.md` si l'utilisateur doit changer sa façon d'installer ;
4. incrémenter `CHANGELOG.md` et, si nécessaire, `docs/VERSION-REASONIX.md`.
