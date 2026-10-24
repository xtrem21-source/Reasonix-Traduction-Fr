# Francisation Reasonix Studio 2.49

> Patch de l'application installée. Réversible : chaque fichier modifié est sauvegardé dans `backups\`.

## Ce que fait ce paquet

| Étape | Contenu |
|---|---|
| Interface (`frontend-next`) | dictionnaire FR de **5 034 entrées**, injecté dans le bundle i18n réellement chargé ; le sélecteur de langue reçoit **Français** |
| Écran de démarrage HTML | reconnaît `fr` au lieu de retomber sur l'anglais |
| Chaînes natives (`app.asar`) | **non portées en 2.49** — l'étape existe pour 2.46 et 2.47 seulement |

Le paquet **détecte** les fichiers à patcher au lieu de coder leurs noms en dur : il lit `index.html` pour trouver le bundle i18n courant, et cherche le bundle `Settings-*.js` qui propose zh/en. C'est ce qui permet de le rejouer après une mise à jour.

## Utilisation

```text
1. Fermer complètement Reasonix Studio
   (icône de la zone de notification → Quitter)
2. Double-cliquer Francisation_2.50.bat
3. Rouvrir Reasonix Studio
4. Paramètres → Apparence → Langue → Français
```

En cas d'échec, le `.bat` s'arrête et affiche la raison.

Si Reasonix Studio n'est pas au chemin Windows standard (`%LOCALAPPDATA%\Programs\Reasonix Studio`), définis la variable avant de lancer :

```text
set "REASONIX_STUDIO_DIR=J:\Reasonix Studio"
Francisation_2.50.bat
```

## Ce qui est traduit

- Toute l'interface : menus, sous-menus, réglages, infobulles, messages d'erreur, pages de paramètres ajoutées jusqu'en 2.49 (exécutions planifiées, bac à sable, texte externe, aperçus de fichiers).
- Les cinq skills ajoutés et leurs descriptions d'interface.

## Ce qui ne l'est pas

| Élément | Pourquoi |
|---|---|
| Le noyau Go (CLI, TUI) | catalogue compilé dans le binaire, non modifiable sans reconstruire Go |
| Les notifications système | passent par le noyau, désactivées par défaut |
| Les réponses du modèle | elles suivent la langue de tes messages, pas ce réglage |
| Les surfaces natives (`app.asar`) en 2.49 | l'étape n'a pas encore été portée depuis 2.47 |

## Restauration

Les originaux sont dans `backups\`, nommés `<horodatage>__<type>__<fichier>`.
Recopie le fichier voulu à sa place :

| Sauvegarde | Destination |
|---|---|
| `*__i18n__i18n-*.js` | `…\resources\frontend-next\dist\assets\` |
| `*__settings__Settings-*.js` | idem |
| `*__index__index.html` | `…\resources\frontend-next\dist\` |

## Après une mise à jour de Reasonix

Les bundles changent de nom : relance simplement `Francisation_2.50.bat`. Le script retrouve les nouveaux fichiers et les patche. Si un motif a changé, il s'arrête en le disant — il ne patch jamais à moitié.

## Contenu du paquet

```text
Reasonix-Traduction-Fr\
├─ Francisation_2.50.bat     lanceur 2.49
├─ Francisation_2.47.bat     lanceur 2.47 (conservé)
├─ LISEZ-MOI.md
├─ translations\
│  └─ fr.json                dictionnaire (5 034 entrées)
├─ scripts\
│  ├─ patch249.py            patch frontend 2.49
│  ├─ patch247.py            patch frontend 2.47 (conservé)
│  ├─ patch_asar247.py       patch natif 2.47 (conservé)
│  └─ …                      outils d'extraction et de vérification
└─ backups\                  créé au premier passage
```
