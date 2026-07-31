"""
TimeWorker - date, heure, jour de la semaine.
"""
import datetime as dt
from core.response import Response
from core.worker_base import Worker

JOURS_FR = {
    "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
    "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"
}


class TimeWorker(Worker):
    name = "time"

    def can_handle(self, intent):
        return intent == "TIME"

    def handle(self, intent, slots, context):
        now = dt.datetime.now()
        sous_intent = slots.get("sous_intent", "heure")

        if sous_intent == "heure":
            valeur = now.strftime('%H:%M:%S')
            texte_defaut = f"Il est {valeur}"
        elif sous_intent == "date":
            valeur = now.strftime('%d/%m/%Y')
            texte_defaut = f"Aujourd'hui c'est le {valeur}"
        else:
            valeur = JOURS_FR[now.strftime('%A')]
            texte_defaut = f"Aujourd'hui c'est {valeur}"

        return Response(text=texte_defaut, params={"sous_intent": sous_intent, "valeur": valeur})