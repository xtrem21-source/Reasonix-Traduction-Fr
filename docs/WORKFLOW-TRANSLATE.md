# Translating Reasonix Studio — the full workflow

This is the detailed version of the "Adding a new language" section in the
README. It assumes no prior knowledge of the codebase.

Replace `xx` with your language code (`es`, `de`, `ja`, `pt-BR`…).

---

## Overview

```
 ① extract      ② translate       ③ merge       ④ inject      ⑤ verify
 read the        write your        combine &     apply to      prove it
 strings         dictionary        check         the app       works
```

You can stop after ② and still open a useful pull request — a partial
translation is fine.

---

## ① Fetch and extract the strings

```bash
python3 scripts/fetch_sources.py   # downloads the upstream catalogs into sources/
python3 scripts/extract_i18n.py    # writes the keys into work/extracted/
```

**What it does.** Reasonix Studio's interface text lives in minified bundles, but
its translation *sources* are plain TypeScript catalogs in the upstream
repository: a dictionary whose **keys are the Chinese source text** and whose
**values are the English translation**. `fetch_sources.py` downloads those
catalogs into `sources/`; `extract_i18n.py` then writes the keys, grouped by
screen, into `work/extracted/` — one JSON file per group.

The catalogs are **fetched, not shipped**: `sources/` is gitignored and never
redistributed. This is the one step that needs the network.

**Output.** `work/extracted/en.json`, `en_settings.json`, `en_kernel.json`, and
so on. Together they hold roughly **3 900 keys**.

**If it fails.** Make sure Reasonix Studio is installed and that `paths.py`
found it. Set `REASONIX_STUDIO_DIR` to the install folder if it lives somewhere
unusual.

---

## ② Translate

Produce a file `translations/xx.json` — a flat JSON object mapping each **Chinese
key** to **your** translation.

```json
{
  "重命名聊天": "Renommer la conversation",
  "聊天标题": "Titre de la conversation",
  "留空以恢复自动标题": "Laisser vide pour restaurer le titre automatique"
}
```

### Rules

1. **Never change the keys.** They are the lookup keys. A translated key simply
   stops matching, and the string falls back to Chinese.
2. **Keep every `{placeholder}`** (`{n}`, `{name}`, `{alt}`, `{who}`, …)
   unchanged. These are substituted at runtime. `scripts/check_placeholders.py`
   fails the build if one is lost, renamed, or added.
3. **Do not translate product names**: Reasonix, WeChat, Alipay, Douyin, QQ,
   GitHub, VS Code, …
4. **Be concise.** These are labels and short sentences, not prose. Match
   `translations/fr.json` for tone.
5. **Empty source → empty value.** If a source string is empty, leave the value
   empty.
6. **Partial is allowed.** Anything you omit falls back to Chinese.

### Starting from scratch

```bash
python3 scripts/next_batch.py 60       # the next 60 strings still missing
python3 scripts/next_batch.py --file en_usage.json   # one group, in full
```

This prints the English values (the keys are implicit in the order). Translate
them and save the array.

### Using the optional AI helper

```bash
python3 scripts/probe_api.py           # checks that an API key is available
python3 scripts/translate_api.py --batch 30
```

This uses the DeepSeek API by default and needs a key in Reasonix's own `.env`
(`%APPDATA%\reasonix\.env`, variable `DEEPSEEK_API_KEY`). It writes arrays into
`work/fr_parts/`, aligned with `work/extracted/`. **It is entirely optional** —
any translation method works, including doing it by hand. Review machine output
before shipping it; the tooling checks structure, not meaning.

---

## ③ Merge and check

```bash
python3 scripts/merge_fr.py            # combine the pieces
python3 scripts/check_placeholders.py  # verify {placeholders}
```

`merge_fr.py` reports:

- **missing** — keys present in the extracted catalogue but absent from your
  translation;
- **unknown** — keys in your translation that are not in the catalogue (usually a
  typo, or a string that moved between versions);
- **conflicts** — two pieces giving different values for the same key.

`check_placeholders.py` compares, for every entry, the set of `{placeholders}` in
the source against the set in your translation, and **exits non-zero** if they
differ. This is the check that keeps `{n}` from becoming `{nombre}`.

> Both scripts currently write and read French paths (`fr_parts/`,
> `fr_dict.json`). For another language, see
> [Using this for another language](#using-this-for-another-language) below.

---

## ④ Inject

Two independent injections, in this order.

### 4a. The web interface

```bash
python3 scripts/inject_fr.py
```

This edits the interface bundle in your installation:

- appends your dictionary to the bundle and registers it in the language table;
- teaches the language resolver your language code;
- adds your language to the in-app language selector.

It asserts every anchor it patches matches **exactly once**, skips (and reports)
any it cannot find, and copies each file to `work/backup/` before touching it.

### 4b. The native shell (optional, needs Node)

```bash
python3 scripts/setup_asar_orig.py     # first time only: a pristine reference
python3 scripts/patch_asar.py          # produce the translated copy
python3 scripts/repack_asar.py         # rebuild app.asar
python3 scripts/verify_asar.py         # check the rebuild
python3 scripts/install_asar.py        # install it, with backup
```

This translates the startup page, the right-click menu, the error dialogs, the
legacy-install dialog, and the tray menu — the parts drawn by the Electron shell
rather than the web page.

Without Node, skip 4b: the web interface is still translated.

---

## ⑤ Verify

```bash
python3 scripts/verify_installed.py        # the web interface
python3 scripts/verify_asar_installed.py   # the native shell
```

These read the **installed** files — not your working copies — and confirm the
translation is really present and the files are still valid JavaScript. A
`VERDICT: OK` here means the change is in place, not merely that a script ran.

Then restart Reasonix Studio and switch the language in **Settings → Language**.

---

## Using this for another language

The scripts speak French in a handful of places. To add `xx`, the constants to
change are:

| Where | What |
|---|---|
| `scripts/inject_fr.py` | the language code (`fr`) and display name (`Français`) |
| `scripts/inject_fr.py` | the global-object name (`__FR`) |
| `scripts/patch_asar.py` | the language code checks in the native files |
| `scripts/merge_fr.py`, `next_batch.py` | the `fr_parts/` and `fr_dict.json` filenames, if you want a second language alongside French |

A cleaner design — one `--lang` parameter threaded through every script — is a
wanted contribution. Until then, the honest description is: **the pipeline is
generic, the invocation is French-named.**

---

## Recovering from a mistake

Nothing is destructive:

- every replaced file is copied to `work/backup/<timestamp>__<name>` **before**
  being overwritten;
- to restore the installed `app.asar`, run `python3 scripts/install_asar.py --restore`;
- to restore a web bundle, copy the matching `work/backup/*__i18n-*.js` back over
  the installed file;
- updating or reinstalling Reasonix Studio also restores the originals.

---

## Quick reference

```bash
# Read the strings from the installed application
python3 scripts/extract_i18n.py

# See what still needs translating
python3 scripts/next_batch.py 60

# Check your work
python3 scripts/merge_fr.py
python3 scripts/check_placeholders.py

# Apply it
python3 scripts/inject_fr.py
python3 scripts/setup_asar_orig.py && \
  python3 scripts/patch_asar.py && \
  python3 scripts/repack_asar.py && \
  python3 scripts/verify_asar.py && \
  python3 scripts/install_asar.py

# Prove it landed
python3 scripts/verify_installed.py
python3 scripts/verify_asar_installed.py
```
