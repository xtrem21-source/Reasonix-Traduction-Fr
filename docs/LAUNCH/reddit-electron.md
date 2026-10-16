> **DRAFT — adapt before posting.** r/electron knows `app.asar` well; the parts
> worth getting right are the **integrity finding** and the **"assert exactly
> one"** discipline. Keep it technical, skip the marketing.

---

**Title:** Patching `app.asar` and a minified renderer bundle to add a UI language (write-up)

**Body:**

I needed an Electron app in a language it does not ship, so I read my own
installation and patched it. Two files, two different problems. Notes in case
someone else needs this.

**Finding 1 — no `asar` integrity check.** Before doing anything, I checked
whether the app validates its own archive. It does not: no
`EnableEmbeddedAsarIntegrityValidation` fuse, no `asarIntegrity` reference in the
main-process code. Without that, `app.asar` is just a file you can unpack, edit,
and repack. Worth checking first — with the fuse on, this whole approach is off
the table.

```
npx asar extract resources/app.asar work/asar_orig
# … edit src/*.js …
npx asar pack work/asar_fr resources/app.asar.new
```

I keep the pristine extraction as the reference, patch a copy, repack, then
verify by extracting the result again and diffing the file list against the
original. 52 files in, 52 files out; only the ones I touched differ.

**Finding 2 — the renderer strings are a dictionary in one bundle.** The web UI
is minified, but the i18n layer is a plain object, keyed by the *source* string:

```js
var e={"查看大图：{alt}":`View image: {alt}`, ...}, h={zh:{},en:{...e,...}};
```

So translating is not editing prose — it is appending a third dictionary and
telling the resolver it exists. Four small patches:

1. the translate function consults my dictionary when the language is mine;
2. the resolver accepts my language code (it was a hard-coded `zh|en` whitelist);
3. `<html lang>` handles it;
4. the persisted choice is not overwritten by the app's own config on next launch
   — **this one bit me**: the app re-applied its stored language and silently
   undid my switch until I guarded it.

Plus the language selector, which lives in a *different* bundle and has its own
hard-coded list. Two files, not one — easy to miss.

**The discipline that makes it safe: assert exactly one match.** Every patch is a
string replacement that first asserts the anchor occurs exactly once. A miss is
reported and skipped. When the app updates and the minifier shifts the code, the
tool tells you which anchor moved instead of corrupting the bundle. I would
rather have a loud skip than a silent wrong edit.

**Native surfaces are ordinary strings again.** The main process
(`src/starting.js`, `editmenu.js`, …) has startup text, context-menu roles, and
error dialogs — but *not* as an i18n object, just inline `en`/`zh` pairs. Those
are translated by adding a third branch. The tray menu was the exception: its
labels come from a backend process at runtime, so I reconstructed them on the
Electron side from the counters the backend sends.

**What stayed English.** The backend's strings are compiled into a native binary
and are genuinely out of reach without rebuilding it. Its own source comments say
it is a CLI-surface catalogue, so the miss is small — but it is a miss, and I say
so in the README rather than pretending the translation is total.

**Verify, don't assume.** The last step loads the *installed* bundle in Node with
a minimal `localStorage`/`navigator` stub, boots it in the target language, and
calls the translate function on real keys. It is about 40 lines and it is the
only reason I trust the result.

Repo (unofficial, unaffiliated): https://github.com/xtrem21-source/Reasonix-Translate.
It targets the Electron desktop app of
[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix), on Reasonix
Studio **2.40.0**. But the transferable bit is the shape:
dictionary-in-bundle, whitelist resolver, second bundle for the selector, assert
exactly one.
