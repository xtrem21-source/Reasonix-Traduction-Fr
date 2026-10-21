# Fiche agent — porter la saisie vocale sur une application Electron

> **À donner à un agent avec ce dépôt.** La méthode couvre environ **95 %** du travail :
> audit, sauvegarde, packaging, sélecteurs, ancrage, tests, documentation. Les **5 % restants**
> sont les petits réglages propres à l'application (sélecteurs exacts, seuil d'ancrage,
> comportement de la file). Ce n'est pas une contrainte : ce sont des mesures à faire.

## 0. Mission

Ajouter un bouton micro à une application de chat Electron qui n'en a pas :

```
clic micro → enregistrement → Gemini → texte → insertion → envoi auto (optionnel)
```

Le module est `src/voice-input.reasonix.js`. Le patcher est `scripts/apply-patch.ps1`.
La méthode générique est `docs/METHODOLOGY.md` (EN) / `docs/DEMARCHE.md` (FR).

## 1. Règles d'or

1. **Audit read-only d'abord.** Ne modifie rien avant d'avoir identifié l'UI, les sélecteurs
   et le type de packaging.
2. **Sauvegarde vérifiée avant toute écriture.** Plain : `index.html.bak` + `.sha256`.
   Asar : `app.asar.bak` + manifeste `app.asar.unpacked` avant/après.
3. **Ne jamais ancrer le micro sur lui-même** (`isOwnNode`), sinon boucle `MutationObserver`
   et gel du renderer.
4. **Tester sur une copie** avant l'installation réelle.
5. **Ne pas fermer l'application** si un reload suffit ; ne jamais supprimer `app.asar.unpacked`.
6. **Aucune clé API dans le dépôt.** La clé est saisie par l'utilisateur dans le panneau.
7. **Documenter** version, sélecteurs, empreintes, journal, problèmes/solutions.
8. **Toujours un retour arrière** qui fonctionne même si l'application ne démarre plus.

## 2. Feuille de route

### Phase 0 — Audit (read-only)

