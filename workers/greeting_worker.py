"""
GreetingWorker - gère l'intent GREETING (salut, bonjour...).
Séparé du reste car la salutation a une saveur "personnalité DUM-E"
plutôt que logique métier pure.
"""
import random
from core.response import Response
from core.worker_base import Worker


class GreetingWorker(Worker):
    name = "greeting"

    def can_handle(self, intent):
        return intent == "GREETING"

    def handle(self, intent, slots, context):
        phrases = [
            "Salut ! Comment je peux t'aider ?",
            "Hey 👋 Dis-moi ce que tu veux faire.",
            "Yo ! Je t'écoute.",
        ]
        return Response(text=random.choice(phrases))