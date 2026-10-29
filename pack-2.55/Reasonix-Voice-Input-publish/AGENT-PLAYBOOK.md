# Agent playbook — port voice input to an Electron app

> **Give this file to an agent together with the repository.** The method covers about **95%**
> of the work: audit, backup, packaging, selectors, anchoring, tests, documentation. The
> remaining **5%** are the app-specific adjustments (exact selectors, anchoring threshold,
> queue behaviour). They are not a constraint: they are measurements to take.

## 0. Mission

Add a mic button to an Electron chat app that has none:

```
mic click → record → Gemini → text → insert → auto-send (optional)
```

The module is `src/voice-input.reasonix.js`. The patcher is `scripts/apply-patch.ps1`.
The generic method is `docs/METHODOLOGY.md` (EN) / `docs/DEMARCHE.md` (FR).

## 1. Golden rules

1. **Read-only audit first.** Do not modify anything before identifying the UI, selectors and
   packaging type.
2. **Verified backup before any write.** Plain: `index.html.bak` + `.sha256`. Asar:
   `app.asar.bak` + `app.asar.unpacked` manifest before/after.
3. **Never anchor the mic onto itself** (`isOwnNode`), or the `MutationObserver` loops and the
   renderer freezes.
4. **Test on a copy** before the real install.
5. **Do not close the app** if a reload is enough; never delete `app.asar.unpacked`.
6. **No API key in the repository.** The user enters it in the panel.
7. **Document** version, selectors, fingerprints, journal, problems/solutions.
8. **Always keep a rollback** that works even if the app no longer starts.

## 2. Roadmap

### Phase 0 — Audit (read-only)

- [ ] App version, install path, processes.
- [ ] UI: plain folder or `app.asar`? Is `app.asar.unpacked` present?
- [ ] Composer: `textarea` / `contenteditable`, visible, `readOnly` during generation?
- [ ] Send: stable button (`data-action`, `data-testid`, explicit class).
- [ ] Stop: button shown while working (exclude from send).
- [ ] Real action row: flex container holding send/tools.
- [ ] Queue: native actions (`queue.*`) or a draft button.
- [ ] Preload: `openExternal`, config, logs available?
- [ ] Storage: persistent prefix (e.g. `rx-` in Reasonix).
- [ ] Write a short report with selectors and uncertainties.

**Gate 0**: audit report + candidate selectors. No writes.

### Phase 1 — Restore point

- [ ] Plain: `apply-patch.ps1 -BackupOnly` → `.bak` + `.sha256` + `old/` archive.
- [ ] Asar: copy `app.asar.bak`, manifest of `app.asar.unpacked`.
- [ ] Verify the copy hash before continuing.
- [ ] Record the exact return path.

**Gate 1**: verified backup. Otherwise touch nothing.

### Phase 2 — Packaging

**Plain UI**:

- [ ] Copy the module into the UI folder.
- [ ] Add `<script src="./voice-input.js"></script>` before `</body>`.
- [ ] No asar, no build.

**UI inside `app.asar`**:

- [ ] Extract the asar to a temporary folder.
- [ ] Patch `index.html` and copy the module.
- [ ] Repack with `--unpack-dir` for each unpacked package and `--unpack "**/<rel>"` for
      loose files.
- [ ] Compare the `app.asar.unpacked` manifest before/after: **0 differences**.
- [ ] Refuse an archive that grows unexpectedly.

**Gate 2**: the patch is applied on a **copy** of the UI, not yet the real install.

### Phase 3 — Selectors

- [ ] Fill `findInput()`, `findSubmitButton()`, `findStopButton()`.
- [ ] Exclude the stop button from the send lookup.
- [ ] Check selectors in the bundle (grep) **and** in the DOM (DevTools).
- [ ] Test a new chat, an old thread, a narrow window, a resize.
- [ ] Check `elementFromPoint` at the mic centre = mic.

**Gate 3**: the 3 selectors are stable and the mic is clickable.

### Phase 4 — Module adaptation

- [ ] Storage keys: persistent prefix (e.g. `rx-ocVoice.*`).
- [ ] External link: `reasonixHost.openExternal` / `electronAPI` / `window.open`.
- [ ] Logs: `console` + `localStorage` buffer (no mandatory logs API).
- [ ] Key: panel + real test; do not assume a config API.
- [ ] `isVisible()`: accept `readOnly` if the app locks the composer during generation.
- [ ] Auto-send: retry ~2 s if the button is disabled (upload/render).
- [ ] During generation: anchor next to `session.stop` if `session.send` disappears, never
      click stop.

**Gate 4**: the module loads without JS errors and the panel opens.

### Phase 5 — Anchoring (the small adjustments)

- [ ] Insert the anchor **after send**, inside the real action row.
- [ ] If send is inside a small `overflow:hidden` tooltip wrapper, climb to the parent and
      insert after the wrapper, not inside it.
- [ ] If the bar is narrower than ~80 px, place the mic **above** the arrow with
      `position:fixed` in `<body>` (escapes `z-index`/`overflow`).
- [ ] Debounce re-anchoring (80 ms) and discard self-made mutations (`takeRecords()`).
- [ ] Listen to `resize`, re-anchor immediately and again after ~250 ms.
- [ ] `positionOverlay`: for a fixed element, `offsetParent` is `null`; use
      `getBoundingClientRect()`.

