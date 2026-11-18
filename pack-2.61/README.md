# Reasonix Studio — French patches

Patches for **Reasonix Studio 2.61** (Windows x64): French interface, voice
dictation, attachment paste fix, and an OpenCode bridge.

This repository contains **no binaries** and **no personal data**. It ships the
scripts that apply the patches to an official archive you download yourself.

---

## What the scripts fix

| # | Patch | What changes |
|---|---|---|
| 1 | **French localisation** | interface and menus in French (`dict/`) |
| 2 | **Voice dictation** | microphone button; keys are read from `data/home/.env` first, with the encrypted vault as fallback |
| 3 | **Attachment paste** | a pasted screenshot (Ctrl+V) is no longer rejected: an extension is derived from the MIME type |
| 4 | **OpenCode bridge** | `data/dev/opencode-bridge/`, exposes OpenCode's free models as a local provider |

---

## Requirements

- Windows 10/11 x64
- **Node.js 18 or newer** (`node --version`)
- The official **`ReasonixStudio-windows-amd64.zip`**, version **2.61**

Download it from the upstream project's releases. The patches target that
version: on another one the replacement anchors will not match, and the scripts
stop without writing anything.

---

## Procedure

```bat
REM 1. Extract the official archive into a working folder
REM    (you get Reasonix-Studio-2.61/ with Reasonix Studio.exe, resources/, ...)

REM 2. Move into the scripts folder
cd tools

REM 3. Apply the patches, in this order
node patch-lang.mjs   "..\Reasonix-Studio-2.61"
node patch-asar.mjs   "..\Reasonix-Studio-2.61"
node micro.mjs        "..\Reasonix-Studio-2.61\resources\frontend-next\dist" "..\dist"
node pont-micro.mjs   "..\Reasonix-Studio-2.61"
node patch-collage.mjs "..\Reasonix-Studio-2.61"

REM 4. Copy the OpenCode bridge
xcopy /E /I /Y "..\opencode-bridge" "..\Reasonix-Studio-2.61\data\dev\opencode-bridge"

REM 5. Re-zip the Reasonix-Studio-2.61 folder
```

Every script is **idempotent**: run again on an already patched folder it writes
nothing and says so. A missing or ambiguous anchor makes it fail without
changing anything.

---

## What these patches do not do

- They modify **neither** `en.json` **nor** upstream translation files: French
  comes from the dictionary and targeted replacements.
- They **never** touch personal data (`data/home/.env`, `data/home/projects`,
  `data/home/memory`).
- They bypass no protection: if a file is read-only or locked, the script fails
  and reports it.

---

## API keys

Voice dictation uses a Groq key (`GROQ_API_KEY`) and, depending on your setup,
Gemini or ElevenLabs. Two ways to provide it:

1. **In `data/home/.env`** — recommended, and what the patch reads first;
2. in the encrypted vault `data/home/mic-keys.bin`, created by earlier versions
   of the bridge (kept as a fallback so nothing is lost).

The vault is encrypted by Electron (`safeStorage`, DPAPI on Windows): readable
only by your Windows account, on this machine.

---

## Credits and licence

- Reasonix Studio is developed by **esengine**, released under the **MIT**
  licence. This repository is affiliated neither with the author nor with the
  upstream project.
- The patches are provided as is, without warranty. Test them on a scratch
  installation before applying them to your main one.
