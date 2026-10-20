# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2026-10-20

Support for **Reasonix Studio 2.46.0**.

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

[0.2.0]: https://github.com/xtrem21-source/Reasonix-Traduction-Fr/releases/tag/v0.2.0
[0.1.0]: https://github.com/xtrem21-source/Reasonix-Traduction-Fr/releases/tag/v0.1.0
