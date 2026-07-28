"""
Worker - classe de base que tous les modules spécialisés doivent suivre
(AgendaWorker, GameWorker, MemoWorker, SystemWorker, TimeWorker...).

RÈGLE D'OR : un worker ne gère JAMAIS de conversation multi-tours lui-même
(pas de input() à l'intérieur !). Si une action a besoin de plusieurs infos
(ex: un rappel a besoin d'un texte ET d'une date), c'est KAREN qui les
collecte une par une AVANT d'appeler le worker, une seule fois, avec
tous les slots déjà remplis.

Ça garantit que les workers restent "sans état de dialogue" -> réutilisables
plus tard sur n'importe quelle interface (Telegram, web...).
"""

class Worker:
    name = "worker_base"

    def can_handle(self, intent):
        """True si ce worker sait traiter cet intent (utile pour le debug)."""
        raise NotImplementedError

    def handle(self, intent, slots, context):
        """
        intent  : str, ex "SET_REMINDER"
        slots   : dict des infos déjà extraites, ex {"texte": "l'ecole", "date": "15/01/2025"}
        context : dict d'infos ambiantes fournies par DUM-E, ex {"game_state": True}

        -> doit toujours renvoyer une Response (jamais un print(), jamais un input())
        """
        raise NotImplementedError