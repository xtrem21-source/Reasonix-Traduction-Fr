# Inspection — Reasonix Studio 2.40.0 (2026-10-18)

> **Read-only.** No application file was modified during this inspection. `app.asar` was
> extracted to a temporary folder, then deleted. French version:
> [`INSPECTION-2026-10-18.md`](INSPECTION-2026-10-18.md).

## 1. Application identity

| Item | Value |
|---|---|
| Name | Reasonix Studio |
| Version | **2.40.0** (`reasonix-studio-electron`) |
| Type | Electron + local host (`resources\bin\reasonix-studio-host.exe`) |
| Processes | `Reasonix Studio.exe` (main/renderer) + `reasonix-studio-host.exe` |
| Install | `%LOCALAPPDATA%\Programs\Reasonix Studio` |
| `app.asar` | 520,964 bytes — main + preload only |
| `app.asar.unpacked` | **absent** |
| UI | `resources\frontend-next\dist` — **plain files** (Vite/React) |
| Service | local host on `http://127.0.0.1:<port>/`; `main.js` loads `origin + "/"` |
| Renderer security | `contextIsolation: true`, `sandbox: true`, `nodeIntegration` off |

## 2. Why no asar repack is needed

The frontend is served from `frontend-next\dist` on disk. The patch only:

1. copies `voice-input.js` into that folder;
2. adds `<script src="./voice-input.js"></script>` to `index.html`.

No extract/pack, no `app.asar.unpacked`, no risk to native modules.

## 3. CSP / headers

| Check | Result |
|---|---|
| `index.html` | no `Content-Security-Policy` meta |
| `main.js` | no `onHeadersReceived` / CSP injection |
| `dist/_headers` | only `Cache-Control` for `/assets/*` |
| Host binary | no CSP string found by text search (not conclusive) |

**Runtime-validated**: Gemini `fetch` works from the sandboxed renderer.

## 4. Composer and send button (2.40.0 bundle)

| Element | Selector / detail |
|---|---|
| Composer | `textarea[data-action-keydown="session.send"][role="combobox"]` |
| Send | `button.btn.send[data-action="session.send"]` |
| Stop | `button.btn.stop[data-action="session.stop"]` — excluded |
| During generation | send gets `data-running`; label becomes “插话” (interject) |
| Queue | `queue.send-now`, `queue.cancel`, `queue.edit`, `queue.pause`, `queue.retry` |
| Plugin surfaces | `composer-trailing`, `inRail`, `pluginId`, `surfaceId` |

## 5. Storage and preload

- `window.reasonixHost`: `openExternal`, `saveText`, `saveBytes`, `pickFolder`,
  `pathForFile`, `revealLogs`, etc. **No** `config` or `logs.write`.
- The origin port changes at each launch. The preload persists only `localStorage` keys
  prefixed **`rx-`** (`prefs:load` / `prefs:save`).
- Therefore the module uses `rx-ocVoice.*`, not `ocVoice.*`.
- External link: `reasonixHost.openExternal`.

## 6. Existing voice feature

No `MediaRecorder`, `SpeechRecognition` or `webkitSpeechRecognition` in the frontend. No
conflict.

## 7. Runtime checks

| Point | Result |
|---|---|
| Mic permission (`getUserMedia`) | works |
| Gemini `fetch` / CSP | works |
| `session.send` during generation | interject; queue depends on the app state |
| Attachment + auto-send | 5 retries over ~2 s; validated |
| Anchoring | new chat, old thread, 600×600, resize; validated |
| Update | `frontend-next` is replaced; reapply the patch |

## 8. Decision

Patch the **plain frontend folder**, not the asar:

- low risk; rollback via `index.html.bak`;
- no impact on native modules/host;
- simple reapply after an update;
- the app is **not** closed by the patcher (reload/relaunch).

## 9. Fingerprints (2.40.0)

| File | SHA-256 |
|---|---|
| `index.html` (13,312 B) | `27343223A506E433CF8C15C5A557DD235FB5C745D214661D6CD5AA16F74C9DDE` |
| `assets/index-e5yng55N.js` (720,112 B) | `5C6435D445EDE088006C3857CB2092427B0BE7598298D744DE1D890CA0180553` |

These hashes change with every app update; use them as a diff reference. The app's
`index.html` is **not** redistributed in this repository.
