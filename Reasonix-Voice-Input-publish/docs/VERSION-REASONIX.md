# Reasonix Studio — version inspectée

| Élément | Valeur |
|---|---|
| Version | **2.40.0** |
| `package.json` (asar) | `reasonix-studio-electron` 2.40.0 |
| Installation | `%LOCALAPPDATA%\Programs\Reasonix Studio` |
| Frontend | `resources\frontend-next\dist` |
| `app.asar` | 520 964 octets (main + preload) |
| `app.asar.unpacked` | absent |
| Hôte | `resources\bin\reasonix-studio-host.exe` |
| Renderer | `http://127.0.0.1:<port>/` (port variable) |

## Empreintes

| Fichier | Taille | SHA-256 |
|---|---|---|
| `index.html` | 13 312 o | `27343223A506E433CF8C15C5A557DD235FB5C745D214661D6CD5AA16F74C9DDE` |
| `assets/index-e5yng55N.js` | 720 112 o | `5C6435D445EDE088006C3857CB2092427B0BE7598298D744DE1D890CA0180553` |

## Sélecteurs

| Rôle | Sélecteur |
|---|---|
| Composeur | `textarea[data-action-keydown="session.send"][role="combobox"]` |
| Composeur actif | textarea visible/focalisé ; boutons cherchés dans son conteneur, pas dans toute la page (0.1.4) |
| Envoi | `button.btn.send[data-action="session.send"]` |
| Stop | `button.btn.stop[data-action="session.stop"]` |
| File | `queue.send-now`, `queue.cancel`, `queue.edit`, `queue.pause`, `queue.retry` |

## Stockage

Préfixe **`rx-`** obligatoire pour la persistance par le preload :
`rx-ocVoice.geminiKey`, `rx-ocVoice.model`, `rx-ocVoice.lang`, `rx-ocVoice.autoInsert`,
`rx-ocVoice.sendKeyword`, `rx-ocVoice.log`.

> Ces valeurs sont datées. Une mise à jour de Reasonix change le nom du bundle et souvent
> `index.html` : refaire le diff et revérifier les sélecteurs (voir `DEMARCHE.md`).