- [ ] Version de l'application, chemin d'installation, processus.
- [ ] UI : dossier plain ou `app.asar` ? `app.asar.unpacked` présent ?
- [ ] Composeur : `textarea` / `contenteditable`, visible, `readOnly` pendant génération ?
- [ ] Envoi : bouton stable (`data-action`, `data-testid`, classe explicite).
- [ ] Arrêt : bouton affiché pendant le travail (à exclure de l'envoi).
- [ ] Barre d'actions réelle : conteneur flex qui contient envoi/outils.
- [ ] File : actions natives (`queue.*`) ou bouton brouillon.
- [ ] Preload : `openExternal`, config, logs disponibles ?
- [ ] Stockage : préfixe persistant (ex. `rx-` chez Reasonix).
- [ ] Écrire un rapport court avec les sélecteurs et les incertitudes.

**Gate 0** : rapport d'audit + sélecteurs candidats. Aucune écriture.

### Phase 1 — Point de retour

- [ ] Plain : `apply-patch.ps1 -BackupOnly` → `.bak` + `.sha256` + archive `old/`.
- [ ] Asar : copie `app.asar.bak`, manifeste des fichiers `app.asar.unpacked`.
- [ ] Vérifier le hash de la copie avant de continuer.
- [ ] Noter le chemin de retour exact.

**Gate 1** : sauvegarde vérifiée. Sinon, on ne touche à rien.

### Phase 2 — Packaging

**UI plain** :

- [ ] Copier le module dans le dossier de l'UI.
- [ ] Ajouter une balise `<script src="./voice-input.js"></script>` avant `</body>`.
- [ ] Pas d'asar, pas de build.

**UI dans `app.asar`** :

- [ ] Extraire l'asar dans un dossier temporaire.
- [ ] Patcher l'`index.html` et copier le module.
- [ ] Repacker avec `--unpack-dir` pour chaque paquet déballé et `--unpack "**/<rel>"`
      pour les fichiers isolés.
- [ ] Comparer le manifeste `app.asar.unpacked` avant/après : **0 différence**.
- [ ] Refuser une archive qui grossit anormalement.

**Gate 2** : le patch est appliqué sur une **copie** de l'UI, pas encore sur l'installation.

### Phase 3 — Sélecteurs

- [ ] Renseigner `findInput()`, `findSubmitButton()`, `findStopButton()`.
- [ ] Exclure le bouton d'arrêt de la recherche d'envoi.
- [ ] Vérifier les sélecteurs dans le bundle (grep) **et** dans le DOM (DevTools).
- [ ] Tester un nouveau chat, un ancien fil, une fenêtre étroite, un redimensionnement.
- [ ] Vérifier `elementFromPoint` au centre du micro = micro.

**Gate 3** : les 3 sélecteurs sont stables et le micro est cliquable.

### Phase 4 — Adaptation du module

- [ ] Clés de stockage : préfixe persistant de l'app (ex. `rx-ocVoice.*`).
- [ ] Lien externe : `reasonixHost.openExternal` / `electronAPI` / `window.open`.
- [ ] Logs : `console` + buffer `localStorage` (pas d'API logs obligatoire).
- [ ] Clé : panneau + test réel ; pas de config API supposée.
- [ ] `isVisible()` : accepter `readOnly` si l'app verrouille le composeur pendant la génération.
- [ ] Envoi auto : retenter ~2 s si le bouton est grisé (upload/rendu).
- [ ] Pendant génération : ancrer à côté de `session.stop` si `session.send` disparaît,
      sans jamais cliquer stop.

**Gate 4** : le module charge sans erreur JS et le panneau s'ouvre.

### Phase 5 — Ancrage (les petits réglages)

- [ ] Insérer l'ancre **après l'envoi**, dans la vraie barre d'actions.
- [ ] Si l'envoi est dans un petit wrapper `overflow:hidden`, remonter au parent et insérer
      après le wrapper, pas dedans.
- [ ] Si la barre fait moins de ~80 px, placer le micro **au-dessus** de la flèche en
      `position:fixed` dans `<body>` (échappe au `z-index` et à l'`overflow`).
- [ ] Débouncer le ré-ancrage (80 ms) et jeter les mutations faites par le module
      (`takeRecords()`).
- [ ] Écouter `resize`, ré-ancrer immédiatement puis après ~250 ms.
- [ ] `positionOverlay` : pour un élément fixed, `offsetParent` vaut `null` ; utiliser
      `getBoundingClientRect()`.

**Gate 5** : micro à droite en large, au-dessus en étroit, cliquable dans les deux cas.

### Phase 6 — Tests sur copie

- [ ] `node --check` du module.
- [ ] Patcher : apply / check / rollback / reapply, tous à 0.
- [ ] Rollback : hash restauré, module supprimé.
- [ ] Checksum corrompu : rollback refusé, patch intact.

**Gate 6** : la boucle complète est prouvée sur une copie.

### Phase 7 — Installation et validation runtime

- [ ] Installer, recharger (`Ctrl+R`) ou relancer.
- [ ] Aucun `Renderer became unresponsive` / `render-process-gone` après 30 s.
- [ ] Micro visible et cliquable : nouveau chat, ancien fil, étroit, redimensionné.
- [ ] Panneau : clé visible, test Gemini réel, message d'erreur explicite.
- [ ] Dicter court, long, avec pièce jointe.
- [ ] Envoi auto ON / OFF ; mot-clé ; file d'attente quand l'agent travaille.
- [ ] Vérifier `localStorage` / le journal du module.

**Gate 7** : tous les cas ci-dessus passent, ou sont documentés comme limites de l'app.

### Phase 8 — Documentation

- [ ] Version, sélecteurs, empreintes (index.html, bundle).
- [ ] Journal daté (ajout seul) : décisions, tests, échecs.
- [ ] Table problèmes → solutions.
- [ ] Procédure de réapplication après mise à jour.
- [ ] Retour arrière manuel (copier `.bak`, supprimer le module).

**Gate 8** : un autre agent peut reprendre le dépôt sans contexte oral.

## Contrat de fonctionnalités (à tester)

- [ ] **Mode manuel** : envoi auto OFF → texte inséré, **non envoyé** ; l'utilisateur relit et envoie.
- [ ] **Mode automatique** : envoi auto ON → texte inséré **et envoyé** à l'arrêt.
- [ ] **Pièce jointe** : joindre un fichier, dicter → texte + fichier ensemble ; l'envoi auto l'inclut.
- [ ] **File d'attente** : agent occupé → message en file ; plusieurs messages ; vidage natif si
      disponible, sinon forçage / envoi manuel.
- [ ] **Forcer / secours** : bouton grisé → réessai ~2 s, puis erreur explicite + presse-papiers ;
      l'utilisateur peut toujours cliquer envoyer/file.
- [ ] **Clic droit** : menu caché (clé, modèle, langue, insertion auto, envoi auto, mot-clé) ;
      le clic gauche ne fait qu'enregistrer/arrêter.
- [ ] **Gemini vs Win+H** : Gemini est le défaut recommandé pour la précision ; Windows est le
      repli hors ligne / sans clé.

## 3. Checklist « 95 % »

| Domaine | Couvert par la méthode |
|---|---|
| Enregistrement / arrêt / transcription | oui |
| Insertion dans le composeur | oui |
| Envoi auto + mot-clé | oui |
| Pièce jointe | oui (le module n'y touche pas) |
| File d'attente | selon l'app (à vérifier) |
| Ancrage large / étroit / resize | oui (règles + mesures) |
| Sauvegarde / rollback | oui |
| Documentation / journal | oui |
| Sélecteurs exacts de l'app | **à mesurer** (5 %) |
| Comportement runtime (CSP, micro, interjection) | **à tester** (5 %) |

## 4. Les 5 % restants (petits réglages)

1. Les **sélecteurs** du composeur, de l'envoi et de l'arrêt.
2. Le **seuil** de bascule à droite / au-dessus (largeur de la barre).
3. La **remontée** du wrapper tooltip (`overflow:hidden`) vers la vraie barre.
4. Le **préfixe de stockage** et les API du preload.
5. Le **comportement de la file** pendant une génération (interjection vs file).

## 5. Pièges connus

| Piège | Symptôme | Correctif |
|---|---|---|
| Ancre sur elle-même | renderer figé, `MutationObserver` en boucle | `isOwnNode`, debounce, `takeRecords()` |
| Wrapper tooltip 32 px | micro à cheval sur l'envoi (ancien fil) | remonter au parent, insérer après le wrapper |
| Barre étroite | micro hors cadre / incliquable | `position:fixed` au-dessus, dans `<body>` |
| Préfixe de stockage | clé perdue au redémarrage | utiliser le préfixe persistant (ex. `rx-`) |
| Bouton grisé | message reste dans le composeur | retenter ~2 s, puis erreur explicite |
| `session.send` absent | micro saute à gauche | ancrer à côté de `session.stop`, ne pas cliquer |
| `app.asar.unpacked` | modules natifs cassés | `--unpack-dir` / `--unpack`, manifeste identique |
| Mise à jour | micro disparaît | réappliquer après sauvegarde |

## 6. Prompt de départ (à copier)

```text
Tu es l'agent de portage de Reasonix Voice Input.

Dépôt : <chemin du dépôt>
Application cible : <nom, version, chemin d'installation>
Objectif : ajouter le bouton micro (enregistrement → Gemini → insertion → envoi auto).

Lis d'abord, dans cet ordre :
1. FICHE-AGENT.fr.md (ou AGENT-PLAYBOOK.md)
2. docs/METHODOLOGY.md
3. docs/SUPPORTED-APPS.md
4. docs/DEMARCHE.md

Applique la feuille de route Phase 0 → Phase 8. Ne modifie rien avant la Phase 0
(audit read-only) et la Phase 1 (sauvegarde vérifiée). Teste sur une copie avant
l'installation réelle. À chaque phase, rends un rapport court avec les commandes,
les mesures et les preuves. Si un sélecteur ou un comportement n'est pas certain,
dis-le au lieu de deviner. Termine par le journal, les empreintes et le retour arrière.
```

## 7. Critères d'acceptation

- [ ] Aucun gel du renderer après 30 s.
- [ ] Micro cliquable (nouveau chat, ancien fil, étroit, resize).
- [ ] Clé testée réellement ; erreur explicite si absente.
- [ ] Dicter → texte inséré ; envoi auto / mot-clé / file selon l'app.
- [ ] Pièce jointe conservée.
- [ ] Sauvegarde vérifiée et rollback prouvé.
- [ ] Documentation et journal à jour.

## 8. Rollback

| Packaging | Retour |
|---|---|
| Plain | `RESTAURER-MIC-REASONIX.bat` ou `apply-patch.ps1 -Rollback` |
| Asar | restaurer `app.asar.bak`, préserver `app.asar.unpacked` |
| Manuel | copier `.bak` sur `index.html`, supprimer `voice-input.js` |

Le rollback doit fonctionner **même si l'application ne démarre plus**.
