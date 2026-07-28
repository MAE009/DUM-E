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
            return Response(text=f"Il est {now.strftime('%H:%M:%S')}")
        if sous_intent == "date":
            return Response(text=f"Aujourd'hui c'est le {now.strftime('%d/%m/%Y')}")
        return Response(text=f"Aujourd'hui c'est {JOURS_FR[now.strftime('%A')]}")