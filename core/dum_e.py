"""
dum_e.py

DUM-E - le "corps" / l'interface avec l'utilisateur.

DUM-E ne réfléchit plus lui-même (fini les close_match/if partout).
Son rôle se limite à :
- afficher les messages, gérer sa personnalité (salutations...)
- récupérer l'input utilisateur
- transmettre le texte brut à KAREN
- afficher la Response que KAREN renvoie
- mettre à jour son propre état (game_state, username...) selon Response.data

Toute la "compréhension" et la logique métier vivent maintenant dans
KAREN et les workers.
"""
import random
import datetime as dt

from core.karen import Karen
from core.personnalite import Personnalite
from workers.personality_worker import PersonalityWorker
from Memo.memo import Memo
from shared.config import confir

from workers.agenda_worker import AgendaWorker
from workers.memo_worker import MemoWorker
from workers.game_worker import GameWorker
from workers.system_worker import SystemWorker
from workers.time_worker import TimeWorker
from workers.greeting_worker import GreetingWorker

class DUM_E:
    def __init__(self):
        self.running = True
        self.name = "DUM-E"
        self.version = 0.4
        self.type = "Assistant intelligent basé sur des règles"
        self.language = "Python"
        self.personnalite = Personnalite.SECRETAIRE  # valeur par défaut

        self.now = dt.datetime.now()
        self.time_demarrage = self.now.strftime('%H:%M:%S')

        # Mémoire (persistance JSON) - la classe Memo ne change pas
        self.memo = Memo()
        self.username = self.memo.get_user_name()

        # Historique des commandes (lu et affiché par SystemWorker)
        self.histo = []

        # États gérés par DUM-E lui-même (pas par KAREN, ce sont des
        # détails d'affichage/interface, pas de la logique métier)
        self.game_state = False
        self._awaiting_exit_confirm = False

        # ---- KAREN : le cerveau ----
        self.karen = Karen()
        self._register_workers()
        self.karen.register("SET_PERSONALITY", PersonalityWorker())

        self.run()

    def _register_workers(self):
        agenda_worker = AgendaWorker(self.memo)
        self.karen.register("GREETING", GreetingWorker())
        self.karen.register("SET_REMINDER", agenda_worker)
        self.karen.register("LIST_REMINDERS", agenda_worker)

        memo_worker = MemoWorker(self.memo)
        for intent in ("SET_NAME", "GET_NAME", "FORGET_NAME"):
            self.karen.register(intent, memo_worker)

        game_worker = GameWorker(self.memo)
        for intent in ("GAME_START", "GAME_INPUT"):
            self.karen.register(intent, game_worker)

        sys_info = {
            "name": self.name, "version": self.version,
            "type": self.type, "language": self.language,
            "time_demarrage": self.time_demarrage, "username": self.username,
        }
        system_worker = SystemWorker(sys_info, self.histo)
        for intent in ("HELP", "EXIT", "DEBUG", "HISTORY"):
            self.karen.register(intent, system_worker)

        self.karen.register("TIME", TimeWorker())

    def salutation(self):
        from core.personality_responses import get_response
        texte = get_response(self.personnalite, "GREETING")
        return texte or f"Bonjour, je suis {self.name}."


    def set_personnalite(self, mode):
        modes_valides = ["secretaire", "majordome", "compagnon"]

        if mode in modes_valides:
            self.personnalite = mode
            return f"Mode {mode} activé."

        return "Personnalité inconnue."



    def add_histo(self, handle, commande):
        self.histo.append({
            "type": handle, "commande": commande,
            "heure": dt.datetime.now().strftime('%H:%M:%S'),
        })
        if len(self.histo) > 5:
            self.histo.pop(0)

    def dialog(self):
        # if self._awaiting_exit_confirm:
        #     print(f"{self.name} : Es-tu sûr de vouloir quitter ?")

        if self.game_state:
            print(f"{self.name} : alors ?")

        elif self.karen.pending is None and not self._awaiting_exit_confirm:
            print(f"{self.name} : Comment puis-je t'aider ?")

        ans = input("Moi : ").strip()
        self.handle_event(ans)

    def handle_event(self, ans):
        # Cas spécial géré directement par DUM-E (pas par KAREN) :
        # la confirmation "oui/non" pour quitter.
        if self._awaiting_exit_confirm:
            if ans.lower() in confir:
                self.running = False
            else:
                print(f"{self.name} : Annulé. Je suis toujours là")
            self._awaiting_exit_confirm = False
            return

        context = {
            "game_state": self.game_state,
            "username": self.username,
            "personnalite": self.personnalite,
        }
        response = self.karen.process(ans, context)

        if response is None or response.text is None:
            if not self.game_state:
                print("Commande non reconnue. Tape 'help' pour voir toutes mes fonctionnalités\n")
            else:
                print(f"{self.name} : Je n'ai pas compris. Tape 'pile', 'face' ou 'stop'.\n")
            return

        if response.text:
            print(f"{self.name} : {response.text}\n")

        # DUM-E met à jour SON PROPRE état selon ce que le worker a demandé
        if "game_state" in response.data:
            self.game_state = response.data["game_state"]
        if "username" in response.data:
            self.username = response.data["username"]
        if response.data.get("awaiting_exit_confirm"):
            self._awaiting_exit_confirm = True

        if "set_personnalite" in response.data:
            from core.personnalite import Personnalite
            self.personnalite = Personnalite(response.data["set_personnalite"])

        self.add_histo("intent", ans)

    def run(self):
        print(self.salutation())
        while self.running:
            self.dialog()