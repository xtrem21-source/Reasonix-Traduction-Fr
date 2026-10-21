# Applications supportées / Supported apps

## Français

Le module a été **porté sur quatre applications**. La méthode est la même ; seuls les
sélecteurs, le stockage et le preload changent.

| Application | Interface | Type de patch | État |
|---|---|---|---|
| **[Reasonix Studio 2.40.0](https://github.com/esengine/DeepSeek-Reasonix)** | `resources\frontend-next\dist` (plain) | copie de `voice-input.js` + une balise `<script>` | **porté et validé** (micro, clé, envoi, file) |
| **[Cline Desktop](https://github.com/cline/cline)** | application Electron | même module + sélecteurs | **porté** ; ancrage à ajuster |
| **[Open Cowork](https://github.com/open-cowork/open-cowork)** | application Electron | même module + sélecteurs | **porté** (base d'origine) |
| **[AionUi 2.2.2](https://github.com/iOfficeAI/AionUi)** | `resources\app.asar` | repack asar avec `--unpack-dir` / `--unpack`, préservation de `app.asar.unpacked` | **porté et validé** sur Windows |

**Ce n'est pas une contrainte :** il n'y a que **quelques petits réglages d'ancrage** dans la
fenêtre de chat (position à côté ou au-dessus de la flèche d'envoi). Le reste du module est
identique.

### Le gros avantage : Gemini plutôt que Win+H

| Critère | Gemini via le module | Dictée Windows (Win+H) |
|---|---|---|
| Précision | **nettement meilleure** : contexte, phrases longues | correcte sur des phrases simples |
| Ponctuation / majuscules | gérées par le modèle | irrégulières |
| Langues | multilingue | dépend des packs installés |
| Termes techniques / noms propres | meilleur contexte | plus approximatif |
| Hors ligne | non (Internet + clé gratuite) | oui |
| Coût | palier gratuit Gemini | inclus dans Windows |

C'est le cœur du module : **une dictée de qualité**, plus fiable que Win+H pour les messages
réels, sans dépendre du moteur local de Windows.

**La méthode en 8 étapes** : repérer le composeur, l'envoi et l'arrêt ; déterminer si l'UI est
plain ou dans un asar ; adapter le stockage et le preload ; ancrer le micro ; vérifier ; garder
un retour arrière ; documenter. Voir [`METHODOLOGY.md`](METHODOLOGY.md) (EN) /
[`DEMARCHE.md`](DEMARCHE.md) (FR).

## English

The module has been **ported to four applications**. The method is the same; only selectors,
storage and preload APIs change.

| App | UI | Patch type | State |
|---|---|---|---|
| **[Reasonix Studio 2.40.0](https://github.com/esengine/DeepSeek-Reasonix)** | `resources\frontend-next\dist` (plain) | copy `voice-input.js` + one `<script>` tag | **ported and validated** (mic, key, send, queue) |
| **[Cline Desktop](https://github.com/cline/cline)** | Electron app | same module + selectors | **ported**; anchoring to adjust |
| **[Open Cowork](https://github.com/open-cowork/open-cowork)** | Electron app | same module + selectors | **ported** (original base) |
| **[AionUi 2.2.2](https://github.com/iOfficeAI/AionUi)** | `resources\app.asar` | asar repack with `--unpack-dir` / `--unpack`, preserve `app.asar.unpacked` | **ported and validated** on Windows |

**This is not a constraint:** only a **few small anchoring adjustments** are needed in the
chat window (position beside or above the send arrow). The rest of the module is identical.

### The big advantage: Gemini rather than Win+H

| Criterion | Gemini via the module | Windows dictation (Win+H) |
|---|---|---|
| Accuracy | **significantly better**: context, long sentences | fine on simple sentences |
| Punctuation / casing | handled by the model | irregular |
| Languages | multilingual | depends on installed packs |
| Technical terms / proper nouns | better context | more approximate |
| Offline | no (Internet + free key) | yes |
| Cost | Gemini free tier | included in Windows |

This is the core of the module: **high-quality dictation**, more reliable than Win+H for real
messages, without relying on the local Windows engine.

**The 8-step method**: locate the composer/send/stop, determine plain vs asar, adapt storage
and preload, anchor the mic, verify, keep a rollback, document. See
[`METHODOLOGY.md`](METHODOLOGY.md) (EN) / [`DEMARCHE.md`](DEMARCHE.md) (FR).
