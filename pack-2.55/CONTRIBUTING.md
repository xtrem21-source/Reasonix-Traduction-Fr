# Contributing

This pack repairs a third-party application after its updates. Contributions are welcome as long
as they keep the two rules that make it readable: **everything is bilingual**, and **nothing is
guessed**.

## What is useful

- **An upstream break**: a Reasonix Studio release that changes a bundle name, an anchor in
  `main.js`, `preload.js` or the context menu. Send the version (`FileVersion`) and the exact
  message from `mettre-a-jour.bat`.
- **A missing translation**: the engine writes `a-traduire.tsv` and applies nothing. Fill the
  `francais` column and open a pull request with the updated `dict/fr.json`.
- **A microphone problem**: provider, model, error message, and whether *Test API key* passed.
- **A wrong French string**: say which screen, quote the English, propose the French.

## What is not accepted

- **A guessed translation.** A missing string stops the run; do not fill it with a machine guess.
- **A version number in a script.** The version is read from `Reasonix Studio.exe`
  (`FileVersion`); nothing is hard-coded.
- **Generated files**: `logs/`, `backups/`, `tools/node_modules/`, `dict/etat.json`,
  `dict/catalog.json`, `a-traduire.tsv`. They are in `.gitignore` for that reason.
- **A key, a `mic-keys.bin`, an `.env`.** Never in an issue, a commit, or a screenshot.

## Before opening a pull request

1. `python tools/maj.py --no-apply` — must end with `OK - tout est conforme`.
2. `python tools/patch_skills.py --check` — must end with `a traduire : 0`, unless the pull
   request is precisely about that.
3. `python tools/selftest.py` — the pipeline replayed on a copy of the application.
4. If you changed `tools/asar_patches.json`: `python tools/patch_asar252.py --dry-run` must print
   `syntaxe : OK sur les 9 fichiers` and `verification du paquet : 4/4 marqueurs`.

## Style

- **Two languages, same content.** `README.md` / `README.fr.md`, `CHANGELOG.md` /
  `CHANGELOG.fr.md`, `SECURITY.md` / `SECURITY.fr.md`. A translation, not a summary.
- **Commit messages**: `type: what changed`, in the imperative, one line summary then a body if
  needed — `fix: read-env block must end with its anchor`.
- **Comments** explain *why*, in French, without accents in code paths that PowerShell 5.1 reads
  as ANSI (the `.ps1` files).
- **`.bat` files must stay CRLF.** `cmd.exe` computes label offsets assuming CRLF; a LF file makes
  `goto` jump too far **without any message**. `normaliser-crlf.ps1` fixes a whole pack.

## Reporting a security problem

Do not open a public issue. Describe it in `SECURITY.md` terms (step, version, log lines) and
assume the vault boundary is documented: a process running under the same Windows account can
decrypt `mic-keys.bin`. That is a known limit, not a vulnerability.
