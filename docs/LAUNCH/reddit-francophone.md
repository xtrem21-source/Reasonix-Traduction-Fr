> **DRAFT — adapt before posting.** Post in **French**. r/francophone is a
> practical audience: lead with "you can use Reasonix Studio in French now", keep
> the technical part short, and be precise about the version constraint — it will
> be the first question.

---

**Titre :** Reasonix Studio en français — un outil pour traduire son interface (non officiel)

**Corps :**

Bonjour à tous,

Reasonix Studio est une application desktop dont l'interface n'existe qu'en
**chinois et en anglais**. Si vous ne lisez confortablement ni l'un ni l'autre,
l'application est difficile à utiliser — non pas parce qu'elle est fermée, mais
parce que ses traductions sont compilées dedans et qu'il n'y a pas de moyen
public d'en ajouter une.

J'ai donc écrit un petit outil qui traduit l'interface **localement**, sur votre
propre installation. Il est entièrement en français, et l'outil est générique :
n'importe qui peut s'en servir pour ajouter l'espagnol, l'allemand, le japonais…

**Ce que ça donne**

Environ 3 900 chaînes traduites : menus, panneaux, paramètres, messages
d'erreur, page de démarrage, menu clic droit, menu de la zone de notification
(tray). Le sélecteur de langue propose désormais **Français**.

**Comment l'utiliser**

```
git clone <lien du dépôt>
cd Reasonix-Traduction-Fr
python3 scripts/inject_fr.py        # applique le français
python3 scripts/verify_installed.py # vérifie que ça a bien pris
```

Puis redémarrez Reasonix Studio et choisissez **Paramètres → Langue → Français**.

Il faut Python 3, et Node pour la partie « coque native » (facultative). Aucune
compilation.

**Ce qu'il faut savoir avant de se lancer**

- **Version ciblée : Reasonix Studio 2.40.0.** C'est important : les fichiers de
  l'interface sont minifiés et leurs noms changent à chaque version. Sur une
  autre version, l'injection peut ne pas trouver ses repères — dans ce cas, elle
  le **signale** et s'abstient, elle ne casse rien.
- **Après une mise à jour de Reasonix Studio, il faut relancer l'outil.**
  La mise à jour écrase les fichiers modifiés et le français disparaît jusqu'à ce
  qu'on le réapplique.
- **Sauvegardes automatiques.** Chaque fichier remplacé est copié avant d'être
  modifié, dans un dossier daté. On peut revenir en arrière.
- **Certaines chaînes restent en anglais** : celles du cœur du programme
  (ligne de commande, notifications), qui sont compilées dans un binaire. Elles
  ne concernent pas la fenêtre de l'application.
- C'est un projet **non officiel et non affilié** à Reasonix.

**Pourquoi je partage**

L'objectif n'est pas de « patcher » une application, mais de la rendre utilisable
par des gens qu'elle exclut aujourd'hui. Si vous êtes à l'aise dans une autre
langue que le français, l'outil sait faire — et une traduction partielle est
utile : toute chaîne non traduite s'affiche simplement en chinois, jamais comme
un vide.

Dépôt : https://github.com/xtrem21-source/Reasonix-Traduction-Fr. Il traduit
l'interface de [DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)
(Reasonix Studio), version ciblée **2.40.0** ; non officiel, non affilié à
l'amont. Les retours, corrections de traduction et nouvelles langues sont les
bienvenus.

*Merci d'avoir lu — et n'hésitez pas si quelque chose n'est pas clair.*
