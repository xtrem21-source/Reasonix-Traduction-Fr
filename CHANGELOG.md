# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.50.0] — 2026-10-24

Support for **Reasonix Studio 2.50.0**. This release required rewriting every
pattern: the minifier of 2.50 rotated the variable names of the i18n bundle.

### Added

- **`Francisation_2.50.bat`**, the launcher for this release, with the same
  variables and the same checks as its predecessors (`REASONIX_STUDIO_DIR`,
  Python fallback, running-instance guard).
- **`scripts/patch250.py`**: same pipeline as 2.49, with the six patterns
  rewritten for the new names.
- **`scripts/force_auto_fr.py`**: forces the automatic language detection to
  answer `fr`. Without it, French does not hold on 2.50 — see *Changed*.
- **`Reasonix-FR-2.50.zip`**: complete, self-contained package for this version.

### Changed

- **The i18n variable names rotated in 2.50.** Current language moved from `y`
  to `b`, the current dictionary from `b` to `x`, the dictionary collection from
  `v` to `y`, and the translation function from `O` to `k` (exported as `o`).
  The 2.49 patterns do not match this build and fail loudly instead of writing.
- **The language selector is no longer durable.** Reasonix Studio 2.50 resets
  its language setting to empty at startup and falls back to auto-detection.
  French holds because auto-detection is forced to `fr`, not because the choice
  is respected. Choosing English in the settings will not persist.

### Known issues

- Two settings labels, `Ask` and `MCP · Skills`, are not translated: their
  source strings changed in 2.50 and no longer match the dictionary.
- The root cause of the language reset — which component writes the empty value
  — is not identified. It is most likely inside the host executable.

---

## [2.49.0] — 2026-10-23

Support for **Reasonix Studio 2.49.0**. The web bundle is now
`i18n-BR2QJ_aY.js` and the settings bundle `Settings-Bbgyi4OO.js`. The 2.48.0
release is deliberately skipped: no work was published for it. The 2.47.0 tag
and its release stay available unchanged.

### Added

- **Reasonix Studio 2.49.0 support**: `scripts/patch249.py` (web interface:
  i18n bundle, Settings language selector, `index.html` startup language) and
  its launcher `Francisation_2.49.bat`.
- **77 new strings translated**, bringing `translations/fr.json` to
  **5 034 entries** (4 957 carried over from 2.47.0 + 77 new). No translation
  was changed or lost: all 4 957 previous entries are byte-identical.
- `patch249.py` reads the install directory from `REASONIX_STUDIO_DIR`, so a
  Reasonix Studio installed outside `%LOCALAPPDATA%\Programs` (for example
  `J:\Reasonix Studio`) patches correctly.

### Changed

- `README.md` / `README.fr.md` / `LISEZ-MOI.md`: supported version is now
  **2.49.0** (bundles `i18n-BR2QJ_aY.js`, `Settings-Bbgyi4OO.js`).
- The 2.46.0 and 2.47.0 scripts are kept in `scripts/` for anyone still on
  those builds.
- `patch249.py` is idempotent: on an already-patched bundle it refreshes the
  dictionary instead of re-applying the anchors, and it refuses to patch if a
  pattern no longer matches exactly once.

### Known limitations

- Targets **Reasonix Studio 2.49.0**. A newer release may move the anchors;
  injection fails visibly (never silently) when that happens.
- **The native `app.asar` step is not ported to 2.49.** 2.49 users get the fully
  translated web interface; the native surfaces (startup page, context menu,
  tray) remain untranslated until `patch_asar249.py` exists.

---

## [2.47.0] — 2026-10-21

Support for **Reasonix Studio 2.47.0**. The web bundle is now
`i18n-DS26LhWq.js` and the settings bundle `Settings-B_4tuZ4i.js`; the native
`app.asar` anchors were re-verified. The 2.46.0 tag and its release stay
available unchanged.

### Added

- **Reasonix Studio 2.47.0 support**:
  `scripts/patch247.py` (web interface: i18n bundle, Settings language
  selector, `index.html` startup language) and `scripts/patch_asar247.py`
  (8 native files: `uilang.js`, `starting.js`, `editmenu.js`, `hostexit.js`,
  `shelllog.js`, `packagegrants.js`, `main.js`, `tray.js`), driven by
  `scripts/asar_patches.json`.
- **160 new strings translated**, bringing `translations/fr.json` to
  **4 957 entries** (4 797 carried over from 2.46.0 + 160 new).
- An optional voice-input module is shipped in `Reasonix-Voice-Input-publish/`,
  driven by `MENU-REASONIX.bat`, which offers three modes: **French only**,
  **microphone only**, or **both**. The module is independent from the
  translation and can be installed alone, alongside the French pack, or not at
  all.

### Changed

- `README.md` / `README.fr.md`: supported version is now **2.47.0**
  (bundles `i18n-DS26LhWq.js`, `Settings-B_4tuZ4i.js`).