**Gate 5**: mic on the right when wide, above when narrow, clickable in both.

### Phase 6 — Tests on a copy

- [ ] `node --check` the module.
- [ ] Patcher: apply / check / rollback / reapply, all exit 0.
- [ ] Rollback: hash restored, module removed.
- [ ] Corrupted checksum: rollback refused, patch intact.

**Gate 6**: the full loop is proven on a copy.

### Phase 7 — Install and runtime validation

- [ ] Install, reload (`Ctrl+R`) or relaunch.
- [ ] No `Renderer became unresponsive` / `render-process-gone` after 30 s.
- [ ] Mic visible and clickable: new chat, old thread, narrow, resized.
- [ ] Panel: key visible, real Gemini test, explicit error message.
- [ ] Dictate short, long, with an attachment.
- [ ] Auto-send ON/OFF; keyword; queue while the agent works.
- [ ] Check `localStorage` / the module log.

**Gate 7**: all above pass, or are documented as app limitations.

### Phase 8 — Documentation

- [ ] Version, selectors, fingerprints (`index.html`, bundle).
- [ ] Dated journal (append-only): decisions, tests, failures.
- [ ] Problem → solution table.
- [ ] Reapply procedure after an update.
- [ ] Manual rollback (copy `.bak`, remove the module).

**Gate 8**: another agent can resume the repo without oral context.

## Feature contract (test these)

- [ ] **Manual mode**: auto-send OFF → text inserted, **not sent**; the user reviews and sends.
- [ ] **Automatic mode**: auto-send ON → text inserted **and sent** when recording stops.
- [ ] **Attachment**: attach a file, dictate → text + file go together; auto-send includes it.
- [ ] **Queue**: agent busy → message queued; several messages can wait; native drain where
      available, otherwise the user can force/manual send.
- [ ] **Force/fallback**: send button disabled → retry ~2 s, then explicit error + clipboard;
      the user can always click send/queue manually.
- [ ] **Right-click**: hidden menu opens key, model, language, auto-insert, auto-send and
      send keyword; left click only records/stops.
- [ ] **Gemini vs Win+H**: Gemini is the recommended default for accuracy; Windows is the
      offline/no-key fallback.

## 3. “95%” checklist

| Area | Covered by the method |
|---|---|
| Record / stop / transcription | yes |
| Insert into composer | yes |
| Auto-send + keyword | yes |
| Attachment | yes (the module does not touch it) |
| Queue | app-dependent (verify) |
| Anchoring wide / narrow / resize | yes (rules + measurements) |
| Backup / rollback | yes |
| Documentation / journal | yes |
| Exact app selectors | **to measure** (5%) |
| Runtime behaviour (CSP, mic, interjection) | **to test** (5%) |

## 4. The remaining 5% (small adjustments)

1. **Selectors** for composer, send and stop.
2. **Threshold** for switching right / above (bar width).
3. **Climb** from the tooltip wrapper (`overflow:hidden`) to the real bar.
4. **Storage prefix** and preload APIs.
5. **Queue behaviour** during generation (interject vs queue).

## 5. Known traps

| Trap | Symptom | Fix |
|---|---|---|
| Anchor onto itself | frozen renderer, observer loop | `isOwnNode`, debounce, `takeRecords()` |
| 32 px tooltip wrapper | mic over send (old thread) | climb to parent, insert after wrapper |
| Narrow bar | mic off-frame / unclickable | `position:fixed` above, in `<body>` |
| Storage prefix | key lost on restart | use the persistent prefix (e.g. `rx-`) |
| Disabled button | message stays in composer | retry ~2 s, then explicit error |
| `session.send` absent | mic jumps left | anchor next to `session.stop`, never click |
| `app.asar.unpacked` | native modules broken | `--unpack-dir` / `--unpack`, identical manifest |
| App update | mic disappears | reapply after backup |

## 6. Starter prompt (copy-paste)

```text
You are the porting agent for Reasonix Voice Input.

Repository: <repo path>
Target app: <name, version, install path>
Goal: add the mic button (record → Gemini → insert → auto-send).

Read first, in this order:
1. AGENT-PLAYBOOK.md (or FICHE-AGENT.fr.md)
2. docs/METHODOLOGY.md
3. docs/SUPPORTED-APPS.md
4. docs/DEMARCHE.md

Apply the roadmap Phase 0 → Phase 8. Do not modify anything before Phase 0
(read-only audit) and Phase 1 (verified backup). Test on a copy before the real
install. At each phase, return a short report with commands, measurements and
evidence. If a selector or behaviour is uncertain, say so instead of guessing.
Finish with the journal, fingerprints and rollback.
```

## 7. Acceptance criteria

- [ ] No renderer freeze after 30 s.
- [ ] Mic clickable (new chat, old thread, narrow, resize).
- [ ] Key really tested; explicit error if missing.
- [ ] Dictate → text inserted; auto-send / keyword / queue per the app.
- [ ] Attachment preserved.
- [ ] Verified backup and proven rollback.
- [ ] Documentation and journal up to date.

## 8. Rollback

| Packaging | Return |
|---|---|
| Plain | `RESTAURER-MIC-REASONIX.bat` or `apply-patch.ps1 -Rollback` |
| Asar | restore `app.asar.bak`, preserve `app.asar.unpacked` |
| Manual | copy `.bak` over `index.html`, delete `voice-input.js` |

Rollback must work **even if the app no longer starts**.
