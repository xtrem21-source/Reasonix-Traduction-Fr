> **DRAFT — adapt before posting.** Reddit's r/tauri is a technical audience that
> will notice a mismatch. Be upfront: the application patched here is an
> **Electron** app, and the post's real subject is the **method**, which ports to
> Tauri. Do not claim a Tauri app was tested — none was.

---

**Title:** Translating a bundled desktop UI by patching its frontend — method, and how it maps to Tauri

**Body:**

I built a small tool that translates the interface of a desktop app I use, and
the technique turned out to be framework-agnostic enough that I think this
subreddit will find the *method* more interesting than the app.

**The problem.** Many desktop apps bundle their frontend — `dist/assets/*.js`,
content-hashed and minified — and ship the UI strings *inside* it. If the app
only offers two languages and neither is yours, there is no supported way in.

**The observation.** In the app I looked at, every visible sentence was a
key/value pair in a plain object inside one bundle:

```js
var e={"查看大图：{alt}":`View image: {alt}`,关闭图片:`Close image`, ...}
```

The **key is the source-language string**, the value is the translation. A
missing key renders as the original, not a blank. That last property is the whole
trick: a partial dictionary degrades gracefully.

**The method**, in five steps:

1. **extract** — pull the keys out of the bundle in the *installed* app.
2. **translate** — produce `{key: value}` for your language. Any method; a model
   works, so does a human.
3. **merge/check** — assert that placeholders (`{n}`, `{name}`) survived and no
   key went missing.
4. **inject** — append your dictionary to the bundle, register the language code,
   and — this is the fiddly part — teach the language resolver and the in-app
   language selector that the language exists.
5. **verify** — load the *installed* file in Node and prove it translates.

Everything is string-patching with `assert exactly one occurrence`. A pattern
that no longer matches is reported and skipped, never guessed: that is what makes
it safe across app updates.

**Why this belongs here.** A Tauri app bundles its frontend too — it is the same
shape: a hashed `dist/` served to the webview, with strings baked in. The four
interesting problems are identical:

- content-hash filenames change every release ⇒ match by *pattern*, never by name;
- minification moves the code around ⇒ anchor on stable substrings;
- the language resolver is a hard-coded whitelist (`zh | en`) ⇒ you must extend
  it, not just add a dictionary;
- the language *selector* is a separate list in a different bundle ⇒ two files to
  patch, not one.

If you have a Tauri app with no i18n layer and an audience that does not read its
shipped language, this pipeline is a direct fit — and honestly, adding a real i18n
layer upstream is the better fix, which is why I say so in the repo.

**What I will not pretend.** The app I patched is Electron, not Tauri. I have not
run this against a Tauri build. The mapping above is by analogy from how Tauri
bundles its frontend, and I would rather say that plainly than imply otherwise.

**Repo:** https://github.com/xtrem21-source/Reasonix-Traduction-Fr — the method is
documented; the scripts are plain Python, no build step. It targets the Electron
desktop app of [DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)
(Reasonix Studio **2.40.0**). It is unofficial and unaffiliated with the app it
translates.

**Honest limits:** the strings I could *not* reach are the ones compiled into a
native binary (Go, in this case). Webview-frontend strings are reachable; native
strings are not, without rebuilding.

Happy to answer questions on the injection mechanics, or to hear from anyone
who has done the equivalent for a Tauri bundle.
