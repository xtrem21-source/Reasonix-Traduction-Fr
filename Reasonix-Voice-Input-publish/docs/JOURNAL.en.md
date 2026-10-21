# Journal — English mirror

> The French [`JOURNAL.md`](JOURNAL.md) is **authoritative and append-only**. This file is the
> English mirror for publication; it is updated with the same dated entries.

## 2026-10-18

- **Origin** — project derived from AiTron Voice Input (Open Cowork base, then AionUi 2.2.2).
  This module keeps the AionUi v5 base (anchoring, observer, self-anchor guard, key/test,
  robust stop) and adapts it to Reasonix Studio.
- **Inspection** — Reasonix Studio **2.40.0**: Electron shell (`app.asar` 520 KB) + plain UI
  in `resources\frontend-next\dist`, served by `reasonix-studio-host.exe` on
  `http://127.0.0.1:<port>/`. No `app.asar.unpacked`. No existing voice feature.
- **Selectors** — composer
  `textarea[data-action-keydown="session.send"][role="combobox"]`; send
  `button.btn.send[data-action="session.send"]`; stop `button.btn.stop[data-action="session.stop"]`;
  queue actions `queue.send-now|cancel|edit|pause|retry`.
- **Decision** — patch the **plain folder** `frontend-next\dist` (no asar): copy
  `voice-input.js` + one `<script>` tag in `index.html`. Backup `.bak`, archive in `old/`,
  rollback. The patcher **does not close** Reasonix Studio (reload/relaunch).
- **Decision** — storage keys **`rx-ocVoice.*`**: the origin port changes at each launch and
  the preload persists only `rx-*` keys.
- **Decision** — external link via `reasonixHost.openExternal`; no logs/config API in the
  preload, so the log lives in `localStorage['rx-ocVoice.log']`.
- **Decision** — auto-send: click `button.btn.send` (`session.send`), 5 attempts over ~2 s if
  the button is still disabled (upload/React render). During generation, anchor next to
  `session.stop` without clicking it; `session.send` may interject.
- **Production** — package 0.1.0: module, PowerShell patcher, 4 batch scripts, README FR/EN,
  inspection, method, journal, fingerprints, local reference copy.
- **Backup** — 0.1.1: `PREPARER-SAUVEGARDE...` (`-BackupOnly`) creates `.bak` + `.sha256` +
  `old/` archive without patching; the patcher verifies the copy before any write;
  `RESTAURER...` (`-Rollback`) verifies the checksum and restored hash, works even if the app
  no longer starts; `-Check` requires a verified backup.
- **Real backup created** — `-BackupOnly` on the live install at 03:55:07: `.bak` + `.sha256`
  in `frontend-next\dist`, archive `old/index.html.20261018-035508`; hash
  `27343223…4C9DDE`; no `voice-input.js`, no tag. **Patch not applied.**
- **Tests** — on a copy: apply/check/rollback 0; corrupted checksum refused (exit 1, patch
  intact); corrected checksum restores the hash and removes `voice-input.js`.
- **Publication prep** — repo name `Reasonix-Voice-Input`; MIT license; FR/EN docs; generic
  8-step methodology for other Electron apps; app `index.html` **not** redistributed; personal
  path sanitized; clean export from the working tree (no app HTML in history).
- **Documentation / porting** — added **Cline Desktop** to the ported apps, alongside Reasonix
  Studio, Open Cowork and AionUi. Only **a few small anchoring adjustments** in the chat window
  are needed; this is not a constraint. Added a **Gemini / Windows Win+H** comparison
  (accuracy, punctuation, languages, offline, cost): Gemini is the main quality advantage.
  Added the **agent playbook FR/EN** (`FICHE-AGENT.fr.md` / `AGENT-PLAYBOOK.md`): 8 phases,
  starter prompt, 95% checklist, acceptance criteria.
- **To validate in the app** — runtime CSP, mic permission, Gemini fetch, send during
  generation, attachment + auto-send. Reasonix Studio was not closed during inspection.

## 2026-10-19

- **Symptom** — in the active chat, the mic disappears as soon as a question is sent; it
  stays visible in the other chat ("est-ce qu'on peut parler 2").
- **Cause** — the module looked up the **first** `button[data-action="session.send"]` on the
  page. During generation, the active chat's send button is replaced by `session.stop`; the
  script therefore anchored to the other chat's send button, or hid itself when no button was
  visible.
- **Fix** — `activeComposer()` + `composerRoot()`: the lookup is scoped to the visible/focused
  composer; `findSubmitButton(root)` and `findStopButton(root)` use that scope; a `focusin`
  listener follows pane changes; if the send button disappears before `session.stop` is
  rendered, the mic stays visible instead of being hidden.
- **Tests** — `node --check` OK; two-pane DOM fixture: the old module anchors to pane A while
  pane B is focused, the new one anchors to pane B's stop button; moving focus A → B moves the
  mic; an AionUi fixture (with and without focus) still anchors to `send-button-custom`.
  Validated in Reasonix Studio 2.40.0 after relaunch.
