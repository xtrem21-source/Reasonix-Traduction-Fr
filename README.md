# Reasonix-Traduction-Fr

<p align="center"><img src="assets/logo.png" width="128" alt="Reasonix Traduction FR"></p>


> **Reasonix Studio 2.55 and later — a new approach lives in [`pack-2.55/`](pack-2.55/).**
> One double-click applies the French interface, a three-provider microphone and an
> encrypted API-key vault. What is below describes the generic toolchain, kept unchanged.
> Read [NEW-APPROACH.md](NEW-APPROACH.md) to choose between the two.

**Translate the Reasonix Studio interface into your language.**

Reasonix-Traduction-Fr is a small, readable toolchain that lets you translate the
desktop interface of **Reasonix Studio** — the desktop app of the
[**DeepSeek-Reasonix**](https://github.com/esengine/DeepSeek-Reasonix) project —
into any language, without rebuilding the application and without its source code.

French is included as a complete, working demonstration. The tool itself is not
French-specific: it is a generic pipeline (extract → translate → inject → verify)
that anyone can point at another language.

> **Unofficial.** This project is not affiliated with, endorsed by, or sponsored
> by the DeepSeek-Reasonix project (Reasonix Studio) or its maintainers.
> See [Non-affiliation](#non-affiliation).

---

## Table of contents

- [Why this project exists](#why-this-project-exists)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install and use (French, in 3 steps)](#install-and-use-french-in-3-steps)
- [Adding a new language](#adding-a-new-language)
- [Supported versions](#supported-versions)
- [Known limitations](#known-limitations)
- [Repository layout](#repository-layout)
- [Non-affiliation](#non-affiliation)
- [Credits](#credits)
- [License](#license)

---

## Why this project exists

Reasonix Studio ships its interface in Chinese and English only. Anyone who
speaks neither language is left out — not because the software is closed, but
because its translations are compiled into the application and there is no
public way to add one.

Reasonix-Traduction-Fr fills that gap. It reads the interface's own string catalogs —
the application's translation sources — so you can translate the parts you
actually see, in a plain text file, and apply them locally. No Reasonix code is
redistributed: the catalogs are downloaded to your machine, and the translation is
applied to your own installation.

The goal is to make the software usable by people it currently excludes.

---

## How it works

Reasonix Studio is an Electron application. Its interface text lives in two
places:

1. **Web interface** — minified JavaScript bundles served to the window. Every
   visible sentence is a key/value pair in a dictionary located in the bundle
   `i18n-*.js`. The keys are the Chinese source strings; the values are the
   English translation. Injecting a new dictionary gives the interface a new
   language.
2. **Native shell** — the Electron main process (`app.asar`): the startup page,
   the right-click menu, the error dialogs, and the tray menu.

The toolchain handles both:

```
extract  →  translate  →  merge  →  inject  →  verify
 (read)     (yours)      (check)    (apply)    (prove)
```

- **extract** pulls the string keys out of the upstream catalogs — the app's own
  i18n sources, fetched locally and never republished.
- **translate** is *your* step: any method works — by hand, a spreadsheet, or an
  AI model. One batch helper is included that uses the DeepSeek API, but it is
  optional.
- **merge** combines your translated pieces and checks them (missing keys,
  unknown keys, broken `{placeholders}`).
- **inject** applies the result to your installation.
- **verify** loads the patched bundle and confirms it really translates.

Every step is a small Python script you can read end to end.

---

## Requirements

| Need | Why |
|---|---|
| **Reasonix Studio installed** | The tool patches your own installation. |
| **Python 3.8+** | All scripts are plain Python, standard library only. |
| **Node.js** | Only to read/write `app.asar` (the `asar` tool). |
| **Windows** | See [Known limitations](#known-limitations) — the current scripts assume Windows. |

No build step, no compiler, no internet (except for the optional AI translation
step and for fetching source strings).

---

## Install and use (French, in 3 steps)

> Back up before you start. The injector writes into your installed
> application. It keeps dated backups of every file it replaces, under
> `work/backup/`, but a copy of the install folder is never wasted.

```bash
git clone https://github.com/xtrem21-source/Reasonix-Traduction-Fr.git
cd Reasonix-Traduction-Fr
```

**1. Fetch and extract the strings**

```bash
python3 scripts/fetch_sources.py   # downloads the upstream string catalogs
python3 scripts/extract_i18n.py    # extracts the keys to translate
```

The catalogs are the application's own i18n sources. They are downloaded into
`sources/` (never committed) and turned into one JSON file per screen group in
`work/extracted/`.

**2. Translate**

Either drop an existing translation into `translations/<code>.json` (see
[Adding a new language](#adding-a-new-language)), or start from scratch with the
batch helper:

```bash
python3 scripts/next_batch.py 60          # shows the next 60 strings to translate
python3 scripts/check_placeholders.py     # verifies {placeholders} are intact
```

The French translation, `translations/fr.json`, is complete and can be used as a
reference for format and tone.

**3. Inject and verify**

```bash
python3 scripts/inject_fr.py              # applies dictionary + patches the bundles
python3 scripts/verify_installed.py       # proves the installed bundle translates
```

Restart Reasonix Studio. In **Settings → Language**, choose **Français**.

---

## Voice input (optional)

This release also ships an **optional voice-input module**: a dictation button in
the chat bar, using the Web Speech API for capture and Gemini for transcription
(BYOK — you bring your own key).

The unified launcher `MENU-REASONIX.bat` offers **three modes**, so you can apply
either part on its own:

| Choice | What it patches |
|---|---|
| `1` — French | Web interface + native context menu, nothing else |
| `2` — Microphone | Dictation button only |
| `3` — Both | French **and** dictation |
| `4` — Quit | Nothing |

From a terminal: `MENU-REASONIX.bat fr`, `MENU-REASONIX.bat mic`, or
`MENU-REASONIX.bat both` (useful for scripts and CI).

The module lives in `Reasonix-Voice-Input-publish/` and is **independent from the
translation**: it can be installed alone on an untranslated Reasonix Studio, or
together with the French pack. Each action is logged under `logs/`, and the
patched files are backed up with a timestamp.

---

## Adding a new language

The workflow is the same for every language. Replace `xx` with your language
code (for example `es`, `de`, `ja`).

1. **Extract the source strings.** `python3 scripts/extract_i18n.py` writes them
   to `work/extracted/`. These keys are the Chinese source text and must not be
   changed — they are the lookup keys.

2. **Create your dictionary.** Copy `translations/fr.json` to
   `translations/xx.json`, then replace the values (keep the keys). The file is a
   flat JSON object:

   ```json
   {
     "重命名聊天": "Renommer la conversation",
     "聊天标题": "Titre de la conversation"
   }
   ```

   - Keys: **Chinese source strings — do not translate or edit them.**
   - Values: **your language.**
   - Keep every `{placeholder}` exactly as written (`{n}`, `{name}`, `{alt}`…).
     `scripts/check_placeholders.py` verifies this for you.

3. **Check your work.** `python3 scripts/merge_fr.py` reports missing keys,
   unknown keys, and (via `check_placeholders.py`) broken placeholders.

4. **Inject and verify.**
   ```bash
   python3 scripts/inject_fr.py
   python3 scripts/verify_installed.py
   ```

5. **Share it.** Open a pull request adding `translations/xx.json`. You do not
   need to translate all ~3 900 strings to be useful — a partial dictionary
   degrades gracefully: any string you leave out is simply shown in its original
   Chinese, never as a blank.

A fuller, step-by-step guide is in [`docs/WORKFLOW-TRANSLATE.md`](docs/WORKFLOW-TRANSLATE.md).

---

## Supported versions

The interface bundles are **minified and content-hashed**, and strings are
patched by matching anchors inside that minified code. As a result, this tool is
**tied to a specific version of Reasonix Studio**.

| Component | Version |
|---|---|
| Reasonix Studio | **2.52.0** — the build this tool was developed and tested against |
| Upstream release | `studio-v2.52.0` (2026-10-26) |
| Interface bundles | `i18n-DunoFOkp.js`, `Settings-Bj8eAezi.js` (names change every release) |

**Check your version before applying.** Open the application's *About* panel, or
read the `version` field of `resources/app.asar` in the install folder. (The
upstream source declares `0.0.0` and injects the real version at build time, so
the built artifact is the only place the number lives.)

- **`2.52.0` is the build the patch anchors were verified against.** Reasonix
  Studio ships frequently; a newer release may move the anchors. At the time of
  writing, `2.52.0` was the current upstream release.
- On a **different version**, extraction usually still works (it reads the string
  catalogs, not the compiled bundle), but **injection may fail**: the anchor
  patterns may have moved, and the injector will report which patterns it could
  not find rather than corrupting anything.
- The scripts **do not** silently mis-apply: every patch is asserted to match
  exactly once, and a failed match is reported and skipped.
- When a newer Reasonix version breaks the anchors, the fix is to update the
  patterns in `scripts/patch252.py` (the 2.46.0 to 2.50.0 scripts are kept in
  `scripts/` for anyone still on those builds). Contributions for newer versions
  are welcome.

---

## Known limitations

Honest list, so nobody is surprised:

- **Windows-oriented.** Paths resolve via `%LOCALAPPDATA%`. The logic is easy to
  port, but macOS/Linux are untested and would need small changes in
  `scripts/paths.py`.
- **Electron desktop app only.** The Go backend (CLI, tray status text,
  notifications) ships its strings **compiled into a binary** and is out of
  scope. Only the English portion of a few native surfaces is affected. See
  `docs/LIMITATIONS.md`.
- **Tied to Reasonix Studio 2.52.0** for injection (see above).
- **2.52.0 support covers the web interface in this launcher.** The native
  `app.asar` step (`scripts/patch_asar247.py`, 2.49 anchors) still applies
  unchanged on 2.52 (11/11 replacements, 4/4 markers, checked), but
  `Francisation_2.52.bat` does not run it; the zip ships it separately.
- **The fallback language is configurable** with `--default-lang` or
  `REASONIX_UI_DEFAULT` (`fr`, `en` or `auto`, `fr` by default): when no language
  is saved, the interface opens in that language instead of falling back to
  English.
- **French is the only complete translation** shipped. Other languages are
  community contributions.
- **Partial translations are expected and safe.** A missing key falls back to
  Chinese, not to a blank or an error.
- **The `asar` step needs Node.** Without it, the web-interface translation still
  works; only the native surfaces (startup page, context menu, tray) are skipped.
- **Injecting modifies your installation.** Uninstalling or updating Reasonix
  Studio replaces the patched files; re-run the injector afterwards. The original
  files are kept under `work/backup/`.

---

## Repository layout

```
Reasonix-Traduction-Fr/
├── README.md                  # this file (English)
├── README.fr.md               # French translation
├── LICENSE                    # MIT — for this project
├── LICENSE-REASONIX.md        # MIT — the original Reasonix license
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitattributes             # normalizes line endings across platforms
├── .gitignore
├── scripts/                   # the toolchain
│   ├── paths.py               #   resolves all paths (portable)
│   ├── fetch_sources.py       #   download the upstream string catalogs
│   ├── extract_i18n.py        #   extract the translatable keys
│   ├── next_batch.py          #   show the next strings to translate
│   ├── translate_api.py       #   optional: batch-translate via an AI API
│   ├── merge_fr.py            #   combine + check translated pieces
│   ├── check_placeholders.py  #   verify {placeholders} survive
│   ├── inject_fr.py           #   apply the dictionary to the bundles
│   ├── patch_asar.py          #   translate the native Electron strings
│   ├── repack_asar.py         #   rebuild app.asar
│   ├── install_asar.py        #   install it (with backup)
│   ├── setup_asar_orig.py     #   grab a pristine app.asar as the reference
│   ├── vendor_asar.py         #   vendor the asar tool into work/tools
│   ├── scan_repo.py           #   scan for anything that must not be published
│   ├── go_extract.py          #   diagnostic: the Go backend is out of scope
│   ├── probe_api.py           #   optional: check that an API key is available
│   └── verify_*.py, verify_i18n.mjs   # prove the result
├── translations/
│   └── fr.json                # the French dictionary (complete)
├── docs/
│   ├── STRUCTURE.md
│   ├── WORKFLOW-TRANSLATE.md
│   ├── LIMITATIONS.md
│   ├── PRE-PUBLISH-CHECKLIST.md
│   └── LAUNCH/                # announcement drafts
└── work/                      # generated at runtime — never committed
```

---

## Non-affiliation

This is an **independent, unofficial** project. It is **not affiliated with,
endorsed by, or sponsored by** the
[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix) project
(Reasonix Studio), its maintainer, or its contributors.

- It contains **no DeepSeek-Reasonix source code** — no `app.asar`, no JavaScript
  bundles, no Go binary. It operates on *your* installed copy, on your machine.
- "DeepSeek-Reasonix" and "Reasonix Studio" refer to the original project, which
  belongs to its authors. All rights to those names and that software remain
  theirs.
- The original DeepSeek-Reasonix is licensed under the MIT License; a copy is kept
  in [`LICENSE-REASONIX.md`](LICENSE-REASONIX.md).

---

## Credits

- **[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)** — the
  project this tool serves — and the people who build it:
  - **Huahui Yu** — maintainer.
  - The [DeepSeek-Reasonix contributors](https://github.com/esengine/DeepSeek-Reasonix/graphs/contributors) —
    for the application, its interface text, and the language catalogs this tool reads.
- The MIT License text of DeepSeek-Reasonix is reproduced in
  [`LICENSE-REASONIX.md`](LICENSE-REASONIX.md), as its terms require.
- The `asar` tool (bundled, or installed on demand) — MIT, by the Electron
  project.
- French translation: contributed by this project's authors.

---

## License

**MIT** — see [`LICENSE`](LICENSE).

You may use, modify, and redistribute this tool and the translations it
contains, provided you keep the copyright notice and the Reasonix license notice.

