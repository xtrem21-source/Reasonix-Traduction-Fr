# Problems and solutions

> Reference table. Details and evidence are in [`JOURNAL.md`](JOURNAL.md) (FR, authoritative)
> and [`JOURNAL.en.md`](JOURNAL.en.md) (EN mirror). French version:
> [`PROBLEMS-SOLUTIONS.md`](PROBLEMS-SOLUTIONS.md).

## Inherited from the AiTron / AionUi base

| Problem | Cause | Fix |
|---|---|---|
| Renderer freeze after patching | the mic became its own “send” button; observer loop | exclude `#ocVoiceAnchor`/`#ocVoiceRoot` (`isOwnNode`), debounce 80 ms, `takeRecords()` |
| Mic over the send arrow in an old thread | send button wrapped in a 32 px `overflow:hidden` tooltip | `anchorTarget()` climbs to the real action row and inserts after the wrapper |
| Mic jumps left during generation | send button disappears; heuristic picked a left tool button | exclude left tool groups and the stop button; anchor next to `session.stop` |
| Mic misplaced in a narrow bar | no room beside the send button | float 6 px above, `position:fixed` in `<body>` so it stays clickable |
| Gemini key lost on restart | origin port changes; preload persists only `rx-*` | `rx-ocVoice.*` keys |
| Auto-send impossible while the agent works | send button disabled | AionUi: click the draft/queue button; Reasonix: retry ~2 s, then explicit error + clipboard |
| Message stays in the composer | button disabled at click time (upload/render) | 5 retries over ~2 s before giving up |
| No config/logs API in preload | module cannot read app config | key panel + `localStorage['rx-ocVoice.log']` + real key test |
| Settings panel off-screen | low window, panel measured before display | show before measure, `max-height: calc(100vh - 24px)`, `ensurePanelVisible()` |

## Reasonix Studio 2.40.0 specifics

| Problem | Cause | Fix / status |
|---|---|---|
| No useful asar for the UI | UI is plain `frontend-next\dist` | patch the plain folder: copy + one script tag |
| Unknown selectors | zh/en UI, generated classes | `data-action`: `session.send`, `session.stop`; composer `data-action-keydown="session.send"` |
| Composer is `readOnly` during generation | React state | `isVisible()` accepts `readOnly` |
| CSP / host headers | not documented | runtime-validated: Gemini fetch works |
| Mic permission | sandboxed renderer | runtime-validated |
| Send during generation | `session.send` becomes “插话” | interject validated; queue behavior depends on the app state |
| App update | `frontend-next` replaced | `REAPPLIQUER-MIC-REASONIX.bat` + `VERIFIER...` + journal |
| Mic disappears from the active chat | the module took the first `session.send` of the page; with two chats it anchored to the other one; during generation the active chat's send button is replaced by `session.stop` | scope the lookup to the active/visible composer, follow panes on `focusin`, anchor to `session.stop`, keep the mic visible during the transition (0.1.4) |
| No restore point | risk of no rollback | `PREPARER-SAUVEGARDE...` + `.bak` + `.sha256` + `old/`; `RESTAURER...`; verified before write |

## Update rule

When a new problem is found:

1. add it here with cause and fix;
2. add a dated entry in `JOURNAL.md` (and the English mirror);
3. update `README.fr.md` / `README.md` if the user procedure changes;
4. bump `CHANGELOG.md` / `CHANGELOG.fr.md`.
