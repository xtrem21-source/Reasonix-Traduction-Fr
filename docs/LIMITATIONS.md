# Known limitations

An honest account of what this tool does, does not do, and cannot do. Read this
before filing a bug — several "bugs" are described here by design.

---

## 1. It is tied to one version of Reasonix Studio

**Target: Reasonix Studio 2.40.0.**

The interface bundles are *minified* and their filenames are *content-hashed*
(`i18n-dyxISsoS.js`). Strings are translated by matching anchors inside that
minified code. When Reasonix ships a new version, the code is minified
differently and the anchors move.

What this means in practice:

- **Extraction** generally still works on other versions — it reads whatever
  bundles are present and pulls the string keys out.
- **Injection** may fail on another version. When it does, the injector reports
  the exact pattern it could not find and skips it. It never guesses.
- **The failure is visible.** Every patch is asserted to match exactly once; a
  mismatch is reported, not silently applied.

Fixing a new version means updating the anchor patterns in
`scripts/inject_fr.py` (web bundles) and `scripts/patch_asar.py` (native
strings). See `CONTRIBUTING.md` → *Supporting a new version*.

---

## 2. The Go backend is out of scope

Reasonix Studio has three parts:

| Part | Language | Strings | Translated? |
|---|---|---|---|
| Web interface | JavaScript (in the bundles) | ~3 900, keyed by Chinese | **Yes** |
| Electron shell | JavaScript (`app.asar`) | startup page, menus, dialogs, tray | **Yes** |
| Kernel / CLI / notifications | Go (compiled binary) | ~650 | **No** |

The Go binary (`reasonix-studio-host.exe`, ~44 MB) **compiles its strings into
the binary**. Its own source comment states the scope:

> *"Scope (v1): CLI surface only — welcome, init wizard, chat REPL banner, usage,
> user-facing CLI errors."*

So, in practice:

- those strings appear **in the terminal**, not in the desktop window;
- the only desktop surface they reach is the **tray menu / status line**, and the
  Electron tray labels were reconstructed in the target language as part of the
  shell translation, so the tray is covered anyway;
- **notifications** also use that catalogue, but they are disabled by default.

Translating the Go side would require rebuilding a binary from source — a
different project, deliberately not attempted here. `scripts/go_extract.py`
documents the finding (it also shows the binary is locked while the app runs, so
it cannot be patched in place).

---

## 3. Windows-oriented

Paths resolve through `%LOCALAPPDATA%`. The logic is easy to port, but **macOS
and Linux are untested** and would need small changes in `scripts/paths.py`
(different install locations, different permission model for the `.app` bundle).

The `.bat`-style convenience launcher is Windows-only; the Python scripts
themselves are portable in principle.

---

## 4. It modifies your installation

This is inherent: the tool edits the files of the application you have installed.

What protects you:

- **Every replaced file is copied to `work/backup/<timestamp>__<name>` first.**
- `install_asar.py --restore` puts back the original `app.asar`.
- Reinstalling or updating Reasonix Studio restores everything.

What it means:

- **After a Reasonix update, re-run the injector.** The update overwrites the
  patched files and the translation is gone until you re-apply it.
- On a shared or managed machine, patching an installed application may not be
  allowed by policy. Check before doing it.

---

## 5. Partial translations are normal and safe

A missing key falls back to the **original Chinese** — never to a blank, never to
an error, never to the key itself. This is by design in Reasonix's own i18n
layer, and it is why a half-finished translation is still useful.

Consequence: after a partial translation you will see **a mix** of your language
and Chinese. That is expected, not a bug.

---

## 6. Translation quality is not checked automatically

The tooling verifies **structure**: that keys match, that placeholders survive,
that the files are valid. It does **not** verify meaning, grammar, or tone. A
translation can pass every check and still read badly.

Machine-translated output (`scripts/translate_api.py`) should be reviewed by a
speaker before it is published.

---

## 7. Some strings are intentionally not translated

- **Product names**: Reasonix, WeChat, Alipay, Douyin, QQ, GitHub, VS Code, …
- **Technical tokens**: URLs, file names, keyboard shortcuts, shell commands.
- **Format placeholders**: `{n}`, `{name}`, `{alt}` — substituted at runtime.

Translating these would break either the display or the behaviour.

---

## 8. The native (`asar`) step needs Node.js

Reading and writing `app.asar` uses the `asar` tool, which runs on Node. Without
Node:

- the **web interface** translation still works fully;
- the **native surfaces** (startup page, context menu, tray) are skipped.

`scripts/vendor_asar.py` can embed a private copy of the tool inside `work/tools/`
so the project does not depend on a global install — but Node itself is still
required.

---

## 9. No integrity checking is performed by the application

A useful fact, not a limitation: Reasonix Studio does **not** verify the
integrity of `app.asar` or of the interface bundles (no `asarIntegrity` /
`EnableEmbeddedAsarIntegrityValidation` fuse). That is why modifying them works at
all. If a future release adds such a check, this approach would stop working — and
that would be a deliberate choice by the Reasonix authors, to be respected.

---

## 10. What this tool will not do

- **It will not redistribute Reasonix code.** No binaries, bundles, or sources
  are shipped; the tool works on your own installation.
- **It will not patch silently.** A pattern that does not match is reported, not
  forced.
- **It will not touch the network** except for the optional AI-translation step
  and the optional source-fetching step.
