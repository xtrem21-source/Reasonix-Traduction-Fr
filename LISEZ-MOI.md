# Francisation Reasonix Studio 2.47

> Patch de l'application installée. Réversible : chaque fichier modifié est sauvegardé dans `backups\`.

## Ce que fait ce paquet

| Étape | Contenu |
|---|---|
| Interface (`frontend-next`) | dictionnaire FR de **4 957 entrées**, injecté dans le bundle i18n réellement chargé ; le sélecteur de langue reçoit **Français** |
| Chaînes natives (`app.asar`) | page de démarrage, menu contextuel, menu du tray, dialogues de plantage, dialogue d'ancienne version |
| Écran de démarrage HTML | reconnaît `fr` au lieu de retomber sur l'anglais |

Le paquet **détecte** les fichiers à patcher au lieu de coder leurs noms en dur : il lit `index.html` pour trouver le bundle i18n courant, et cherche le bundle `Settings-*.js` qui propose zh/en. C'est ce qui permet de le rejouer après une mise à jour.

## Utilisation

```text
1. Fermer complètement Reasonix Studio
   (icône de la zone de notification → Quitter)
2. Double-cliquer Francisation_2.47.bat
3. Rouvrir Reasonix Studio
4. Paramètres → Apparence → Langue → Français
```

En cas d'échec, le `.bat` s'arrête et affiche la raison.

## Ce qui est traduit

- Toute l'interface : menus, sous-menus, réglages, infobulles, messages d'erreur, pages de paramètres ajoutées en 2.47 (exécutions planifiées, bac à sable, texte externe, aperçus de fichiers).
- Les cinq skills ajoutés et leurs descriptions d'interface.
- Les 10 chaînes natives listées plus haut.

## Ce qui ne l'est pas

| Élément | Pourquoi |
|---|---|
| Le noyau Go (CLI, TUI) | catalogue compilé dans le binaire, non modifiable sans reconstruire Go |
| Les notifications système | passent par le noyau, désactivées par défaut |
| Les réponses du modèle | elles suivent la langue de tes messages, pas ce réglage |

## Restauration

Les originaux sont dans `backups\`, nommés `<horodatage>__<type>__<fichier>`.
Recopie le fichier voulu à sa place :

| Sauvegarde | Destination |
|---|---|
| `*__i18n__i18n-*.js` | `…\resources\frontend-next\dist\assets\` |
| `*__settings__Settings-*.js` | idem |
| `*__index__index.html` | `…\resources\frontend-next\dist\` |
| `*__app.asar` | `…\resources\app.asar` |

## Après une mise à jour de Reasonix

Les bundles changent de nom : relance simplement `Francisation_2.47.bat`. Le script retrouve les nouveaux fichiers et les patche. Si un motif a changé, il s'arrête en le disant — il ne patch jamais à moitié.

## Contenu du paquet

```text
Reasonix-FR-2.47\
├─ Francisation_2.47.bat
├─ LISEZ-MOI.md
├─ dict\
│  ├─ en_dict_247.json      catalogue anglais/chinois extrait de 2.47
│  ├─ fr_dict_246.json      dictionnaire 2.46 réutilisé
│  ├─ fr_dict_247.json      dictionnaire final (4 957)
│  └─ parts\                lots de traduction
├─ tools\
│  ├─ patch247.py           patch frontend
│  ├─ patch_asar247.py      patch natif
│  ├─ translate247.py       outil de maintenance (API DeepSeek)
│  └─ asar_patches.json     motifs natifs extraits de 2.46
└─ backups\                 créé au premier passage
```
