"""
Response - le format standard que TOUS les workers renvoient à KAREN,
et que KAREN renvoie ensuite à DUM-E.

Grâce à ce format commun, DUM-E n'a jamais besoin de savoir QUEL worker
a répondu (Agenda ? Game ? Memo ?) : il sait juste comment afficher
une Response. C'est ça qui permet d'ajouter de nouveaux workers plus
tard sans toucher à DUM-E.
"""

class Response:
    def __init__(self, text=None, data=None, params=None):
        # text : ce qui doit être affiché à l'utilisateur (texte par défaut).
        self.text = text

        # data : infos "techniques" pour DUM-E (game_state, username...)
        self.data = data or {}

        # params : faits BRUTS pour la personnalité (ex: {"valeur": "17:43"}).
        # Séparés de "data" car ce ne sont pas des infos système, juste
        # de quoi reformuler le texte selon la voix active.
        self.params = params or {}

    def __repr__(self):
        return f"Response(text={self.text!r}, data={self.data!r}, params={self.params!r})"