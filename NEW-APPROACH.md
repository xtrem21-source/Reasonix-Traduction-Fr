# Two approaches in this repository

This repository now carries **two methods**, side by side. The old one has not been changed by a
single line: it stays where it is, with its scripts, archives and documentation. The new one lives
in [`pack-2.55/`](pack-2.55/).

| | Old method (2.46 → 2.52) | New method (2.55 and later) |
|---|---|---|
| Location | repository root (`scripts/`, `translations/`, `micro-winh/`, `Francisation_2.x.bat`) | [`pack-2.55/`](pack-2.55/) |
| Entry point | `Francisation_2.x.bat`, then `APPLIQUER-*.bat` as needed | **`mettre-a-jour.bat`** — one double-click does everything |
| Interface | Chinese → French dictionary injected into the bundle | same, plus a patcher for the text written directly in the bundles |
| Microphone | Gemini or Groq, `micro-winh/` module | Gemini, **Groq** and **ElevenLabs Scribe v2**, one key field visible |
| API keys | plain text in `.env` | **encrypted vault** (Windows DPAPI) in `data\home\mic-keys.bin` |
| Context menu | separate `MENU-REASONIX.bat` | included in the `app.asar` patch |
| Skills | not handled | descriptions translated (frontmatter of `SKILL.md`) |
| Verification | `verify.mjs` over the strings | same, plus the `app.asar` patch and the vault state |
| Rollback | `restaurer.bat` | same, plus `verifier-cles.bat` |

## What changed, concretely

1. **One gesture.** `mettre-a-jour.bat` chains: dictionary, hard-coded labels, microphone, native
   strings of `app.asar`, skill descriptions, then verification.
2. **Keys leave the file.** `GEMINI_API_KEY`, `GROQ_API_KEY` and `ELEVENLABS_API_KEY` move from
   `.env` to `mic-keys.bin`, encrypted by Windows. The page never receives a key. The limits of
   that vault are written plainly in [`pack-2.55/SECURITY.md`](pack-2.55/SECURITY.md) — it is not
   end-to-end encryption.
3. **Three providers instead of two**, including ElevenLabs in batch mode: the text arrives after
   you stop recording.
4. **The patch follows the version.** The method contains no version number: it reads
   `FileVersion` from `Reasonix Studio.exe`, extracts the catalogue of the bundles actually
   loaded, and refuses to apply anything when a translation is missing.

## Which one to pick

- **Reasonix Studio 2.55.0** → `pack-2.55/`, and nothing else.
- **Reasonix Studio 2.52.0 or earlier** → the old method, as it stands.
- **Translating into another language than French** → the old method remains the reference: it is
  the one carrying the generic pipeline (extract → translate → inject → verify).

The two do not stack: applying `pack-2.55` and then a `Francisation_2.x.bat` overwrites the pack
with the old flow. Pick one.

## What did not move

Nothing. `README`, `CHANGELOG`, `scripts/`, `translations/`, `micro-winh/`, the
`Francisation_2.x.bat` files, `MENU-REASONIX.bat`, `docs/`, `assets/` and the
`Reasonix-FR-2.49/2.50/2.52.zip` archives are exactly as they were. Only the top of both READMEs
gets a pointer to this file — no existing line was rewritten.
