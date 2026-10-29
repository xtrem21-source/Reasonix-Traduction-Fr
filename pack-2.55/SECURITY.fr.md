# Politique de sécurité

## Ce que le pack touche

| Surface | Ce qui se passe | Réversible |
|---|---|---|
| `resources\frontend-next\dist` | `index.html` reçoit une balise `<script>` et quelques attributs ; `voice-input.js` est ajouté ; les bundles sont réécrits sur place pour les libellés en dur | Oui — `index.html.bak` et sauvegardes datées |
| `resources\app.asar` | Reconstruit avec les chaînes natives françaises, le menu contextuel et deux ponts IPC (`readEnv`, `sendKey`) | Oui — l'archive d'origine est copiée dans `backups/<horodatage>__app.asar` avant remplacement |
| `<app>\data\home\.env` | Les lignes des trois clés du micro sont **retirées** une fois les clés dans le coffre | Seulement depuis votre copie du fichier — gardez-en une si besoin |
| `<app>\data\home\mic-keys.bin` | Créé : les trois clés, chiffrées par Windows (DPAPI) | Supprimez-le et réécrivez les clés dans `.env` |
| `<app>\data\home\skills\*\SKILL.md` | La `description` du frontmatter est réécrite en français ; le corps reste intact | Oui — `SKILL.md.avant-fr` |

Rien d'autre n'est lu ni écrit. Le pack n'ouvre jamais `config.toml`, les sessions, la mémoire ni
le fichier d'identifiants de l'application.

## Comment les clés API sont rangées

1. Vous écrivez les clés dans `.env` (en clair, comme l'application les attend).
2. Au premier démarrage après le patch, le micro demande chaque clé au processus principal.
3. Le processus principal lit la ligne demandée dans `.env`, la chiffre avec le `safeStorage`
   d'Electron (DPAPI sous Windows), écrit `mic-keys.bin`, puis **retire cette ligne de `.env`**.
4. Aux démarrages suivants, la clé est déchiffrée depuis `mic-keys.bin` et remise à la page —
   jamais l'inverse : la page ne peut pas demander un nom absent de la liste blanche
   (`GEMINI_API_KEY`, `GROQ_API_KEY`, `ELEVENLABS_API_KEY`).

Une clé tapée dans le panneau de réglages reste **en mémoire pour la session** et n'est jamais
écrite sur disque.

## Modèle de menace — ce que le coffre protège, et ce qu'il ne protège pas

**Protégé**

- Une copie du dossier, une sauvegarde, un client de synchronisation, une image de disque volée :
  `mic-keys.bin` est du chiffré, lié à votre compte Windows et à votre machine.
- La page (renderer) : elle ne voit jamais le fichier du coffre et ne peut pas demander une
  variable arbitraire.
- Les journaux : aucune clé n'est journalisée ; `verifier-cles.bat` affiche des noms, jamais des
  valeurs.

**Non protégé**

| Limite | Conséquence |
|---|---|
| Même compte Windows, même machine | Tout processus lancé sous votre compte peut appeler DPAPI et déchiffrer le fichier, exactement comme le fait l'application |
| Mémoire du processus | Tant que Reasonix Studio tourne, les clés sont en clair dans la mémoire du processus principal |
| Aucun mot de passe maître | Il n'y a pas de second facteur. Le compte **est** le secret |
| Support amovible | Copier `mic-keys.bin` ailleurs ne donne rien (il ne se déchiffrera pas) — mais la copie n'est pas une sauvegarde non plus |
| Fichiers voisins | `.env` garde les clés des autres fournisseurs en clair ; ce pack ne déplace que les trois dont il a besoin |
| Mise à jour amont | Remplacer `app.asar` supprime le pont jusqu'à ce que le pack soit réappliqué ; pendant cette fenêtre, le coffre est illisible |

**En résumé.** Le coffre ferme le vrai trou : avant ce pack, lire `.env` dans le Bloc-notes
suffisait à voler les clés. Il ne rend **pas** une session volée, déverrouillée et connectée
inoffensive, et ce n'est ni du chiffrement de bout en bout ni un gestionnaire de mots de passe.

## Recommandations

- Utilisez des clés dédiées à la dictée, avec des limites de dépense côté fournisseur.
- Faites-les tourner si la machine est partagée ou sort de vos mains.
- Gardez une copie des clés en lieu sûr **avant** la première migration : le pack les supprime
  de `.env`.
- Traitez la session Windows comme le vrai secret : verrouillez l'écran, protégez le compte.

## Signaler un problème

Ouvrez une *issue* dans ce dépôt avec : la version de Reasonix Studio (`FileVersion` de
`Reasonix Studio.exe`), l'étape qui a échoué, et les lignes utiles de `logs/journal.log`. Ne
collez jamais une clé, et jamais le contenu de `mic-keys.bin`.

## Le pack continuera d'évoluer

Les mises à jour de Reasonix Studio remplacent `frontend-next\` et `app.asar`, et peuvent renommer
des bundles ou déplacer les ancres sur lesquelles ce pack s'appuie. Le patcheur refuse d'installer
un fichier qu'il ne peut pas analyser, et dit quelle ancre manque. Les correctifs de sécurité et
la compatibilité amont arriveront donc comme de nouvelles versions de ce pack, pas comme des
rustines appliquées à l'application.
