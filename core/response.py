"""
Response - le format standard que TOUS les workers renvoient à KAREN,
et que KAREN renvoie ensuite à DUM-E.

Grâce à ce format commun, DUM-E n'a jamais besoin de savoir QUEL worker
a répondu (Agenda ? Game ? Memo ?) : il sait juste comment afficher
une Response. C'est ça qui permet d'ajouter de nouveaux workers plus
tard sans toucher à DUM-E.
"""

class Response:
    def __init__(self, text=None, data=None):
        # text : ce qui doit être affiché à l'utilisateur.
        #        None = "je n'ai rien compris", DUM-E affichera son message par défaut.
        self.text = text

        # data : infos "techniques" pour DUM-E, PAS pour l'utilisateur.
        #        ex: {"game_state": True} pour dire à DUM-E qu'on est entré dans un jeu
        #        ex: {"username": "Armand"} pour mettre à jour le prénom connu
        self.data = data or {}

    def __repr__(self):
        return f"Response(text={self.text!r}, data={self.data!r})"