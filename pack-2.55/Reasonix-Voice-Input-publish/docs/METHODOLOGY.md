# Methodology — voice input for Electron chat apps

> The module is app-agnostic. Only the **selectors**, **storage keys**, **preload APIs** and
> **packaging method** change. This is the 8-step method used for Reasonix Studio 2.40.0,
> AionUi 2.2.2 and Open Cowork.

## 1. Locate the controls

Record stable selectors, not text labels (the UI may be in Chinese, English or French):

| Control | What to find |
|---|---|
| Composer | `textarea` or `contenteditable`, visible, editable |
| Send | the button that submits; prefer `data-action` / `data-testid` / explicit class |
| Stop | the button shown while the agent works; exclude it from “send” |
| Action row | the real flex container that holds send/stop/tools |
| Queue | native actions such as `queue.send-now`, `queue.cancel`, `queue.edit` |

## 2. Determine the packaging

| UI location | Patch method |
|---|---|
| Plain folder (e.g. `frontend-next\dist`) | copy the module + one `<script>` tag |
| `app.asar` | extract, patch, repack with `--unpack-dir` / `--unpack` |

For an asar, **preserve `app.asar.unpacked`**: pass `--unpack-dir` for each unpacked package
root and `--unpack "**/<relative-path>"` for loose files. Compare the unpacked file manifest
before/after. Abort if the archive grows unexpectedly.

## 3. Adapt storage

Use a prefix the app's preload persists. Example: Reasonix persists only `rx-*` keys, so the
module uses `rx-ocVoice.*`. Otherwise the key and settings disappear when the origin port
changes at the next launch.

## 4. Adapt preload APIs

| Need | Fallback |
|---|---|
| Open an external URL | `reasonixHost.openExternal` / `window.electronAPI` / `window.open` |
| Logs | `console` + a capped `localStorage` buffer |
| Config | explicit panel; do not assume a config API exists |

## 5. Anchor the mic

- Insert the anchor **after the send button**, inside the real action row.
- If the send button sits inside a small tooltip wrapper (`overflow:hidden`), climb to its
  parent and insert after the wrapper — not inside it.
- Never anchor onto the mic itself (`isOwnNode`), or the `MutationObserver` loops and freezes
  the renderer.
- Debounce re-anchoring (80 ms), discard self-made mutations (`takeRecords()`).
- If the action row is narrower than ~80 px, place the mic **above** the send arrow with
  `position:fixed` moved into `<body>`; it escapes `z-index`/`overflow` and stays clickable.
- During generation, the send button may be replaced by a stop button; anchor next to stop
  without ever clicking it.

## 6. Verify

1. No renderer freeze after 30 s; no `Renderer became unresponsive` in the app log.
2. Mic is at the expected place in a new chat, an old thread, and after resizing.
3. `elementFromPoint` at the mic centre returns the mic.
4. Right-click panel opens; key field visible at 600×600.
5. Gemini test button returns a real API response.
6. Record → stop → text inserted; auto-send sends or queues.
7. Drag a file into the composer; the mic stays anchored while the attachment uploads.

## 7. Keep a rollback

| Packaging | Rollback |
|---|---|
| Plain UI | `index.html.bak` + `.sha256`; restore and delete the module |
| asar | `app.asar.bak`; restore; preserve `app.asar.unpacked` |

Verify the backup **before** writing. The rollback must work even if the app no longer starts.

## 8. Document

Add an inspection note (selectors, version, fingerprints), an append-only journal, a
problem/solution table, and a version-specific reapply procedure. This is what makes the patch
survive an app update.

## Portability table

| App | UI | Patch | State |
|---|---|---|---|
| Reasonix Studio 2.40.0 | `frontend-next\dist` | copy + script tag | **ported and validated** |
| Cline Desktop | Electron | same module + selectors | **ported**; anchoring to adjust |
| Open Cowork | Electron | same module | **ported** (base) |
| AionUi 2.2.2 | `resources\app.asar` | asar repack | **ported and validated** |

The port is **~95% generic**. The last 5% are the exact selectors and anchoring measurements —
small adjustments, not a constraint. For a ready-to-use agent roadmap, see
[`AGENT-PLAYBOOK.md`](AGENT-PLAYBOOK.md) (EN) / [`FICHE-AGENT.fr.md`](FICHE-AGENT.fr.md) (FR).

**Why Gemini?** Its transcription is significantly more accurate and better punctuated than
Windows dictation (**Win+H**), especially for technical terms and long messages. Windows
remains an offline/no-key fallback.

French version: [`DEMARCHE.md`](DEMARCHE.md). Supported apps: [`SUPPORTED-APPS.md`](SUPPORTED-APPS.md).
