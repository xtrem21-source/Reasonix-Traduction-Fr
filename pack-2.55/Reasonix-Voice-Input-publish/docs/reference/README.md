# Reference — original index.html

**This file is not shipped in the public repository.** `ReasonixStudio-2.40.0-index.html` is a
copy of a third-party application file; the app's `package.json` has no license field, so the
repository does **not** redistribute it. The patch does not need it.

## Recreate it locally

```powershell
$fe = "$env:LOCALAPPDATA\Programs\Reasonix Studio\resources\frontend-next\dist"
Copy-Item "$fe\index.html" ".\docs\reference\ReasonixStudio-2.40.0-index.html"
```

Then compare with the installed file after an app update:

```powershell
Compare-Object (Get-Content $fe\index.html) (Get-Content .\docs\reference\ReasonixStudio-2.40.0-index.html)
```

## Version 2.40.0 fingerprint

- Size: 13,312 bytes
- SHA-256: `27343223A506E433CF8C15C5A557DD235FB5C745D214661D6CD5AA16F74C9DDE`
- No CSP meta tag; one `</body>` injection point.

The local backup `index.html.bak` (inside the app's `frontend-next\dist`) is the primary restore
point. The `old/` archive is a second copy. Neither is committed to this repository.
