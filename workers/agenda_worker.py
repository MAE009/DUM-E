"""
AgendaWorker - fait le pont entre KAREN et ta logique Agenda existante
(agenda.py + Memo/memo.py), sans la réécrire tout de suite.

Ce worker reste "bête" volontairement : il ne gère aucun dialogue
multi-tours (KAREN s'en occupe via REQUIRED_SLOTS dans karen.py).
Il reçoit intent + slots déjà complets, et répond.
"""
import datetime as dt
from core.response import Response
from core.worker_base import Worker
from features.agenda import Agenda


class AgendaWorker(Worker):
    name = "agenda"

    def __init__(self, memo):
        # Agenda (agenda.py) attend un objet "dum_e" avec .memo et .name.
        # Plutôt que de réécrire agenda.py maintenant, on lui donne un
        # petit objet minimal qui joue ce rôle (_AgendaHost ci-dessous).
        # TODO plus tard : simplifier agenda.py pour qu'il ne dépende
        # plus que de memo directement.
        self._host = _AgendaHost(memo)
        self.agenda = Agenda(self._host)

    def can_handle(self, intent):
        return intent in ("SET_REMINDER", "LIST_REMINDERS")

    def handle(self, intent, slots, context):
        if intent == "SET_REMINDER":
            texte = slots.get("texte", "").strip()
            date_input = slots.get("date", "").strip()

            ok = self.agenda.update_reminder(texte, date_input)
            if ok:
                return Response(text=f"C'est noté : « {texte} »")

            # On ne redemande PAS le texte du rappel (déjà validé),
            # seulement la date -> signal retry_slot pour KAREN.
            return Response(
                text="Je n'ai pas compris cette date, tu peux réessayer ?",
                data={"retry_slot": "date"}
            )

        if intent == "LIST_REMINDERS":
            self.agenda.reminder_priority()  # affiche encore via print() pour l'instant
            return Response(text=None)

        return Response(text="Je ne sais pas traiter cette demande d'agenda.")


class _AgendaHost:
    """Objet minimal qui imite l'ancien `dum_e`, juste pour ce dont Agenda a besoin."""
    def __init__(self, memo):
        self.memo = memo
        self.name = "DUM-E"
        self.now = dt.datetime.now()