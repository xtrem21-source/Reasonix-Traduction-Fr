# Francisation Reasonix Studio 2.52

> Patch de l'application installée. Réversible : chaque fichier modifié est sauvegardé dans `work\backup\`.

## Ce que fait ce paquet

| Étape | Contenu |
|---|---|
| Interface (`frontend-next`) | dictionnaire FR de **5 146 entrées** — 100 % du catalogue du build 2.52 — injecté dans le bundle i18n réellement chargé ; le sélecteur de langue reçoit **Français** |
| Langue de repli | quand aucune langue n'est enregistrée, l'interface s'ouvre en **français** au lieu de retomber en anglais (`--default-lang fr\|en\|auto`) |
| Écran de démarrage HTML | reconnaît `fr` au lieu de retomber sur l'anglais |
| Libellés codés en dur | `Clé API`, `Jetons`, `Tours`, `CONNEXION AU MODÈLE`, `agent de code` |
| Chaînes natives (`app.asar`) | les ancres 2.49 s'appliquent toujours (11/11 vérifiés sur 2.52), mais le lanceur ne les exécute pas |

Le paquet **détecte** les fichiers à patcher au lieu de coder leurs noms en dur : il lit `index.html` pour trouver le bundle i18n courant, et le bundle `Settings-*.js` que le bundle principal charge réellement.

## Pourquoi la langue « ne tenait pas » avant la 2.52

| Maillon | Constat |
|---|---|
| `preload.js` | restaure les préférences `rx-*` depuis `window-prefs.json` ; `rx-lang` y revient **vide** |
| Origine de la page | le noyau écoute sur un **port local neuf à chaque lancement** : `localStorage` démarre vide |
| `i18n` | sans valeur enregistrée, la langue retombait sur celle de la machine — l'anglais |
| `uilang.js` (natif) | ne connaît que `zh` et `en` : il ne pouvait pas rétablir `fr` |

Résultat : choisir « Français » rechargeait la fenêtre… en anglais. La 2.52 fait résoudre une valeur vide vers le défaut configuré.

## Utilisation

```text
1. Fermer complètement Reasonix Studio
   (icône de la zone de notification → Quitter)
2. Double-cliquer Francisation_2.52.bat
3. Rouvrir Reasonix Studio
```

L'interface doit s'ouvrir en français, sans rien sélectionner.

En cas d'échec, le `.bat` s'arrête et affiche la raison.

Si Reasonix Studio n'est pas au chemin Windows standard (`%LOCALAPPDATA%\Programs\Reasonix Studio`), définis la variable avant de lancer :

```text
set "REASONIX_STUDIO_DIR=J:\Reasonix Studio"
Francisation_2.52.bat
```

Changer la langue de repli :

```text
set "REASONIX_UI_DEFAULT=en"
Francisation_2.52.bat
```

## Ce qui est traduit

- Toute l'interface : menus, sous-menus, réglages, infobulles, messages d'erreur, pages ajoutées jusqu'en 2.52 (historique paginé, compaction du contexte, cartes de fichiers, mise en veille, Wallpaper Engine, raccourcis clavier, facturation).
- Les descriptions des outils intégrés et les libellés anglais câblés dans les bundles.

## Ce qui ne l'est pas

| Élément | Pourquoi |
|---|---|
| Le noyau Go (CLI, TUI) | catalogue compilé dans le binaire, non modifiable sans reconstruire Go |
| Les notifications système | passent par le noyau, désactivées par défaut |
| Les réponses du modèle | elles suivent la langue de tes messages, pas ce réglage |
| Les mots-clés de recherche des réglages | tableaux `keywords:[…]`, jamais affichés |
| Les noms propres | Reasonix, DeepSeek, GitHub, Wallpaper Engine, Discord, WeChat… |

## Restauration

Les originaux sont dans `work\backup\`, nommés `<horodatage>__<type>__<fichier>`.
Recopie le fichier voulu à sa place :

| Sauvegarde | Destination |
|---|---|
| `*__i18n__i18n-*.js` | `…\resources\frontend-next\dist\assets\` |
| `*__settings__Settings-*.js` | idem |
| `*__labels__*.js` | idem |
| `*__index__index.html` | `…\resources\frontend-next\dist\` |

Ou automatiquement : `python scripts\patch252.py --restore`.

## Après une mise à jour de Reasonix

Les bundles changent de nom : relance simplement `Francisation_2.52.bat`. Le script retrouve les nouveaux fichiers et les patche. Si un motif a changé, il s'arrête en le disant — il ne patch jamais à moitié.

## Contenu du paquet

```text
Reasonix-Traduction-Fr\
├─ Francisation_2.52.bat     lanceur 2.52
├─ Francisation_2.50.bat     lanceur 2.50 (conservé)
├─ Francisation_2.49.bat     lanceur 2.49 (conservé)
├─ LISEZ-MOI.md
├─ translations\
│  └─ fr.json                dictionnaire (5 146 entrées)
├─ scripts\
│  ├─ patch252.py            patch frontend 2.52 + langue de repli
│  ├─ patch250.py            patch frontend 2.50 (conservé)
│  ├─ patch_asar247.py       patch natif 2.47 (conservé)
│  └─ …                      extraction, fusion, vérification
└─ work\                     créé au premier passage (ignoré par git)
```
