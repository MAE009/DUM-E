"""
PersonalityWorker - permet de changer la personnalité active de DUM-E
en discutant ("deviens Golgame", "mode secretaire"...).
"""
from core.response import Response
from core.worker_base import Worker

MODES_VALIDES = ("secretaire", "majordome", "compagnon")


class PersonalityWorker(Worker):
    name = "personality"

    def can_handle(self, intent):
        return intent == "SET_PERSONALITY"

    def handle(self, intent, slots, context):
        mode = slots.get("mode")
        if mode not in MODES_VALIDES:
            return Response(text="Je ne connais pas cette personnalité.")
        return Response(text=f"Mode {mode} activé.", data={"set_personnalite": mode})