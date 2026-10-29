# Deux approches dans ce dépôt

Ce dépôt contient maintenant **deux méthodes**, côte à côte. L'ancienne n'a pas été modifiée
d'une ligne : elle reste à sa place, avec ses scripts, ses archives et sa documentation. La
nouvelle est dans [`pack-2.55/`](pack-2.55/).

| | Ancienne méthode (2.46 → 2.52) | Nouvelle méthode (2.55 et après) |
|---|---|---|
| Emplacement | racine du dépôt (`scripts/`, `translations/`, `micro-winh/`, `Francisation_2.x.bat`) | [`pack-2.55/`](pack-2.55/) |
| Point d'entrée | `Francisation_2.x.bat`, puis `APPLIQUER-*.bat` selon le besoin | **`mettre-a-jour.bat`** — un seul double-clic fait tout |
| Interface | dictionnaire chinois → français injecté dans le bundle | idem, plus la réécriture des textes écrits en dur dans les bundles |
| Micro | Gemini ou Groq, module `micro-winh/` | Gemini, **Groq** et **ElevenLabs Scribe v2**, un seul champ de clé visible |
| Clés API | en clair dans `.env` | **coffre chiffré** (Windows DPAPI) dans `data\home\mic-keys.bin` |
| Menu contextuel | `MENU-REASONIX.bat` séparé | inclus dans le patch `app.asar` |
| Skills | non traité | descriptions traduites (frontmatter des `SKILL.md`) |
| Vérification | `verify.mjs` sur les chaînes | idem, plus le contrôle du patch `app.asar` et l'état du coffre |
| Retour arrière | `restaurer.bat` | idem, plus `verifier-cles.bat` |

## Ce qui a changé, concrètement

1. **Un seul geste.** `mettre-a-jour.bat` enchaîne : dictionnaire, libellés en dur, micro,
   chaînes natives de l'`app.asar`, descriptions des skills, puis vérification.
2. **Les clés sortent du fichier.** `GEMINI_API_KEY`, `GROQ_API_KEY` et `ELEVENLABS_API_KEY`
   passent de `.env` à `mic-keys.bin`, chiffré par Windows. La page ne reçoit jamais une clé.
   Les limites de ce coffre sont écrites noir sur blanc dans
   [`pack-2.55/SECURITY.fr.md`](pack-2.55/SECURITY.fr.md) — ce n'est pas du chiffrement de bout
   en bout.
3. **Trois fournisseurs au lieu de deux**, dont ElevenLabs, en mode batch : le texte arrive
   après l'arrêt de l'enregistrement.
4. **Le patch suit la version.** La méthode ne contient aucun numéro de version : elle lit
   `FileVersion` dans `Reasonix Studio.exe`, extrait le catalogue des bundles réellement
   chargés, et refuse d'appliquer quoi que ce soit s'il manque une traduction.

## Laquelle choisir

- **Reasonix Studio 2.55.0** → `pack-2.55/`, et rien d'autre.
- **Reasonix Studio 2.52.0 ou antérieur** → l'ancienne méthode, telle quelle.
- **Traduire vers une autre langue que le français** → l'ancienne méthode reste la référence :
  c'est elle qui porte la chaîne générique (extraire → traduire → injecter → vérifier).

Les deux méthodes ne se cumulent pas : appliquer `pack-2.55` puis un `Francisation_2.x.bat`
revient à écraser le pack avec l'ancien flux. Choisissez-en une.

## Ce qui n'a pas bougé

Rien. `README`, `CHANGELOG`, `scripts/`, `translations/`, `micro-winh/`, les `Francisation_2.x.bat`,
`MENU-REASONIX.bat`, `docs/`, `assets/` et les archives `Reasonix-FR-2.49/2.50/2.52.zip` sont
exactement dans l'état où ils étaient. Seule la tête des deux README reçoit un renvoi vers ce
fichier — aucune ligne existante n'a été réécrite.
