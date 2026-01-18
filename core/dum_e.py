
#dum_e.py
import datetime as dt
from core.agenda import Agenda
from core.handle_main import HandleMain
from core.game import GameMain
from core.memo import Memo
import random


class DUM_E:
    def __init__(self, telegram_mode=False, chat_id=None):
        self.running = True
        self.name = "DUM-E"
        self.version = 0.3
        self.type = "Assistant intelligent"
        self.language = "Python"
        self.telegram_mode = telegram_mode
        self.chat_id = chat_id

        # Date de démarrage
        self.now = dt.datetime.now()
        self.time_demarrage = self.now.strftime('%H:%M:%S')

        # Initialiser la mémoire (avec chemin spécifique pour Telegram)
        if telegram_mode and chat_id:
            self.memo = Memo(chat_id=chat_id)
        else:
            self.memo = Memo()

        # Récupérer le nom de l'utilisateur
        self.username = self.memo.get_user_name()

        # Agenda
        self.agenda_reminder = Agenda(self)

        # Game
        self.game = GameMain(self)

        # Créer l'instance handle
        self.handle = HandleMain(self, self.game, self.memo, self.agenda_reminder)

        # State
        self.game_state = False

        # Si pas en mode Telegram, démarrer l'interface console
        if not telegram_mode:
            self.run_console()

    async def process_message(self, message):
        """Traiter un message venant de Telegram"""
        self.Ans = message.lower()
        response = await self.handle_event_async()
        return response

    async def handle_event_async(self):
        """Version asynchrone pour Telegram"""
        ans = self.Ans

        # Vérifier si on est dans un jeu
        if self.game_state and self.game.game_current is not None:
            game_response = await self.game.update_game_current_async(ans)
            if game_response:
                return game_response

        # Essayer chaque handler
        response = await self.handle.handle_base_async(ans)
        if response: return response

        response = await self.handle.handle_system_async(ans)
        if response: return response

        response = await self.handle.handle_memo_async(ans)
        if response: return response

        response = await self.handle.handle_time_async(ans)
        if response: return response

        response = await self.handle.handle_historique_async(ans)
        if response: return response

        response = await self.handle.handle_game_async(ans)
        if response: return response

        response = await self.handle.handle_debug_async(ans)
        if response: return response

        response = await self.handle.handle_reminder_async(ans)
        if response: return response

        # Si rien n'est reconnu
        if not self.game_state:
            return "Commande non reconnue. Tape /help pour voir toutes mes fonctionnalités."
        else:
            return "Je n'ai pas compris. Tape 'pile', 'face' ou 'stop'."

    def salutation(self):
        """Générer une salutation"""
        ans_various = [
            f"Salut ! Je suis {self.name} v{self.version}. Prêt à t'aider 😄",
            f"Hey 👋 {self.name} à ton service.",
            f"Yo ! C'est {self.name}. Dis-moi ce que tu veux faire.",
            f"Hello 😎 Je suis {self.name} version {self.version}.",
            f"Salut ! Content de te voir. Moi c'est {self.name}.",
            f"Hey ! {self.name} est en ligne et opérationnel 💪",
            f"Bonjour ! Prêt pour bosser ensemble ? {self.name} est là."
        ]
        return random.choice(ans_various)

    def exit(self):
        """Gérer la sortie"""
        return "Au revoir ! Tape /start pour me redémarrer."

    def run_console(self):
        """Mode console (pour tests)"""
        print(self.salutation())
        while self.running:
            self.dialog_console()

    def dialog_console(self):
        """Dialogue en mode console"""
        if not self.game_state:
            print(f"{self.name} : Comment puis-je t'aider ?")
        elif self.game.game_current == "pile_face":
            print(f"{self.name} : pile ou face ?")
        else:
            print(f"{self.name} : alors ? {self.game.game_current}")

        self.Ans = input("Moi : ").lower()
        self.handle_event_console()

    def handle_event_console(self):
        """Version console (synchrone)"""
        ans = self.Ans

        if self.game_state and self.game.game_current is not None:
            if self.game.update_game_current():
                return

        handled = (self.handle.handle_base(ans) or
                   self.handle.handle_system(ans) or
                   self.handle.handle_memo(ans) or
                   self.handle.handle_time(ans) or
                   self.handle.handle_historique(ans) or
                   self.handle.handle_game(ans) or
                   self.handle.handle_debug(ans) or
                   self.handle.handle_reminder(ans))

        if not handled and not self.game_state:
            print("Commande non reconnue. Tape 'help' pour voir toutes mes fonctionnalités\n")