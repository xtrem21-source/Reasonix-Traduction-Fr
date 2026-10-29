# Sécurité / Security

## Français

- **Aucune clé API n'est présente dans ce dépôt.** La clé Gemini est saisie par l'utilisateur
  et stockée dans le `localStorage` de l'application (`rx-ocVoice.geminiKey`).
- L'audio est envoyé **directement à Google Gemini** avec la clé de l'utilisateur. Aucun
  serveur intermédiaire, aucune télémétrie, aucun compte.
- Le module ne lit pas les conversations et ne modifie que le composeur, le bouton d'envoi et
  son propre panneau.
- Ne publie jamais ta clé dans une issue, une capture d'écran ou un commit.
- Pour signaler une vulnérabilité : ouvre une **issue privée** sur le dépôt ou contacte
  l'auteur via GitHub. Ne divulgue pas publiquement une clé ou un exploit.
- Le patch modifie une copie locale de l'interface d'une application tierce ; il est fourni
  **tel quel**, sans garantie. Voir `LICENSE`.

## English

- **No API key is present in this repository.** The Gemini key is entered by the user and
  stored in the app's `localStorage` (`rx-ocVoice.geminiKey`).
- Audio is sent **directly to Google Gemini** with the user's key. No intermediary server, no
  telemetry, no account.
- The module does not read conversations; it only touches the composer, the send button and
  its own panel.
- Never publish your key in an issue, screenshot or commit.
- To report a vulnerability: open a **private issue** on the repository or contact the author
  via GitHub. Do not disclose a key or an exploit publicly.
- The patch modifies a local copy of a third-party app's UI; it is provided **as is**, without
  warranty. See `LICENSE`.
