# Reasonix-Traduction-Vault

[![Version](https://img.shields.io/badge/reasonix%20studio-2.55.0-2f81f7)](#supported-versions)
[![Platform](https://img.shields.io/badge/platform-Windows%20amd64-0078D4)](#requirements)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](LICENSE)
[![Statut](https://img.shields.io/badge/status-unofficial-orange)](#non-affiliation)

**French translation, microphone and encrypted key vault for Reasonix Studio — in one double-click.**

This pack translates the desktop interface of **Reasonix Studio** (the desktop app of
[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)) into French, adds a
dictation button with three transcription providers, and moves the API keys out of a plain
text file into a vault encrypted by Windows.

> **Unofficial.** Not affiliated with, endorsed by, or sponsored by the DeepSeek-Reasonix
> project or its maintainers. The installer replaces `resources\frontend-next\` and
> `app.asar`; this pack repairs both after every update. See [Non-affiliation](#non-affiliation).

---

## Table of contents

- [What it does](#what-it-does)
- [Why a vault](#why-a-vault)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install and use](#install-and-use)
- [The microphone](#the-microphone)
- [Key security](#key-security)
- [Maintenance: the patch follows the app](#maintenance-the-patch-follows-the-app)
- [Known limitations](#known-limitations)
- [Repository layout](#repository-layout)
- [Non-affiliation](#non-affiliation)
- [License](#license)

---

## What it does

| Layer | What the pack does |
|---|---|
| **Interface** | Injects a 5 243-entry French dictionary into the bundle the app actually loads, and rewrites the strings written directly in the bundles (labels, states, tooltips, messages) |
| **Native strings** | Repatches `app.asar`: French start screen, dialogs, tray, **context menu**, and the bridge that reads the vault |
| **Microphone** | Installs `voice-input.js` and its `<script>` tag: dictation with **Gemini**, **Groq** or **ElevenLabs**, one key field visible at a time |
| **Skills** | Translates the `description` of every skill installed in `<home>\skills` (frontmatter only, content untouched) |
| **Keys** | Moves `GEMINI_API_KEY`, `GROQ_API_KEY` and `ELEVENLABS_API_KEY` from `.env` into `mic-keys.bin`, encrypted with Windows DPAPI |
| **Verification** | Checks that every string of the build returns French, then reads back the hash of each file it installed |
| **Rollback** | `restaurer.bat` puts every file back the way it was, from a dated backup |

Measured on Reasonix Studio 2.55.0: **5 205 / 5 205 strings covered, 0 error**, 0 hard-coded
label left untranslated.

## Why a vault

The microphone needs API keys. The obvious way to store them is a file — and a file is read by
anyone who can read the folder, copied by any sync client, and left behind in backups.

This pack does what the application does for its own secrets: it asks Windows to encrypt them,
then removes the plain lines from `.env`. What it does **not** do is make the keys harmless —
see [Key security](#key-security) for the exact boundary.

## How it works

```
mettre-a-jour.bat
   │
   ├── 1. close Reasonix Studio, remember which files it will touch
   ├── 2. dictionary     → dict/fr.json injected into the live i18n bundle
   ├── 3. hard-coded     → tools/patch_literals.py rewrites the loaded bundles
   ├── 4. microphone     → Reasonix-Voice-Input-publish/scripts/apply-patch.ps1
   ├── 5. native strings → tools/patch_asar252.py (menu, start, tray, vault bridge)
   ├── 6. skills         → tools/patch_skills.py (frontmatter descriptions)
   └── 7. verify         → tools/verify.mjs sweeps every string of the build
```

Each step is idempotent: running it twice rewrites nothing. Each step writes a dated backup
before touching a file (`.avant-*`, `backups/<timestamp>/`, `index.html.bak`).

## Requirements

- **Windows 10/11, amd64.**
- **Reasonix Studio 2.55.0**, installed as a plain folder (portable or `%LOCALAPPDATA%\Programs`).
- **Python 3** — the engine is a Python script. The launcher finds `py -3`, `%LOCALAPPDATA%\Programs\Python\Python313`, `C:\Python313`, or whatever `config.bat` says.
- **Node.js** — optional; the Reasonix Studio binary can serve as Node (`ELECTRON_RUN_AS_NODE=1`).

## Install and use

1. Write your keys in `J:\Reasonix Studio\data\home\.env`:

   ```ini
   GEMINI_API_KEY=AIza...
   GROQ_API_KEY=gsk_...
   ELEVENLABS_API_KEY=sk_...
   ```

   One key is enough to dictate; three keys mean three chances.

2. Close Reasonix Studio completely (tray icon → Quit).

3. Double-click **`mettre-a-jour.bat`**. It closes the app if needed, extracts the catalogue,
   compares it with the dictionary, applies, and verifies.

4. Reopen the app, then double-click **`verifier-cles.bat`**: it must announce **three
   entries** and a clean `.env`.

After the first launch, the keys live in `data\home\mic-keys.bin`; the lines disappear from
`.env`. To change a key later, write it in `.env` again and restart once.

## The microphone

Right-click the microphone button in the composer to open the settings panel.

| Provider | Model | Key | Transport | When to use it |
|---|---|---|---|---|
| **Gemini** | `gemini-3.5-flash-lite` (editable) | `AIza…` | `generateContent` | default; reformulates and punctuates well |
| **Groq** | `whisper-large-v3-turbo` | `gsk_…` | `POST /openai/v1/audio/transcriptions` | fast, generous free quota |
| **ElevenLabs** | `scribe_v2` (fixed) | `sk_…` | `POST /v1/speech-to-text` (batch) | best on noisy French speech |

The **Test API key** button tests the selected provider only: `GET /v1/user` for ElevenLabs
(no credit spent, no audio), a one-word generation for Gemini, the model list for Groq.

Dictation records, converts to 16 kHz mono WAV, sends, then inserts the text in the composer —
or sends the message directly if *automatic send* is checked.

## Key security

**What is done.** The three keys are encrypted by Electron's `safeStorage`, which on Windows is
DPAPI: the ciphertext is bound to your Windows account and this machine, and stored in
`data\home\mic-keys.bin`. The plain text lines are removed from `.env`, and the page never
receives a key — the decryption happens in the main process, behind a whitelist of three names.

**What that buys.** A copy of the folder, a sync client, a backup, a stolen disk image no longer
contain a usable key. Before this pack, reading `.env` in Notepad was enough.

**What it does not buy — read this.** The vault is **not** end-to-end encryption and **not** a
password manager:

| Limit | Why |
|---|---|
| Same Windows account, same machine | Any process running as you can ask DPAPI to decrypt the file, exactly as the app does |
| Memory | While the app runs, the keys are in clear text in the main process memory |
| No master password | There is no second factor: the account **is** the secret |
| Roaming | Copy `mic-keys.bin` to another machine or account and it will not decrypt — the keys are lost, not compromised. Write them in `.env` again |
| Panel input | A key typed in the panel is kept in memory for the session only; it is never written to disk |
| Upstream | The bridge lives in `app.asar`. A Reasonix Studio update removes it until the pack is applied again — during that window, the microphone cannot read the vault |

In short: it closes the "plain file on disk" hole, which was the real one. It does not make a
stolen, unlocked, logged-in session safe.

## Maintenance: the patch follows the app

Reasonix Studio updates replace `resources\frontend-next\` and `app.asar`. That is expected:
after each update the interface returns to English, the microphone disappears, and the keys
become unreadable until the pack is applied again.

The method does not contain a version number: it **reads** the version from `Reasonix Studio.exe`
(`FileVersion`), extracts the catalogue of the bundles actually loaded, and compares it with the
dictionary. When the upstream release adds strings, the engine refuses to apply anything, writes
`a-traduire.tsv`, and waits. Fill the `francais` column, run it again — nothing else to learn.

That is also why this repository will keep evolving: each upstream release can rename bundles,
add strings, or move a menu anchor. The pack is meant to be re-run, not frozen.

## Known limitations

| Limit | Detail |
|---|---|
| Built-in skills | The nine built-in skills (*explore*, *locate*, *review*…) keep their English description: it is compiled into `reasonix-studio-host.exe`, not stored in a file this pack can rewrite |
| No streaming dictation | ElevenLabs is used in batch mode: the text arrives after you stop, not while you speak |
| Windows only | The vault relies on DPAPI through Electron; the rest of the pipeline is portable in principle but untested elsewhere |
| Upstream churn | An update can break an anchor (`main.js`, `preload.js`, menu). The patcher refuses to install a broken file — it stops and says which anchor is missing |
| Quota | Gemini, Groq and ElevenLabs free tiers have limits; the pack does not bypass them |

## Repository layout

```
mettre-a-jour.bat              the double-click: apply everything
restaurer.bat                  roll back from a dated backup
verifier-cles.bat              vault state, never prints a key
config.bat                     paths and fallback language
normaliser-crlf.ps1            puts the .bat files back in CRLF (a LF .bat breaks `goto` silently)

dict/fr.json                   5 243 translations (Chinese source → French)
dict/literals.json             rules for the hard-coded label patcher
dict/skills-fr.json            French descriptions of the installed skills

tools/maj.py                   the engine: extract, compare, apply, verify
tools/patch252.py              dictionary + default language + start screen
tools/patch_literals.py        strings written directly in the bundles
tools/patch_asar252.py         native strings, context menu, vault bridge
tools/patch_skills.py          skill descriptions (frontmatter)
tools/asar_patches.json        the exact anchors and replacements for app.asar
tools/verify.mjs               sweep of every string of the build
tools/selftest.py              self-test on a copy of the application
tools/verifier-cles.py         vault state

Reasonix-Voice-Input-publish/  the microphone module and its installer
```

## Non-affiliation

Reasonix Studio is developed by the DeepSeek-Reasonix project. This repository is an
independent, unofficial work: it contains no code from the application, only patches applied to
a local copy the user already owns. Names and trademarks belong to their owners.

## License

MIT — see [LICENSE](LICENSE). The patched application keeps its own licence.
