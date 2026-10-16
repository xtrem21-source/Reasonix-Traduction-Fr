# Repository structure

This document explains what every folder and file is for, and — more usefully —
what must **never** be committed.

---

## What is committed

```
Reasonix-Translate/
├── README.md                  # English overview (the front door)
├── README.fr.md               # French overview
├── LICENSE                    # MIT — for this project
├── LICENSE-REASONIX.md        # MIT — the original Reasonix license (kept verbatim)
├── CONTRIBUTING.md            # how to translate, report, and submit
├── CHANGELOG.md               # release history
├── .gitignore
│
├── scripts/                   # the toolchain (see below)
├── translations/              # dictionaries: one JSON per language
├── docs/                      # documentation
│   ├── STRUCTURE.md           #   this file
│   ├── WORKFLOW-TRANSLATE.md  #   step-by-step translation guide
│   ├── LIMITATIONS.md         #   what this tool does not do
│   ├── PRE-PUBLISH-CHECKLIST.md
│   └── LAUNCH/                #   announcement drafts
└── work/                      # generated — GITIGNORED, never committed
```

### `scripts/`

Each script does one thing and can be read end to end.

| Script | Role |
|---|---|
| `paths.py` | Resolves every path. The project is portable: it derives its own root from its location and finds Reasonix Studio from the environment. **Every other script imports this.** |
| `fetch_sources.py` | Downloads the public string catalogs from the Reasonix repository. **Required** before extraction. |
| `extract_i18n.py` | Reads the fetched catalogs and writes the string keys to `work/extracted/`. |
| `next_batch.py` | Prints the next N strings still untranslated. |
| `translate_api.py` | *(optional)* Batch-translates via an AI API (DeepSeek by default). |
| `merge_fr.py` | Merges the translated pieces and reports missing / unknown keys. |
| `check_placeholders.py` | Fails if any `{placeholder}` was lost, renamed, or added. |
| `inject_fr.py` | Applies the dictionary to the web-interface bundles and enables the language. |
| `patch_asar.py` | Produces a French-patched copy of the native Electron strings (startup page, context menu, dialogs, tray). |
| `repack_asar.py` | Rebuilds `app.asar` from the patched copy. |
| `install_asar.py` | Installs the rebuilt `app.asar`, keeping a dated backup. |
| `verify_installed.py` | Loads the **installed** bundle in Node and proves it translates. |
| `verify_asar_installed.py` | Extracts the installed `app.asar` and checks the native strings. |
| `verify_i18n.mjs` | The Node harness used by the two verifiers above. |
| `go_extract.py` | *(diagnostic)* Confirms the Go backend's strings are compiled into a binary (out of scope). |

### `translations/`

One file per language: `translations/<code>.json`.

```json
{
  "重命名聊天": "Renommer la conversation",
  "聊天标题": "Titre de la conversation"
}
```

- **Keys** — the Chinese source strings. They are the lookup keys. Never edit or
  translate them.
- **Values** — the translation.
- **Placeholders** — `{n}`, `{name}`, `{alt}`… must survive unchanged.

`fr.json` is complete (3 866 entries) and doubles as the format reference.

### `work/`

Everything generated at runtime:

| Folder | Contents |
|---|---|
| `work/backup/` | Dated copies of every file the injector replaces. Your undo. |
| `work/extracted/` | The string keys pulled from the installation. |
| `work/asar_orig/` | A pristine extraction of `app.asar`, kept as the reference for the native patch. |
| `work/asar_fr/` | The patched copy, before repacking. |
| `work/tools/` | The `asar` tool, so the project does not depend on a global install. |

`work/` is **generated** and **gitignored**. It can always be rebuilt by
re-running the extractor.

---

## What is never committed

This is a licensing requirement, not just tidiness.

| Excluded | Why |
|---|---|
| `app.asar`, `*.js` interface bundles | Reasonix code. Redistributing it is not this project's job. |
| `go_messages_en.json` | Extracted from the Reasonix Go binary — a derived copy of their strings. |
| `sources/` | Files fetched from the Reasonix repository. Read locally, never republished. |
| `work/backup/` | Contains copies of Reasonix code. |
| `work/asar_orig/`, `work/asar_fr/` | Likewise. |
| `node_modules/`, `work/tools/` | Third-party tools; installed on demand. |
| `__pycache__/`, `*.pyc` | Build noise. |
| `.env` | May hold API keys. |

The `.gitignore` covers all of these, plus safety-net entries in case one ever
appears at the top level.

---

## Why this layout

- **`scripts/` and `translations/` are separate** so a translator never has to
  open a script, and a developer never has to open a translation.
- **`docs/` is separate from the READMEs** so the front door stays short and the
  depth stays available.
- **`work/` is separate and disposable** so "what is the project" (committed) and
  "what the project produced" (generated) never blur.
- **`paths.py` is the single source of truth for locations**, so the whole thing
  can be cloned, copied, or renamed without editing anything.
