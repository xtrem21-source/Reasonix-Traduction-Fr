> **DRAFT — adapt before posting.** Hacker News rewards precision and punishes
> marketing. Keep the title literal (no "any Electron app" overclaim), lead with
> the technical finding, and put the honest limits in the *first screen* of text —
> commenters will find them anyway, and volunteering them is what earns trust.

---

**Title:** Show HN: I translated an Electron app's UI by patching its own bundles (unofficial)

**URL:** <link to the repository>

**First comment (post this immediately as the author):**

The app is Reasonix Studio. Its interface ships in Chinese and English only, I
read neither well, and it is not open to upstream translations — so I read my own
installation and patched it.

Two things I think are worth your time.

**The finding that makes this possible.** The app does not verify the integrity of
its own archive. No `EnableEmbeddedAsarIntegrityValidation` fuse, no `asarIntegrity`
reference in the main process. That single fact is the difference between "you can
translate this" and "you cannot". I checked for it before writing a line of code,
and it should be the first thing anyone checks.

**What the strings actually are.** Not prose to edit. In the renderer, all the UI
text is one plain object inside a minified, content-hashed bundle, keyed by the
*source-language* string:

```js
var e={"查看大图：{alt}":`View image: {alt}`, ...}, h={zh:{},en:{...e,...}};
```

So a translation is a third dictionary plus telling a hard-coded `zh|en` resolver
that your language exists. Four small patches, and the one that actually bit me
was the persistence path: the app re-applied its own stored language on the next
launch and silently reverted my switch. A language you add is not added until the
app stops overwriting it.

**The discipline.** Every patch asserts its anchor occurs **exactly once**. A miss
is reported and skipped, never guessed. When the app updates and the minifier
shifts the code, you get a list of moved anchors instead of a corrupted bundle.
That is the whole reason I trust this across versions, and it is also why it is
version-bound: right now it is built for one specific release, and says so.

**The limits, up front:**

- **Tied to a version** (currently Reasonix Studio 2.40.0). Content-hashed bundle
  names and minified anchors move every release.
- **Web UI and Electron shell only.** The backend is Go, and its strings are
  *compiled into a 44 MB binary* — genuinely out of reach without rebuilding it.
  Its own source says that catalogue is CLI-surface, so the miss lands in the
  terminal, not the window — but it is a miss, and the README says so.
- **Windows-oriented** path handling; macOS/Linux untested.
- **French is the only finished translation.** The tool is a pipeline, not a
  French patch — that is the point — but I have only proven one language.

**On doing this at all.** The app is MIT, so I *may* redistribute parts of it. I
chose not to: no `app.asar`, no bundles, no binary. The tool runs on your own
installation and only the translation travels. And the README credits the authors,
carries their license verbatim, and states non-affiliation in the first screen.
If a maintainer told me to stop, I would.

Repo's here: https://github.com/xtrem21-source/Reasonix-Translate. It translates
the desktop UI of [DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)
(Reasonix Studio), and it is pinned to Reasonix Studio **2.40.0** — the build I
verified the patch anchors against. Unofficial, not affiliated with upstream. Ask
me anything about the injection mechanics — or tell me
why adding a real i18n layer upstream is the right fix, because honestly it is,
and that is exactly the thing these apps make impossible to contribute.

---

**Notes for the poster (delete before submitting):**

- Post between 8–10am US Eastern on a weekday for the best chance of staying on
  the front page; HN's ranking is time-sensitive.
- Do **not** ask for upvotes anywhere. It is against the guidelines and it is
  visible.
- Be present in the thread for the first few hours. The best comments will be
  people who know Electron internals better than you do — say so, and learn from
  them.
- If someone points out that an upstream i18n contribution is better: agree. It
  is. The reason it does not exist is the interesting part of the discussion.
