# Pre-publication checklist

Run through this **before** making the repository public. Each line is something
to verify, not to assume.

---

## 1. Licensing and attribution

- [ ] `LICENSE` exists and names this project (MIT), with the current year.
- [ ] `LICENSE-REASONIX.md` contains the **verbatim** MIT text of Reasonix,
      including `Copyright (c) 2026 Reasonix Contributors`.
- [ ] `README.md` credits **DeepSeek-Reasonix** and its maintainer **Huahui Yu**,
      and links to <https://github.com/esengine/DeepSeek-Reasonix>.
- [ ] `README.md` states **non-affiliation** explicitly ("not affiliated with,
      endorsed by, or sponsored by").
- [ ] `README.fr.md` carries the same credits and non-affiliation notice.
- [ ] `CONTRIBUTING.md` repeats the non-affiliation requirement **and** links to
      the upstream project.
- [ ] Each of the 5 drafts in `docs/LAUNCH/` names **DeepSeek-Reasonix**, links to
      the upstream repository, and states the target version.
- [ ] Both READMEs explain how to **check the installed version** before applying
      the patch, and that `2.40.0` is not the latest upstream.

## 2. No Reasonix code in the repository

Verify each of these is **absent** from the tree that will be committed:

- [ ] No `app.asar` or `app_fr.asar`.
- [ ] No minified JavaScript bundles (`i18n-*.js`, `Settings-*.js`, …).
- [ ] No Go binary (`reasonix-studio-host.exe`, `cua-driver.exe`).
- [ ] No `go_messages_en.json` (derived from the Go binary).
- [ ] No `sources/` directory (files fetched from the Reasonix repository).
- [ ] No `work/backup/`, `work/asar_orig/`, `work/asar_fr/` (they hold Reasonix
      code copies).

*How to check:* the automated scan in §6, plus `git status --porcelain` in §7.

## 3. Repository hygiene

- [ ] `.gitignore` covers: `work/`, `sources/`, `tools/`, `node_modules/`,
      `backup/`, `asar_orig/`, `asar_fr/`, `app_fr.asar`,
      `go_messages_en.json`, `extracted/`, `fr_parts/`, `__pycache__/`, `.env`.
- [ ] `__pycache__/` folders are not present.
- [ ] No `.env` file, and no API key anywhere in the tree.
- [ ] No absolute user paths (`C:\Users\...`) in any committed file.
- [ ] No temporary or scratch folders (`_scratch/`).

## 4. Documentation accuracy

- [ ] `README.md` is in **English** and is the primary entry point.
- [ ] `README.fr.md` is in **French** and matches the English version in content.
- [ ] Both READMEs name the **supported version** (Reasonix Studio **2.40.0**)
      in a dedicated section.
- [ ] Both READMEs describe how to **add a new language**.
- [ ] Both READMEs list the **known limitations** honestly.
- [ ] `CHANGELOG.md` has a `0.1.0` entry dated today.
- [ ] Every relative link in the READMEs resolves to a file that exists.
- [ ] `docs/` files referenced from the READMEs all exist.

## 5. The tool actually works

- [ ] `python3 scripts/extract_i18n.py` succeeds on a real installation.
- [ ] `python3 scripts/inject_fr.py` applies cleanly (all anchors match once).
- [ ] `python3 scripts/verify_installed.py` returns `VERDICT: OK`.
- [ ] `python3 scripts/verify_asar_installed.py` returns `VERDICT: OK`.
- [ ] `python3 scripts/check_placeholders.py` exits 0 on `translations/fr.json`.
- [ ] Reasonix Studio, restarted, shows the interface in the target language,
      and the language appears in **Settings → Language**.

## 6. Automated scan: zero proprietary artefacts

Run the scan (it walks the publishable tree and reports anything that looks like
Reasonix code or a leftover):

```bash
python3 scripts/scan_repo.py        # if present, else use the command below
```

Or without the helper — the scan is a single command:

```powershell
# Windows PowerShell: report any suspicious file in the publishable tree
Get-ChildItem -Recurse -File | Where-Object {
  $_.Name -match '\.asar$|\.exe$|go_messages|i18n-.*\.js$|Settings-.*\.js$' -or
  $_.FullName -match '\\work\\|\\sources\\|\\node_modules\\|__pycache__\\'
} | Select-Object FullName
```

- [ ] The command above returns **nothing** (or only `work/`-generated files you
      have already gitignored).

## 7. The commit contains what you think it does

```bash
cd Reasonix-Traduction-Fr
git init
git add .
git status --porcelain
```

- [ ] The listed files are exactly the intended set: READMEs, licenses, docs,
      `scripts/`, `translations/fr.json`, `.gitignore`.
- [ ] **Nothing** under `work/`, `sources/`, `node_modules/`, `tools/`, or any
      backup appears.
- [ ] `git ls-files | wc -l` gives a number that matches your expectation.

Then, before the first push:

```bash
git add -A
git commit -m "Initial release v0.1.0"
git remote add origin https://github.com/xtrem21-source/Reasonix-Traduction-Fr.git
git push -u origin main
```

## 8. On GitHub, after pushing

- [ ] The repository **description** is set to:
      *"Unofficial translation toolkit for DeepSeek-Reasonix (Reasonix Studio):
      translate its desktop UI into any language. Ships a complete French
      translation."*
- [ ] The **topics** are set: `reasonix`, `deepseek-reasonix`, `translation`,
      `i18n`, `localization`, `electron`, `desktop-app`, `french`, `francais`,
      `language-pack`, `unofficial`, `python`.
      (Deliberately **no** `tauri`: the target application is Electron, so the
      topic would be misleading.)
- [ ] A **license** is detected by GitHub (it reads `LICENSE`).
- [ ] If you enable **Issues**, the blank issue template asks for the Reasonix
      version — that is the first thing you will need.
- [ ] The repository does **not** publish a release containing any Reasonix
      binary.

## 9. Announcements

- [ ] Each text in `docs/LAUNCH/` has been re-read and adapted to its platform
      (they are drafts, not copy-paste).
- [ ] Any claim in an announcement is one you can back with this repository.
- [ ] The non-affiliation notice appears in every announcement.

---

## Sign-off

| Item | Date | By |
|---|---|---|
| Licensing (§1–2) | | |
| Hygiene (§3–4) | | |
| Works (§5) | | |
| Scan clean (§6–7) | | |
| Published (§8) | | |
| Announced (§9) | | |
