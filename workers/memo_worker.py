"""
MemoWorker - gère le prénom utilisateur (SET_NAME, GET_NAME, FORGET_NAME).

Memo (Memo/memo.py) reste la SEULE source de vérité pour la persistance
JSON. Les autres workers (Agenda, Game) l'utilisent aussi directement
pour leurs propres besoins (agenda, scores de jeu).
"""
from core.response import Response
from core.worker_base import Worker


class MemoWorker(Worker):
    name = "memo"

    def __init__(self, memo):
        self.memo = memo

    def can_handle(self, intent):
        return intent in ("SET_NAME", "GET_NAME", "FORGET_NAME")

    def handle(self, intent, slots, context):
        if intent == "SET_NAME":
            nom = slots.get("nom", "").strip()
            if not nom:
                return Response(text="Je n'ai pas compris ton prénom.")
            self.memo.update_user_name(nom)
            return Response(text=f"Enchanté {nom} !", data={"username": nom})

        if intent == "GET_NAME":
            nom = self.memo.get_user_name()
            if nom:
                return Response(text=f"Tu t'appelles {nom}.")
            return Response(text="Je ne connais pas encore ton nom.")

        if intent == "FORGET_NAME":
            self.memo.update_user_name("")
            return Response(text="J'ai oublié ton nom.", data={"username": ""})

        return Response(text="Je ne sais pas traiter cette demande.")