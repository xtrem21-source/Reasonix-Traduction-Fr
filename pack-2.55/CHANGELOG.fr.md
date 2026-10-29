# Journal des versions

Les changements notables de ce pack sont documentés ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/) ; la version suit celle de
Reasonix Studio visée.

## [2.55.0] — 2026-10-29

Première publication. Cible **Reasonix Studio 2.55.0** (Windows amd64).

### Ajouté

- **Interface française, mesurée.** Un dictionnaire de 5 243 entrées injecté dans le bundle
  réellement chargé, plus un patcheur pour les textes écrits directement dans les bundles.
  Vérification sur 2.55.0 : **5 205 / 5 205 chaînes couvertes, 0 erreur, aucun libellé codé en
  dur laissé sans traduction**.
- **Coffre à clés chiffré.** `GEMINI_API_KEY`, `GROQ_API_KEY` et `ELEVENLABS_API_KEY` quittent
  `.env` pour `data\home\mic-keys.bin`, chiffré par Windows (DPAPI) via le `safeStorage`
  d'Electron. La page ne reçoit jamais une clé : le déchiffrement a lieu dans le processus
  principal, derrière une liste blanche de trois noms. `verifier-cles.bat` donne l'état du coffre
  sans jamais afficher une clé. Les limites sont écrites dans [SECURITY.fr.md](SECURITY.fr.md).
- **Migration non destructive.** Le pont fusionne avec le coffre existant au lieu de le
  remplacer : ajouter une troisième clé ne peut plus effacer les deux premières.
- **Micro à trois fournisseurs.** Gemini (`gemini-3.5-flash-lite`), Groq
  (`whisper-large-v3-turbo`) et **ElevenLabs Scribe v2** (`POST /v1/speech-to-text`, batch). Un
  seul champ de clé visible à la fois, sélecteur dans le panneau, « Tester la clé API » qui ne
  teste que le fournisseur choisi — `GET /v1/user` pour ElevenLabs, sans consommer de crédit.
- **Menu contextuel en français.** `app.asar` est repatché : écran de démarrage, dialogues, zone
  de notification, menu contextuel, et les ponts `readEnv`/`sendKey`.
- **Descriptions de skills en français.** Sept skills installés reçoivent une `description`
  française dans le frontmatter de leur `SKILL.md` ; le contenu et les références sont intacts.
  Les neuf skills intégrés gardent leur description anglaise, compilée dans le binaire du noyau.
- **Retour arrière et auto-test.** `restaurer.bat` restaure chaque fichier depuis une sauvegarde
  datée ; `tools/selftest.py` rejoue le pipeline sur une copie de l'application.

### Modifié

- Le moteur lit la version de l'application dans `Reasonix Studio.exe` (`FileVersion`) au lieu de
  la coder en dur : aucun numéro de version dans les scripts.
- Une traduction manquante arrête le passage **avant** toute écriture et produit
  `a-traduire.tsv` ; le patch ne devine jamais une chaîne absente.

### Corrigé

- Le bloc `read-env` du patch asar se terminait sans son ancre, ce qui supprimait la ligne
  d'ouverture de `shell:open-external` et rendait `main.js` inanalysable — tout le patch natif
  était refusé en silence sur la 2.55. Le bloc se termine désormais par l'ancre qu'il remplace.
- Le panneau du micro ne masquait les champs de clé inutilisés qu'à son ouverture : un panneau
  créé avant tout réglage montrait les trois clés à la fois. Groq et ElevenLabs sont maintenant
  masqués dès le HTML, l'état est recalculé à la création du panneau, et un fournisseur inconnu
  retombe sur Gemini.
- `Write-Log 'a' + b + 'c'` dans l'installeur passait `+` comme couleur et interrompait le script
  après la copie ; la concaténation est parenthésée.

### Notes

- Les mises à jour de Reasonix Studio remplacent `frontend-next\` et `app.asar` : l'interface
  repasse en anglais et le micro disparaît jusqu'à ce que le pack soit réappliqué. C'est attendu.
- ElevenLabs est utilisé en mode batch : le texte arrive après l'arrêt, pas pendant que vous
  parlez.
