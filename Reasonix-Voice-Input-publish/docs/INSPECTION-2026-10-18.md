# Inspection — Reasonix Studio 2.40.0 (2026-10-18)

> **Lecture seule.** Aucun fichier de l'application n'a été modifié pendant cette inspection.
> `app.asar` a été extrait dans un dossier temporaire, puis supprimé.
> **English:** [`INSPECTION-2026-10-18.en.md`](INSPECTION-2026-10-18.en.md).

## 1. Identité de l'application

| Élément | Valeur |
|---|---|
| Nom | Reasonix Studio |
| Version | **2.40.0** (`reasonix-studio-electron`) |
| Type | Electron + hôte local (`resources\bin\reasonix-studio-host.exe`) |
| Processus | `Reasonix Studio.exe` (renderer/main) + `reasonix-studio-host.exe` |
| Installation | `%LOCALAPPDATA%\Programs\Reasonix Studio` |
| `app.asar` | 520 964 octets — main + preload uniquement |
| `app.asar.unpacked` | **absent** |
| Interface | `resources\frontend-next\dist` — **fichiers plain** (Vite/React) |
| Service | hôte local sur `http://127.0.0.1:<port>/` ; `main.js` fait `loadURL(origin + "/")` |
| Sécurité renderer | `contextIsolation: true`, `sandbox: true`, `nodeIntegration` désactivé |

## 2. Pourquoi aucun asar n'est nécessaire

`layout.js` résout le frontend sur `frontend-next\dist` ; `main.js` charge cette origine via
l'hôte local. Le dossier est servi depuis le disque. Le patch peut donc :

1. copier `voice-input.js` dans `frontend-next\dist` ;
2. ajouter une balise `<script src="./voice-input.js"></script>` dans `index.html`.

Aucun `extract`/`pack` d'asar, aucun `app.asar.unpacked`, aucun risque de casser les modules
natifs.

## 3. En-têtes / CSP

| Contrôle | Résultat |
|---|---|
| `index.html` | pas de balise `Content-Security-Policy` |
| `main.js` | pas d'injection `onHeadersReceived` / CSP |
| `dist/_headers` | uniquement `Cache-Control` pour `/assets/*` |
| Hôte binaire | aucune chaîne CSP trouvée par recherche textuelle (non concluant) |

**À valider à l'exécution** : le `fetch` vers `generativelanguage.googleapis.com` depuis le
renderer sandboxé.

## 4. Composeur et bouton d'envoi (bundle 2.40.0)

| Élément | Sélecteur / détail |
|---|---|
| Composeur | `textarea[data-action-keydown="session.send"][role="combobox"]` ; `aria-label` = « 任务输入 » (zh) |
| Bouton d'envoi | `button.btn.send[data-action="session.send"]` ; contient un SVG et un libellé « 发送 » / « 插话 » |
| Stop | `button.btn.stop[data-action="session.stop"]` — à exclure |
| Pendant génération | le bouton d'envoi reçoit `data-running`, le texte devient « 插话 » (interjection) |
| File native | `queue.send-now`, `queue.cancel`, `queue.edit`, `queue.pause`, `queue.retry` |
| Surfaces plugin | `composer-trailing`, `inRail`, `pluginId`, `surfaceId` (piste native future) |

Le texte du bouton est en chinois/anglais ; les sélecteurs `data-action` sont stables et
indépendants de la langue.

## 5. Stockage et preload

- Le preload expose `window.reasonixHost` : `openExternal`, `saveText`, `saveBytes`,
  `pickFolder`, `pathForFile`, `revealLogs`, etc. **Pas** de `config` ni de `logs.write`.
- L'origine change de port à chaque lancement. Le preload restaure sur disque **uniquement les
  clés `localStorage` préfixées `rx-`** (`prefs:load` / `prefs:save`).
- Conséquence : le module utilise `rx-ocVoice.*` (clé Gemini incluse), pas `ocVoice.*`.
- Le lien vers Google AI Studio utilise `reasonixHost.openExternal`.

## 6. Voix existante

Aucune trace de `MediaRecorder`, `SpeechRecognition` ou `webkitSpeechRecognition` dans le
frontend. Le module n'entre pas en conflit avec une fonction existante.

## 7. Points à valider à l'exécution

| Point | Pourquoi |
|---|---|
| Permission micro (`getUserMedia`) | renderer sandboxé ; première utilisation |
| `fetch` Gemini | CSP de l'hôte non confirmée |
| `session.send` pendant génération | « 插话 » = interjection probable, pas nécessairement file |
| Pièce jointe + envoi auto | le bouton d'envoi peut être grisé pendant l'upload ; le module retente 2 s |
| Ancrage | insérer après `button[data-action="session.send"]` ; le groupe `.go` contient aussi le stop |
| Mise à jour | `frontend-next` est remplacé ; réappliquer le patch |

## 8. Décision

**Patching du dossier `frontend-next\dist`**, pas de l'asar :

- risque faible, rollback par `index.html.bak` ;
- aucun impact sur les modules natifs / l'hôte ;
- réapplication simple après mise à jour ;
- l'application n'est **pas** fermée par le patcher (elle sert la page ; un reload suffit).

## 9. Empreintes de la version inspectée

| Fichier | SHA-256 |
|---|---|
| `index.html` (13 312 o) | `27343223A506E433CF8C15C5A557DD235FB5C745D214661D6CD5AA16F74C9DDE` |
| `assets/index-e5yng55N.js` (720 112 o) | `5C6435D445EDE088006C3857CB2092427B0BE7598298D744DE1D890CA0180553` |

Ces empreintes changent à chaque mise à jour ; elles servent de repère pour le diff.
