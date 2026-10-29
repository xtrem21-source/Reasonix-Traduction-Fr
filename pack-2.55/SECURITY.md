# Security policy

## What this pack touches

| Surface | What happens | Reversible |
|---|---|---|
| `resources\frontend-next\dist` | `index.html` gets one `<script>` tag and a few attributes; `voice-input.js` is added; bundles are rewritten in place for hard-coded labels | Yes — `index.html.bak` and dated backups |
| `resources\app.asar` | Repacked with French native strings, the context menu, and two IPC bridges (`readEnv`, `sendKey`) | Yes — the original archive is copied to `backups/<timestamp>__app.asar` before replacement |
| `<app>\data\home\.env` | Lines for the three microphone keys are **removed** once they are in the vault | Only from your own copy of the file — keep one if you need it |
| `<app>\data\home\mic-keys.bin` | Created: the three keys, encrypted by Windows DPAPI | Delete it and write the keys in `.env` again |
| `<app>\data\home\skills\*\SKILL.md` | The `description` of the frontmatter is rewritten in French; the body is untouched | Yes — `SKILL.md.avant-fr` |

Nothing else is read or written. The pack never opens `config.toml`, sessions, memory, or the
credentials file of the application.

## How the API keys are stored

1. You write the keys in `.env` (plain text, as the application itself expects them).
2. At the first start after the patch, the microphone asks the main process for each key.
3. The main process reads the named line from `.env`, encrypts it with Electron `safeStorage`
   (DPAPI on Windows), writes `mic-keys.bin`, then **removes that line from `.env`**.
4. On later starts, the key is decrypted from `mic-keys.bin` and handed to the page — never the
   reverse: the page cannot ask for a name that is not in the whitelist
   (`GEMINI_API_KEY`, `GROQ_API_KEY`, `ELEVENLABS_API_KEY`).

A key typed in the settings panel is kept **in memory for the session only** and is never written
to disk.

## Threat model — what the vault does and does not protect

**Protected**

- A copy of the folder, a backup, a sync client, a stolen disk image: `mic-keys.bin` is
  ciphertext, bound to your Windows account and machine.
- The page (renderer): it never sees the vault file and cannot ask for an arbitrary variable.
- Logs: no key is ever logged; `verifier-cles.bat` prints names, never values.

**Not protected**

| Limit | Consequence |
|---|---|
| Same Windows account, same machine | Any process running as you can call DPAPI and decrypt the file, exactly as the app does |
| Process memory | While Reasonix Studio runs, the keys are in clear text in the main process memory |
| No master password | There is no second factor. The account **is** the secret |
| Portable media | Copying `mic-keys.bin` elsewhere yields nothing (it will not decrypt) — but the copy is not a backup either |
| Neighbouring files | `.env` keeps the other providers' keys in clear text; this pack only moves the three it needs |
| Upstream update | Replacing `app.asar` removes the bridge until the pack is applied again; during that window, the vault is unreadable |

**Bottom line.** The vault closes the real hole: before this pack, reading `.env` in Notepad was
enough to steal the keys. It does **not** make a stolen, unlocked, logged-in session safe, and it
is not end-to-end encryption or a password manager.

## Recommendations

- Use keys dedicated to dictation, with spending limits on the provider side.
- Rotate them if the machine is shared or leaves your hands.
- Keep a copy of the keys somewhere safe **before** the first migration: the pack deletes them
  from `.env`.
- Treat the Windows session as the real secret: lock the screen, use an account password.

## Reporting a problem

Open an issue in this repository with: the Reasonix Studio version (`FileVersion` of
`Reasonix Studio.exe`), the step that failed, and the relevant `logs/journal.log` lines. Never
paste a key, and never paste the contents of `mic-keys.bin`.

## The pack will keep changing

Reasonix Studio updates replace `frontend-next\` and `app.asar`, and may rename bundles or move
the anchors this pack relies on. The patcher refuses to install a file it cannot parse, and says
which anchor is missing. Security fixes and upstream compatibility will therefore arrive as new
versions of this pack, not as patches to the application.
