# Démarche — réinspecter et réappliquer après une mise à jour

> **Principe** : l'interface de Reasonix Studio est un dossier plain
> (`resources\frontend-next\dist`). Une mise à jour remplace ce dossier : le patch disparaît.
> La méthode consiste à **réinspecter les sélecteurs**, **tester le patcher sur une copie**,
> puis **réappliquer** et consigner l'opération dans le journal.

## 0. Règles

1. Ne pas fermer Reasonix Studio pour patcher : le patcher écrit sur disque, puis on recharge
   (`Ctrl+R`) ou on relance.
2. Toujours garder `index.html.bak` et une copie dans `old/`.
3. Tester le patcher sur une **copie** de `index.html` avant de toucher l'installation réelle.
4. Ne jamais modifier `app.asar` : ce n'est pas nécessaire ici.
5. Consigner chaque essai dans [`JOURNAL.md`](JOURNAL.md) (ajout seul).

## 1. Identifier la version et les chemins

```powershell
$app = Join-Path $env:LOCALAPPDATA 'Programs\Reasonix Studio'
Get-Content "$app\resources\app.asar" -TotalCount 0   # (facultatif)
$fe  = Join-Path $app 'resources\frontend-next\dist'
Get-ChildItem $fe
Get-FileHash "$fe\index.html" -Algorithm SHA256
```

Comparer `index.html` avec `docs/reference/ReasonixStudio-2.40.0-index.html` :

```powershell
code --diff "$fe\index.html" ".\docs\reference\ReasonixStudio-2.40.0-index.html"
```

## 2. Revérifier les sélecteurs dans le bundle

Le bundle principal est `assets\index-*.js` (le nom change à chaque build).

```powershell
$js = Get-ChildItem "$fe\assets\index-*.js" | Select-Object -First 1
Select-String -Path $js.FullName -Pattern 'data-action="session.send"|data-action-keydown="session.send"|className:`btn send`|data-action="session.stop"' -AllMatches
```

Vérifier aussi que le composeur est toujours un `<textarea>` :

```powershell
Select-String -Path $js.FullName -Pattern 'textarea.*session.send|role:`combobox`' -AllMatches
```

Si les noms changent :
- `findInput()` → nouveau sélecteur du textarea ;
- `findSubmitButton()` → nouveau sélecteur du bouton d'envoi ;
- exclure le bouton d'arrêt ;
- vérifier `data-running` (interjection) et les actions `queue.*`.

Mettre à jour `src/voice-input.reasonix.js`, puis :

```powershell
node --check .\src\voice-input.reasonix.js
```

## 3. Tester le patcher sur une copie

```powershell
$tmp = Join-Path $env:TEMP 'reasonix-patch-test'
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory $tmp | Out-Null
Copy-Item "$fe\index.html" $tmp
.\scripts\apply-patch.ps1 -FrontendDir $tmp -ScriptPath .\src\voice-input.reasonix.js -Force
Select-String -Path "$tmp\index.html" -Pattern 'voice-input.js'
.\scripts\apply-patch.ps1 -FrontendDir $tmp -Check -ScriptPath .\src\voice-input.reasonix.js
.\scripts\apply-patch.ps1 -FrontendDir $tmp -Rollback
(Get-FileHash "$tmp\index.html").Hash -eq (Get-FileHash "$fe\index.html").Hash
Remove-Item $tmp -Recurse -Force
```

Attendu : tag présent, hash identique à la source, rollback qui restaure l'original.

## 4. Appliquer et vérifier dans l'application

1. `REAPPLIQUER-MIC-REASONIX.bat` (ou `apply-patch.ps1 -Force`).
2. Recharger (`Ctrl+R`) / relancer Reasonix Studio.
3. `VERIFIER-MIC-REASONIX.bat` → `html tagged = True`, `voice-input.js present = True`,
   `hash matches source = True`.
4. Clic droit sur le micro → clé Gemini → **Enregistrer** → **Tester la clé Gemini**.
5. Dicter un message court, un long, avec pièce jointe, pendant une génération.
6. En cas d'échec, lire `localStorage['rx-ocVoice.log']` (DevTools → Console) :

```js
copy(localStorage['rx-ocVoice.log'])
```

## 5. Diagnostic des cas connus

| Symptôme | Piste |
|---|---|
| Micro absent | `index.html` non rechargé ; tag absent ; CSP ; erreur JS (DevTools Console) |
| Micro mal placé | sélecteur d'envoi changé ; `anchorTarget` à adapter |
| Micro à gauche/à droite pendant la génération | le bouton d'envoi change (`data-running`, `session.stop`) ; exclure le stop |
| Envoi auto impossible | bouton grisé (upload/rendu) ; le module retente 2 s ; sinon copie/erreur |
| Message pendant génération | `session.send` peut interjecter ; vérifier la file native (`queue.*`) |
| Clé perdue au redémarrage | les clés doivent commencer par `rx-` (préfixe `rx-ocVoice.*`) |
| `fetch` Gemini bloqué | CSP de l'hôte ; tester depuis la Console |

## 6. Journal

Ajouter une entrée datée dans [`JOURNAL.md`](JOURNAL.md) :

```
## AAAA-MM-JJ
- HH:MM — version Reasonix, sélecteurs vérifiés, patch appliqué/rollback, résultat.
```

C'est cette trace qui permet de repartir vite après une mise à jour.
