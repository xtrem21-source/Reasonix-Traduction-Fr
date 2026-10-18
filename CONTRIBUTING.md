# Contributing to Reasonix-Traduction-Fr

Thanks for helping. This project exists so that people who don't read Chinese or
English can use Reasonix Studio. The most valuable contribution is **a
translation**, but bug reports and fixes are welcome too.

By participating, you agree to keep the project's [non-affiliation
notice](README.md#non-affiliation) and the [MIT license](LICENSE) intact.

## The upstream project

This tool translates
**[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)** — the
project behind the *Reasonix Studio* desktop app — maintained by **Huahui Yu**
and its contributors, and licensed under MIT.

We are **not affiliated with it**. Nothing here is endorsed by upstream, and
nothing we do should be reported to them as a bug of theirs. The version our
patch targets is tracked under
[Supported versions](README.md#supported-versions).

---

## Ways to contribute

| I want to… | Go to |
|---|---|
| Translate the interface into my language | [Adding a new language](#adding-a-new-language) |
| Improve the existing French translation | [Improving a translation](#improving-a-translation) |
| Report a bug | [Reporting a bug](#reporting-a-bug) |
| Suggest a feature | [Suggesting a feature](#suggesting-a-feature) |
| Support a newer Reasonix version | [Supporting a new version](#supporting-a-new-version) |

---

## Adding a new language

This is the main workflow. Replace `xx` with your language code (`es`, `de`,
`ja`…).

### 1. Fork and clone

```bash
git clone https://github.com/xtrem21-source/Reasonix-Traduction-Fr.git
cd Reasonix-Traduction-Fr
```

### 2. Install Reasonix Studio

You need the application installed — the tool reads the strings from your own
copy. Note your exact version (**Settings → About**, or the `version` field in
`resources/app.asar`).

### 3. Extract the source strings

```bash
python3 scripts/extract_i18n.py
```

This writes the extracted keys to `work/extracted/`. That folder is generated and
never committed.

### 4. Build your dictionary

```bash
cp translations/fr.json translations/xx.json
```

Then translate the **values**, keeping the **keys** untouched. Details that
matter:

- **Keys are the Chinese source strings.** They are the lookup keys — editing one
  breaks the string it points to.
- **Preserve every `{placeholder}`.** `{n}`, `{name}`, `{alt}`, … must appear
  unchanged, and normally in the same order. Two helpers check this:
  ```bash
  python3 scripts/check_placeholders.py
  ```
- **Partial is fine.** A missing key falls back to Chinese, never to a blank.
  Translate the screens you care about first and open the PR — you can extend it
  later.
- **Keep it plain.** These are interface labels, not prose. Stay concise and
  match the tone of `translations/fr.json`.
- **Do not translate product names**: Reasonix, WeChat, Alipay, Douyin, QQ,
  GitHub, VS Code, …

### 5. Verify locally, then inject

```bash
python3 scripts/merge_fr.py            # checks missing / unknown keys
python3 scripts/check_placeholders.py  # checks placeholders
python3 scripts/inject_fr.py           # applies it to your installation
python3 scripts/verify_installed.py    # proves the installed bundle translates
```

Restart Reasonix Studio and switch the language to confirm it looks right.

### 6. Open a pull request

- One language per PR. Name the file exactly `translations/xx.json`.
- In the PR description, say **which Reasonix Studio version** you tested against.
- If your translation is partial, say so — that's fine.

---

## Improving a translation

Typos, awkward wording, better terminology — all welcome. Edit
`translations/xx.json`, re-run the two checkers, and open a PR. Small, focused
PRs are easiest to review.

---

## Reporting a bug

Open an issue and include:

- **What you did** — the exact commands you ran.
- **What you expected** and **what happened** — paste the real output, don't
  summarise it.
- **Your Reasonix Studio version** (critical: the injector is version-bound).
- **Your OS and Python/Node versions.**
- **Whether it still happens on a clean install** of Reasonix Studio, if you can
  test that.

If the injector reported a pattern it could not find, paste that line — it names
the exact anchor that moved, which is the single most useful clue for a version
fix.

---

## Suggesting a feature

Open an issue describing the problem before the solution. Especially useful:

- Porting to **macOS/Linux** (see `scripts/paths.py`).
- Handling a **newer Reasonix version**.
- Extending the native (`asar`) translation to more surfaces.

---

## Supporting a new version

When Reasonix Studio updates, the minified bundles change and the patch anchors
move. To fix it:

1. Extract from the new version and find where each anchor moved.
2. Update the patterns in `scripts/inject_fr.py` (web bundles) and
   `scripts/patch_asar.py` (native strings).
3. Re-run the injector — it tells you explicitly which patterns it could not
   find, so you can iterate.
4. Update the version table in `README.md` → **Supported versions**.

Please keep the injector's "assert exactly once" behaviour: never replace a
"best effort" match for a failure. A skipped patch is recoverable; a wrong one is
not.

---

## Git workflow

**Branches**

- `main` is always the working state.
- Branch names: `lang/<code>` for translations, `fix/<short-name>` for fixes,
  `feat/<short-name>` for features. Example: `lang/es`, `fix/inject-anchor`.

**Commits**

Use the imperative mood and a short prefix when it helps:

```
lang: add Spanish translation
fix: handle Reasonix 2.41 bundle hashes
docs: clarify partial translation behaviour
```

Keep a commit to one idea. Do not commit generated files — `work/`, `sources/`,
`tools/`, `node_modules/`, backups, or any Reasonix artifact (the `.gitignore`
already excludes them; check `git status` before committing).

**Pull requests**

- Base branch: `main`.
- Rebase or merge `main` in before opening, so the diff is only your change.
- Say what you tested and how. "It compiles" is not a test for a translation —
  say that you injected it and saw the interface in your language.
- One concern per PR.

**What we will not merge**

- Any Reasonix binary or bundle (`app.asar`, `*.js` bundles, the Go binary).
- Source files copied from the Reasonix repository.
- Changes that remove the non-affiliation notice or the Reasonix license notice.

---

## Adding a second language: what changes in the scripts

Out of the box, the scripts speak French in a few places (`fr`, `Français`,
`__FR`). To support `xx`, either edit those constants or pass the language
through. The places to look are noted in
[`docs/WORKFLOW-TRANSLATE.md`](docs/WORKFLOW-TRANSLATE.md). A future improvement
is to move these into a single language parameter — contributions welcome.

---

## Code of conduct

Be decent. Assume good faith. This project's whole point is to include people who
are currently excluded — that spirit applies to the issue tracker too.