- The 2.46.0 and 2.40.0 scripts are kept in `scripts/` for anyone still on
  those builds.
- Both patches are idempotent: a re-run detects an already-patched bundle and
  reports it instead of rewriting.

### Known limitations

- Targets **Reasonix Studio 2.47.0**. A newer release may move the anchors;
  injection fails visibly (never silently) when that happens.

---

## [2.46.0] — 2026-10-20

Support for **Reasonix Studio 2.46.0**. This is the major release: the interface
bundle changed shape, 946 new strings were added, and the native patch anchors
were re-verified. It supersedes the short-lived `v0.2.0` tag, which pointed to
the same content under the old numbering.

### Added

- **Reasonix Studio 2.46.0 support**: the interface bundle changed shape since
  2.40.0 (dictionaries and helpers were renamed: `h` → `_`, `T` → `D`, `x` → `C`,
  `w` → `E`). New injectors match the 2.46.0 anchors:
  `scripts/inject_fr_246.py` (web interface) and `scripts/asar_246.py` (native
  surfaces), with `scripts/setup_asar_orig_246.py` and
  `scripts/verify_asar_246.py`.
- **946 new strings translated**, bringing `translations/fr.json` to
  **4 797 entries** (3 866 carried over from 0.1.0 + 946 new).
- `scripts/check_placeholders.py` now validates the final dictionary directly
  (`translations/fr.json`), not the intermediate work files.

### Changed

- `README.md` / `README.fr.md`: supported version is now **2.46.0**
  (bundles `i18n-BBt-pvJM.js`, `Settings-DVNS8HMO.js`).
- The 2.40.0 scripts are kept in `scripts/` for anyone still on that build.

### Known limitations

- Targets **Reasonix Studio 2.46.0**. A newer release may move the anchors;
  injection fails visibly (never silently) when that happens.

---

## [0.1.0] — 2026-10-16

First public release.

### Added

- **Generic translation pipeline** for Reasonix Studio, in five steps:
  `extract` → `translate` → `merge` → `inject` → `verify`.
- **Extraction** of the interface strings from an installed copy of Reasonix
  Studio (`scripts/extract_i18n.py`), including the Chinese-keyed dictionary held
  in the minified interface bundles.
- **Dictionary injection** (`scripts/inject_fr.py`): adds the translated
  dictionary to the interface bundle, teaches the language resolver the new code,
  and adds the language to the in-app language selector.
- **Native surface translation** (`scripts/patch_asar.py`,
  `scripts/repack_asar.py`, `scripts/install_asar.py`): startup page, right-click
  menu, error dialogs, legacy-install dialog, and the tray menu.
- **Verification** (`scripts/verify_installed.py`,
  `scripts/verify_asar_installed.py`): loads the *installed* bundle and proves
  that it translates, rather than assuming it does.
- **Placeholder safety** (`scripts/check_placeholders.py`): fails if any
  `{placeholder}` is lost, renamed, or added in a translation.
- **Batch helpers**: `scripts/next_batch.py` (show the next strings to translate)
  and `scripts/translate_api.py` (optional batch translation via the DeepSeek
  API).
- **Complete French translation**: `translations/fr.json`, 3 866 strings.
- **Portable path resolution** (`scripts/paths.py`): the project can be cloned,
  copied, or moved anywhere; it locates Reasonix Studio from the environment and
  never hard-codes a path.
- **Automatic backups**: every file the injector replaces is copied to a dated
  folder under `work/backup/` before it is overwritten.
- **Documentation**: `README.md` (English), `README.fr.md` (French),
  `docs/STRUCTURE.md`, `docs/WORKFLOW-TRANSLATE.md`, `docs/LIMITATIONS.md`,
  `docs/PRE-PUBLISH-CHECKLIST.md`, and announcement drafts under `docs/LAUNCH/`.

### Known limitations

- Targets **Reasonix Studio 2.40.0**. The interface bundles are content-hashed
  and minified; a different version may move the patch anchors. Injection fails
  visibly (never silently) when that happens.
- **Windows-oriented** path handling. macOS and Linux are untested.
- **Web interface and Electron shell only.** The Go backend (CLI, tray status
  text, notifications) compiles its strings into a binary and is out of scope.
- **French is the only complete translation** shipped.

### Security and privacy

- No DeepSeek-Reasonix code is redistributed. The tool operates on the user's own
  installation.
- The API-based translation helper is **optional** and sends interface strings to
  the configured provider (DeepSeek by default). No other step touches the
  network.

### Credits

- **[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)** —
  maintained by **Huahui Yu** and its contributors — for the application this
  tool serves. MIT licensed; see
  [`LICENSE-REASONIX.md`](LICENSE-REASONIX.md).
- Unofficial and unaffiliated with upstream.

[2.46.0]: https://github.com/xtrem21-source/Reasonix-Traduction-Fr/releases/tag/v2.46.0
[0.1.0]: https://github.com/xtrem21-source/Reasonix-Traduction-Fr/releases/tag/v0.1.0
