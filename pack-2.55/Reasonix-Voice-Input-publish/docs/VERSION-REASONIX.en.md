# Reasonix Studio — inspected version

| Item | Value |
|---|---|
| Version | **2.40.0** |
| `package.json` (asar) | `reasonix-studio-electron` 2.40.0 |
| Install | `%LOCALAPPDATA%\Programs\Reasonix Studio` |
| Frontend | `resources\frontend-next\dist` |
| `app.asar` | 520,964 bytes (main + preload) |
| `app.asar.unpacked` | absent |
| Host | `resources\bin\reasonix-studio-host.exe` |
| Renderer | `http://127.0.0.1:<port>/` (random port) |

## Fingerprints

| File | Size | SHA-256 |
|---|---|---|
| `index.html` | 13,312 B | `27343223A506E433CF8C15C5A557DD235FB5C745D214661D6CD5AA16F74C9DDE` |
| `assets/index-e5yng55N.js` | 720,112 B | `5C6435D445EDE088006C3857CB2092427B0BE7598298D744DE1D890CA0180553` |

## Selectors

| Role | Selector |
|---|---|
| Composer | `textarea[data-action-keydown="session.send"][role="combobox"]` |
| Active composer | visible/focused textarea; buttons are looked up in its container, not the whole page (0.1.4) |
| Send | `button.btn.send[data-action="session.send"]` |
| Stop | `button.btn.stop[data-action="session.stop"]` |
| Queue | `queue.send-now`, `queue.cancel`, `queue.edit`, `queue.pause`, `queue.retry` |

## Storage

Use the **`rx-`** prefix so the preload persists the keys:
`rx-ocVoice.geminiKey`, `rx-ocVoice.model`, `rx-ocVoice.lang`, `rx-ocVoice.autoInsert`,
`rx-ocVoice.sendKeyword`, `rx-ocVoice.log`.

> These values are dated. An app update changes the bundle name and often `index.html`:
> diff and re-check the selectors (see `METHODOLOGY.md` / `DEMARCHE.md`).
