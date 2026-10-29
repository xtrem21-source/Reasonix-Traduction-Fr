# Changelog

All notable changes to this patch package are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] — 2026-10-29

### Added
- **Third provider: ElevenLabs Scribe v2.** The panel now offers Gemini, Groq or ElevenLabs.
  ElevenLabs uses the **batch** endpoint `POST https://api.elevenlabs.io/v1/speech-to-text`
  (`model_id=scribe_v2`, `language_code`, `tag_audio_events=false`, `xi-api-key` header): the
  16 kHz WAV already produced is sent as is, with no re-encoding and no streaming.
- **ElevenLabs key test**: `GET /v1/user`, no credit spent and no audio needed.
- **Key in the vault**: `ELEVENLABS_API_KEY` joins `GEMINI_API_KEY` and `GROQ_API_KEY` in the
  `reasonix:read-env` bridge (DPAPI, `data\home\mic-keys.bin`). The module keeps keys in memory
  only.

### Fixed
- **Destructive vault migration.** The bridge used to rewrite the vault with only the keys found
  in `.env`, so adding a third key would have wiped the first two. It now merges with what is
  already encrypted, then removes the migrated lines from `.env`.
- **Settings save**: the Gemini key is no longer required when Groq or ElevenLabs is selected;
  the missing-key message names the right provider.
- **Panel links**: the Groq and ElevenLabs links open the key page (the Groq link had no listener).

## [0.1.4] — 2026-10-19

### Fixed
- **Mic anchored to the wrong chat.** With two chats/panes open, the module took the first
  `session.send` button of the page. When the active chat entered generation, its send button
  was replaced by `session.stop`, so the mic disappeared from the active chat (or stayed on the
  other one). The lookup is now scoped to the active/visible composer, anchors to
  `session.stop` during generation, follows focus between panes, and keeps the mic visible
  during the send → stop transition. Validated on a two-pane DOM fixture and in Reasonix
  Studio 2.40.0.

## [0.1.3] — 2026-10-18

### Added
- **Agent playbook FR/EN**: `FICHE-AGENT.fr.md` / `AGENT-PLAYBOOK.md` — 8-phase roadmap,
  copy-paste starter prompt, 95% checklist, acceptance criteria, known traps.
- **Cline Desktop** listed as ported (small anchoring adjustments, not a constraint).
- **Feature contract** in README/tutorial/playbook: manual vs auto-send, attachments, queue,
  force/fallback, hidden right-click menu.
- **Gemini vs Windows Win+H** comparison: accuracy, punctuation, languages, offline, cost.
  Gemini is the module's main quality advantage; Windows is the offline/no-key fallback.

### Changed
- README, tutorial and supported-apps tables updated for the four ports.

## [0.1.2] — 2026-10-18

### Added
- MIT `LICENSE` and an “unofficial project” disclaimer in both READMEs.
- **FR/EN documentation**: tutorial, inspection, method, problems/solutions, version,
  journal, changelog, security, publication, supported apps.
- **Portable 8-step method**: the same module adapts to other Electron apps (AionUi 2.2.2,
  Open Cowork); only selectors, storage and preload APIs change.

### Changed
- `docs/INSPECTION-2026-10-18.md`: install path sanitized to
  `%LOCALAPPDATA%\Programs\Reasonix Studio`.
- `docs/reference/README.md`: the app's `index.html` is **not shipped** in the public
  repository; instructions to recreate it locally.
- `.gitignore`: ignores the local `docs/reference/ReasonixStudio-*.html` copy.

### Removed
- The Reasonix Studio `index.html` is no longer tracked in the public export (third-party
  file, app license undocumented).

## [0.1.1] — 2026-10-18

### Added
- **Guaranteed restore point**: `PREPARER-SAUVEGARDE-MIC-REASONIX.bat` (`-BackupOnly`) creates
  `index.html.bak` + `index.html.bak.sha256` + a dated archive in `old/`, **without patching**.
- `RESTAURER-MIC-REASONIX.bat` (`-Rollback`) restores `index.html`, removes `voice-input.js`,
  verifies the restored hash, and works even if Reasonix Studio no longer starts.
- The patcher now **verifies the backup copy before any write** and aborts on mismatch.
- `-Check` now also reports `backup present` and `backup sha256`; a missing/unverified backup
  makes the check fail.
- Manual fallback documented in both READMEs: copy `index.html.bak` over `index.html`, delete
  `voice-input.js`.

### Changed
- Re-apply (`-Force`) verifies the backup checksum and refuses a backup that is itself patched.

## [0.1.0] — 2026-10-18

### Added
- Initial package for **Reasonix Studio 2.40.0**.
- `src/voice-input.reasonix.js` — adaptation of AiTron Voice Input v5:
  - Reasonix composer selectors (`textarea[data-action-keydown="session.send"]`,
    `button.btn.send[data-action="session.send"]`);
  - `rx-ocVoice.*` storage keys (Reasonix's preload persists only `rx-*` keys);
  - `reasonixHost.openExternal` for the Gemini key link;
  - exclude `session.stop` / `.btn.stop` from the send-button lookup;
  - if `session.send` disappears during a generation, anchor next to `session.stop` without
    ever clicking it;
  - allow a readOnly composer (Reasonix makes it readOnly during generation);
  - retry the auto-send for ~2 s if the send button is still disabled;
  - the AionUi anchoring/observer fixes are kept.
- `scripts/apply-patch.ps1` — plain-frontend patcher: backup, inject one script tag, verify
  hash, `-Force`, `-Rollback`, `-Check`. The app is **never closed**.
- `INSTALLER-MIC-REASONIX.bat`, `REAPPLIQUER-MIC-REASONIX.bat`,
  `DESINSTALLER-MIC-REASONIX.bat`, `VERIFIER-MIC-REASONIX.bat`.
- `docs/INSPECTION-2026-10-18.md`, `docs/DEMARCHE.md`, `docs/JOURNAL.md`,
  `docs/VERSION-REASONIX.md`, reference copy of the original `index.html`.

### Known limitations / to validate
- Runtime CSP headers, microphone permission and Gemini `fetch` from the sandboxed renderer
  were not tested (inspection was read-only; Reasonix Studio was not restarted).
- The exact behaviour of `session.send` during a generation (interjection vs queue) must be
  tested.
- The frontend folder is replaced by app updates: reapply the patch.
