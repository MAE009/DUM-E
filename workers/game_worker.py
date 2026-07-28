"""
GameWorker - fait le pont entre KAREN et GameMain (game.py).

⚠️ Dette technique transitoire : GameMain fait encore des print() DIRECTS
à l'intérieur de lui-même (pile_face, update_game_current...), au lieu de
renvoyer du texte via Response. Pour l'instant on le laisse tel quel pour
ne pas tout casser d'un coup. TODO futur : faire renvoyer du texte à
GameMain au lieu de print(), pour respecter le protocole partout.
"""
from core.response import Response
from core.worker_base import Worker
from features.game import GameMain


class GameWorker(Worker):
    name = "game"

    def __init__(self, memo):
        self._host = _GameHost(memo)
        self.game = GameMain(self._host)

    def can_handle(self, intent):
        return intent in ("GAME_START", "GAME_INPUT")

    def handle(self, intent, slots, context):
        if intent == "GAME_START":
            self._host.game_state = True
            self.game.game_current = "waiting_choice"
            texte = (
                "Quel jeu te ferait plaisir ?\n"
                "===== Jeux disponibles =====\n"
                "\t🔹 Pile ou Face (tape 'pile' ou 'face')\n"
                "\t🔹 Tape 'stop' pour quitter un jeu"
            )
            return Response(text=texte, data={"game_state": True})

        if intent == "GAME_INPUT":
            self._host.Ans = slots.get("texte", "")
            handled = self.game.update_game_current()  # renvoie True/False

            if handled:
                # Traité avec succès -> game.py a déjà tout affiché via print()
                # (dette technique connue). text="" = "rien à ajouter, mais
                # ce n'est PAS une erreur" (différent de text=None).
                return Response(text="", data={"game_state": self._host.game_state})
            else:
                # Vraiment pas compris -> laisse DUM-E afficher le message
                # "Tape pile/face/stop"
                return Response(text=None, data={"game_state": self._host.game_state})

        return Response(text=None)


class _GameHost:
    """Objet minimal qui imite l'ancien `dum_e`, juste pour ce dont GameMain a besoin."""
    def __init__(self, memo):
        self.name = "DUM-E"
        self.memo = memo
        self.Ans = ""
        self.game_state = False