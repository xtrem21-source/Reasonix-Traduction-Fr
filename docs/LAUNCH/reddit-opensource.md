> **DRAFT — adapt before posting.** r/opensource cares about *why* and *how you
> behave as a maintainer*, not about the app. Lead with the exclusion problem, be
> explicit about what you will and will not merge, and do not oversell.

---

**Title:** I built an unofficial translation layer for an app that only ships two languages — here is the licensing reasoning and what I refuse to redistribute

**Body:**

I use a desktop app whose interface exists in Chinese and English only. I do not
read either well enough to be comfortable. The app is closed to contributors — I
cannot add a translation upstream — so I did the only thing left: built a local
translation layer, and then thought hard about whether I was allowed to publish
it.

This post is mostly about that second part, because I suspect others hit the same
wall and, like me, are not sure where the line is.

**The situation.**

- The application is licensed **MIT**.
- MIT lets me use, modify, and redistribute — *with* attribution and the license
  text.
- But "I am allowed" is not the same as "this is the right thing to ship".

**What I decided to redistribute:** only my own code (a translation pipeline, in
plain Python) and my own translation (a JSON dictionary of ~3 900 strings).

**What I refuse to redistribute**, even though MIT would permit some of it:

- the application's archive (`app.asar`),
- its JavaScript bundles,
- its native binary.

Two reasons, and I want to be honest that the second matters more than the first:

1. **Attribution gets murky.** Once I ship a *modified* bundle, the artifact is
   part mine and part theirs, and a user cannot tell where one stops.
2. **It is not my work to hand out.** The app is actively developed. If I ship a
   modified copy, I create a fork by accident — one that goes stale, that I have
   not tested, and that competes with the original for the user's trust.

So the tool **operates on the user's own installation, on their machine**. It
never copies the application anywhere. The only thing that travels is the
translation, which is mine, and the code, which is mine.

**The mechanism, in one paragraph.** The app is an Electron application whose UI
strings live in a minified, content-hashed bundle as a dictionary keyed by the
source-language string. The pipeline extracts those keys, lets you translate
them, injects your dictionary back into your own copy, and verifies the result by
loading the installed file. A missing key falls back to the original language
rather than to a blank, so a partial translation is genuinely useful — which
matters, because 3 900 strings is a lot to ask of one volunteer.

**The maintainer decisions I made before publishing**, written down because they
are the part most projects skip:

- **Non-affiliation, stated up front.** Not in small print. First screen. The
  project is not the vendor's and must never be mistaken for it.
- **Their license text, verbatim, in my repo.** `LICENSE-REASONIX.md`. MIT asks
  for this; it is also just correct.
- **Refuse merge requests that add their code.** A contribution guideline that
  only lists what you *want* is half a guideline. Mine says: no binaries, no
  bundles, no files copied from their repository. Ever.
- **A pre-publish checklist** that includes an automated scan for accidentally
  committed proprietary artifacts — because one bad `git add .` is all it takes.
- **Say what is broken.** The native binary's strings are unreachable without
  rebuilding it. The README says so plainly instead of implying the translation
  is complete.

**Why I am posting this here rather than just shipping it.** If you maintain
software and someone asks for a language you cannot support, the answer is not
always "send a PR" — sometimes the code cannot accept one. I would like to see
more maintainers say *that* out loud, and more people treat "I did it locally"
as a legitimate response instead of a workaround. This is my attempt at both.

The tool is a demonstration in French, but it is not French-specific: it is a
pipeline anyone can point at their own language.

Repo: https://github.com/xtrem21-source/Reasonix-Translate. It translates the UI
of [DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix) (Reasonix
Studio), pinned to **2.40.0**; unofficial and unaffiliated. Happy to talk about
the licensing line specifically — I am not
certain I drew it in the *right* place, only that I drew it in a place I can
defend.
