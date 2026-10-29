# Tutoriel — le micro pour les applications qui n'en ont pas

> **English version:** [`TUTORIAL.md`](TUTORIAL.md).

## 1. C'est quoi ?

C'est un **petit module de saisie vocale** que l'on ajoute à une application de chat Electron
qui n'a pas de bouton micro. Tu parles, le module transcrit ta voix et insère le texte dans le
composeur — exactement comme si tu l'avais tapé.

Ce n'est pas une application séparée, pas un serveur, pas un compte à créer. C'est **un fichier
JavaScript léger** (environ 66 Ko) ajouté à l'interface de l'application, plus un patcher pour
l'installer et revenir en arrière.

> **Le gros avantage :** la transcription passe par **Gemini**, dont la reconnaissance est
> nettement plus précise et mieux ponctuée que la dictée intégrée de Windows (**Win+H**),
> surtout pour les termes techniques, les noms propres et les messages longs. C'est le cœur
> du module : une dictée de qualité, sans dépendre du moteur local de Windows.

## 2. À quoi ça sert ?

| Situation | Ce que le module apporte |
|---|---|
| L'application n'a aucun bouton micro | un bouton micro à côté de la flèche d'envoi |
| Tu veux dicter un message long | enregistrement + transcription + insertion |
| Tu veux envoyer sans cliquer | envoi automatique à la fin de l'enregistrement |
| Tu joins un fichier | le micro reste en place ; l'envoi part avec la pièce jointe |
| L'agent travaille déjà | le message part en file d'attente (selon l'application) |
| Tu changes de taille de fenêtre | le micro suit, à droite ou au-dessus de la flèche |

## 3. Comment ça marche

```
clic micro → enregistrement (MediaRecorder)
           → arrêt
           → envoi de l'audio à Gemini (clé API)
           → texte transcrit
           → insertion dans le composeur
           → envoi automatique (optionnel)
```

Tout se passe **dans l'application**, côté interface. Aucun serveur intermédiaire, aucune
télémétrie, aucun compte. La clé Gemini reste dans le stockage local de l'application
(`localStorage`) et n'est envoyée qu'à Google pour la transcription.

## 4. Ce qu'il faut

| Besoin | Détail |
|---|---|
| **Une clé API Gemini gratuite** | créée sur Google AI Studio ; c'est la seule dépendance externe |
| **Une connexion Internet** | pour joindre Gemini |
| **L'application cible** | Reasonix Studio 2.40.0 (actuellement), AionUi 2.2.2, Open Cowork |
| **Rien d'autre** | pas de Node, pas de Python, pas de build, pas de compte |

Le module est **autonome et léger** : un fichier JS + une balise `<script>` dans l'interface.
Il n'ajoute aucune dépendance à l'application.

## 5. Installer (Reasonix Studio)

1. Ferme ou laisse Reasonix Studio ouvert — le patcher ne le ferme pas.
2. **Recommandé** : double-clique `PREPARER-SAUVEGARDE-MIC-REASONIX.bat`. Il crée et vérifie
   `index.html.bak` + `.sha256` **sans modifier l'application**.
3. Double-clique `REAPPLIQUER-MIC-REASONIX.bat` (le `mettre-a-jour.bat` du pack le fait déjà).
4. Recharge l'application (`Ctrl+R`) ou relance-la.
5. Le micro apparaît à côté de la flèche d'envoi.

Pour les autres applications, la démarche est la même ; seule la méthode d'installation
change (dossier plain ou asar). Voir [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) et
[`docs/SUPPORTED-APPS.md`](docs/SUPPORTED-APPS.md).

## 6. Obtenir la clé Gemini

1. Va sur **Google AI Studio** (`https://aistudio.google.com/apikey`).
2. Crée une clé API (le palier gratuit suffit pour un usage personnel).
3. Copie la clé (`AIza…`).
4. Dans l'application : **clic droit sur le micro** → colle la clé → **Enregistrer**.
5. Clique **Tester la clé Gemini**. Le panneau doit afficher que la clé est valide et que le
   modèle répond.

La clé est stockée localement. Ne la mets jamais dans un dépôt Git, une capture d'écran ou un
message public.

## 7. Utiliser

| Geste / mode | Effet |
|---|---|
| **Clic** sur le micro | démarre l'enregistrement ; le bouton devient « stop » |
| **Clic** à nouveau | arrête, transcrit, insère le texte |
| **Clic droit** | ouvre le **menu caché** : clé, modèle, langue, insertion auto, envoi auto, mot-clé |
| **Mode manuel** (envoi auto OFF) | le texte est inséré ; tu le relis, tu le modifies, tu envoies toi-même |
| **Mode automatique** (envoi auto ON) | le texte est inséré **et envoyé tout seul** à la fin de la transcription |
| **Pièce jointe** | joins le fichier avant de dicter ; le texte **et** le fichier partent ensemble |
| **Agent occupé** | le message est **mis en file d'attente** ; plusieurs messages peuvent attendre |
| **Forcer** | si le bouton reste grisé, le module réessaie ~2 s, puis affiche l'erreur et copie le texte ; tu peux cliquer envoyer/file |
| **Mot-clé d'envoi** | si activé, un mot à la fin (ex. « envoyer ») déclenche l'envoi |

**La particularité du programme :** un seul micro **dans le chat**, un **menu caché au clic
droit**, les modes **manuel / automatique**, les **pièces jointes**, la **file d'attente** et
la possibilité de **forcer**. Selon l'application, la file se vide automatiquement (Reasonix)
ou demande un envoi manuel pour les messages suivants (AionUi) ; dans tous les cas, tu peux
forcer ou envoyer à la main.

> **Le gros avantage :** Gemini transcrit mieux que Win+H, et le couple envoi automatique /
> file / pièces jointes permet de dicter plusieurs messages sans toucher la souris — tout en
> gardant le mode manuel pour relire.

## 8. Réglages

| Réglage | Rôle |
|---|---|
| Clé Gemini | obligatoire pour la transcription |
| Modèle | modèle Gemini utilisé pour la transcription |
| Langue | langue de la dictée (français par défaut) |
| Insertion auto | insère le texte sans confirmation |
| Envoi auto | envoie le message après l'insertion |
| Mot-clé d'envoi | envoie seulement si le texte contient le mot-clé |

## 9. Revenir en arrière / mettre à jour

| Situation | Geste |
|---|---|
| Problème après le patch | `RESTAURER-MIC-REASONIX.bat` |
| L'application ne démarre plus | ferme-la, lance `RESTAURER-MIC-REASONIX.bat`, relance |
| Mise à jour de l'application | `PREPARER-SAUVEGARDE...` puis `REAPPLIQUER-MIC-REASONIX.bat` |
| Vérifier l'état | `VERIFIER-MIC-REASONIX.bat` (lecture seule) |

La sauvegarde et son empreinte sont conservées ; le retour arrière fonctionne même sans
démarrer l'application.

## 10. Dépannage

| Symptôme | Piste |
|---|---|
| Pas de micro | interface non rechargée ; tag absent ; erreur JS dans la console |
| « Aucune clé API Gemini » | clé non enregistrée ; clic droit → Enregistrer → Tester |
| La clé est refusée | clé incorrecte, quota, ou modèle indisponible ; retester |
| Rien n'est inséré | composer introuvable ; vérifier les sélecteurs (voir inspection) |
| Le micro est mal placé | sélecteur d'envoi modifié ; voir `docs/METHODOLOGY.md` |
| Le message ne part pas | bouton d'envoi grisé (upload/rendu) ; le module retente ~2 s |
| L'agent travaille | le message peut être mis en file ou interjecté selon l'application |
| Après une mise à jour | réappliquer le patch (le dossier de l'interface est remplacé) |

## 11. Variante Windows / locale

### Pourquoi Gemini plutôt que Win+H ?

| Critère | Gemini via le module | Dictée Windows (Win+H) |
|---|---|---|
| Précision | **nettement meilleure** : contexte, phrases longues | correcte sur des phrases simples |
| Ponctuation / majuscules | gérées par le modèle | irrégulières |
| Langues | multilingue | dépend des packs installés |
| Termes techniques / noms propres | meilleur contexte | plus approximatif |
| Hors ligne | non (Internet + clé) | oui |
| Coût | palier gratuit Gemini | inclus dans Windows |

C'est le **gros avantage** du module : pour dictée réelle, Gemini est plus fiable que Win+H.
Windows reste un bon repli hors ligne ou sans clé.

Le backend de transcription est **remplaçable**. Aujourd'hui : Gemini. Demain, si tu veux
supprimer la clé et/ou Internet, on peut brancher :

| Backend | Avantage | Contrainte |
|---|---|---|
| Gemini (actuel) | qualité, langues, zéro install | clé + Internet |
| Windows `System.Speech` | local, pas de clé | nécessite un petit helper côté hôte (PowerShell/.NET) et un IPC ; qualité/langues variables |
| `Windows.Media.SpeechRecognition` | local, WinRT | pont Node/UWP, packs de langue, plus complexe |
| Whisper local | très bonne qualité | modèle lourd, CPU/GPU, installation |

Le point important : **le module garde l'enregistrement, l'insertion et l'envoi** ; seule la
fonction `transcribe()` change. La méthode et l'ancrage restent identiques. La variante
Windows n'est **pas implémentée dans la v1** ; elle demande un pont côté application (le
renderer est sandboxé et ne peut pas lancer un processus). C'est une piste documentée, pas une
promesse.

## 12. Autres applications

| Application | Interface | Patch | État |
|---|---|---|---|
| Reasonix Studio 2.40.0 | `frontend-next\dist` | copie + balise | **porté et validé** |
| Cline Desktop | Electron | même module + sélecteurs | **porté** ; ancrage à ajuster |
| Open Cowork | Electron | même module | **porté** (base) |
| AionUi 2.2.2 | `app.asar` | repack asar | **porté et validé** |

Le projet a été porté sur ces quatre applications. **Seuls quelques petits réglages d'ancrage
dans la fenêtre de chat sont nécessaires ; ce n'est pas une contrainte.** La méthode en
8 étapes est la même : repérer les contrôles, déterminer le packaging, adapter le stockage et
le preload, ancrer, vérifier, garder un retour arrière, documenter.

## 13. Vie privée et sécurité

- Aucune télémétrie, aucun serveur intermédiaire.
- L'audio est envoyé directement à Google Gemini avec **ta** clé.
- La clé est dans le stockage local de l'application ; elle n'est pas dans ce dépôt.
- Le module ne lit pas les conversations ; il ne touche qu'au composeur et au bouton d'envoi.
- Projet **non officiel**, fourni tel quel, sans garantie ; voir `LICENSE`.
