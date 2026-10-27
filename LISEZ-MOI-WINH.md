# Reasonix-FR-2.52 + Win+H — 26 octobre 2026

Ce dossier est la **copie exacte** de `Reasonix-FR-2.52`, plus la version corrigée du micro.
Rien n'a été supprimé ni écrasé : les fichiers d'origine sont intacts, les ajouts sont à côté.

## Ce qui a été ajouté

| Dossier | Fichier | Rôle |
|---|---|---|
| `micro-winh\` | `voice-input.js` | le module complet tel qu'il fonctionne ce soir (Groq, deux clés, case Windows, garde-fou anti-double envoi, masquage pendant un tour) |
| | `patch_asar_menu.py` + `APPLIQUER-MENU-FR.bat` | francisent le **menu clic droit** (Annuler, Copier, Coller, Tout sélectionner, Ajouter à la conversation…) |
| | `winh.ps1` | envoie `Win+H` : `SCANCODE + EXTENDEDKEY`, `wVk=0`, `wScan=0x5B`, un événement par appel |
| | `dicter.bat` | lance `winh.ps1` sans fenêtre |
| | `patch_asar_sendkey2.py` | réinjecte le pont `shell:send-key` dans `app.asar` |
| | `APPLIQUER-SENDKEY.bat` | ferme Studio, applique le pont, relance par l'Explorateur |
| `Reasonix-Voice-Input-publish\src\` | `voice-input.20261026-groq-winh.js` | le même module, déposé **à côté** de `voice-input.reasonix.js` sans le remplacer |

## Les trois corrections de la soirée

| Correction | Symptôme qu'elle supprime |
|---|---|
| `spawn(..., { detached: false })` | PowerShell démarrait puis sortait en code 0 **sans exécuter le script** |
| `KEYEVENTF_SCANCODE | KEYEVENTF_EXTENDEDKEY` + `wScan = 0x5B` | un `h` littéral s'écrivait au lieu du raccourci |
| un seul `Win+H` toutes les 3 s, et la case ne déclenche plus rien | deux envois rapprochés **refermaient** la dictée (les « 2 secondes ») |

## Ce que fait ce micro aujourd'hui

| Voie | État | Usage |
|---|---|---|
| **Groq** (`whisper-large-v3-turbo`) | réponse immédiate | la dictée du quotidien |
| **Gemini** | lent (4 s et plus) | secours |
| **Windows H** (case à cocher) | session de 10-15 s, une phrase | insertion courte |

Les deux clés sont stockées séparément (`rx-ocVoice.geminiKey`, `rx-ocVoice.groqKey`) : changer de
fournisseur n'efface jamais l'autre. Le bouton du panneau teste **la clé active**.

## Après une mise à jour de Studio

1. `micro-winh\voice-input.js` → copier dans `J:\Reasonix Studio\resources\frontend-next\dist\`
   (valable pour la 2.52 ; si les noms changent, servir de référence).
2. `micro-winh\APPLIQUER-SENDKEY.bat` → double-clic, Studio fermé.
3. `micro-winh\winh.ps1` et `dicter.bat` doivent rester à `J:\Reasonix\dev\voix-winh\`.
