# Changelog

All notable changes to this pack are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows the
Reasonix Studio release it targets.

## [2.55.0] — 2026-10-29

First public release. Targets **Reasonix Studio 2.55.0** (Windows amd64).

### Added

- **French interface, measured.** A 5 243-entry dictionary injected into the bundle the app
  actually loads, plus a patcher for the strings written directly in the bundles.
  Verification on 2.55.0: **5 205 / 5 205 strings covered, 0 error, 0 hard-coded label left
  untranslated**.
- **Encrypted key vault.** `GEMINI_API_KEY`, `GROQ_API_KEY` and `ELEVENLABS_API_KEY` move from
  `.env` into `data\home\mic-keys.bin`, encrypted by Windows DPAPI through Electron
  `safeStorage`. The page never receives a key: decryption happens in the main process, behind a
  whitelist of three names. `verifier-cles.bat` reports the vault state without ever printing a
  key. Limits are documented in [SECURITY.md](SECURITY.md).
- **Non-destructive migration.** The bridge merges with the existing vault instead of replacing
  it, so adding a third key cannot erase the first two.
- **Microphone with three providers.** Gemini (`gemini-3.5-flash-lite`), Groq
  (`whisper-large-v3-turbo`) and **ElevenLabs Scribe v2** (`POST /v1/speech-to-text`, batch).
  One key field visible at a time, selector in the panel, "Test API key" that only tests the
  selected provider — `GET /v1/user` for ElevenLabs, which spends no credit.
- **French context menu.** `app.asar` is repatched: start screen, dialogs, tray, context menu,
  and the `readEnv`/`sendKey` bridges.
- **Skill descriptions in French.** Seven installed skills get a French `description` in their
  `SKILL.md` frontmatter; content and references are untouched. The nine built-in skills keep
  their English description, which is compiled into the kernel binary.
- **Rollback and self-test.** `restaurer.bat` restores every file from a dated backup;
  `tools/selftest.py` replays the pipeline on a copy of the application.

### Changed

- The engine reads the application version from `Reasonix Studio.exe` (`FileVersion`) instead of
  hard-coding it: no version number anywhere in the scripts.
- A translation gap stops the run before writing anything, and produces `a-traduire.tsv`; the
  patch never guesses a missing string.

### Fixed

- The `read-env` block of the asar patch ended without its anchor, which deleted the opening line
  of `shell:open-external` and made `main.js` unparseable — the whole native patch was silently
  refused on 2.55. The block now ends with the anchor it replaces.
- The microphone panel only hid the unused key fields when it was opened, so a panel created
  before any setting showed the three keys at once. Groq and ElevenLabs are now hidden in the
  HTML itself, the state is recomputed when the panel is created, and an unknown provider falls
  back to Gemini.
- `Write-Log 'a' + b + 'c'` in the installer passed `+` as a colour and aborted the script after
  the copy; the concatenation is parenthesised.

### Notes

- Reasonix Studio updates replace `frontend-next\` and `app.asar`: the interface returns to
  English and the microphone disappears until the pack is applied again. That is expected.
- ElevenLabs is used in batch mode: text arrives after you stop, not while you speak.
