import datetime as dt
from tkinter import StringVar
from agenda import Agenda
from Config import confir

# pour separer en different handle :
#         handle_base(),
#         handle_system(),
#         handle_memo(),
#         handle_time()...
from Memo import memo
import random
from handle_main import HandleMain
from Game.game import GameMain
import Memo.memo




class DUM_E:
    def __init__(self):
        self.running = True
        self.name = "DUM-E"
        self.version = 0.2
        self.type = "Assistant intelligent basé sur des règles"
        self.language = "Python"

        # Date de demarrage
        self.now = dt.datetime.now()
        self.time_demarrage = self.now.strftime('%H:%M:%S')

        # Initialiser la mémoire
        self.memo = Memo.memo.Memo()

        # Récupérer le nom de l'utilisateur depuis la mémoire
        self.username = self.memo.get_user_name()

        # Garder une référence aux données complètes si besoin
        self.memory_data = self.memo.data

        # Agenda
        self.agenda_reminder = Agenda(self)
        self.agenda_reminder.reminder_priority()


        # reponse de l'utilisateur
        self.Ans = ""

        #Permet de passer a une autre preoccupation
        self.Go = False

        # Game
        self.game = GameMain(self)

        # Créer l’instance handle en lui passant self
        self.handle = HandleMain(self, self.game, self.memo, self.agenda_reminder)

        # state
        self.game_state = False





        # Maintenir DUM-E
        self.run()


    # Modifier
    def salutation(self):
        ans_various = [
            f"Salut ! Je suis {self.name} v{self.version}. Prêt à t’aider 😄\n",
            f"Hey 👋 {self.name} à ton service.\n",
            f"Yo ! C’est {self.name}. Dis-moi ce que tu veux faire.\n",
            f"Hello 😎 Je suis {self.name} version {self.version}.\n",
            f"Salut ! Content de te voir. Moi c’est {self.name}.\n",
            f"Hey ! {self.name} est en ligne et opérationnel 💪\n",
            f"Bonjour ! Prêt pour bosser ensemble ? {self.name} est là.\n"
        ]

        print(random.choice(ans_various))


    def dialog(self):
        # if self.just_played:
        #     self.just_played = False  # Reset le flag
        #     # Ne pas afficher d'invite supplémentaire
        if not self.game_state:
            print(f"{self.name} : Comment puis-je t'aider ?")

        elif self.game.game_current == "pile_face":
            print(f"\n{self.name} : Parfait ! On joue à Pile ou Face.")
            print(f"{self.name} : pile ou face ?")

        else:
            print(f"{self.name} : alors ? {self.game.game_current}")

        self.Ans = input("Moi : ").lower()
        self.handle_event()




    # Modifier
    def exit(self):
        print(f"{self.name} : Es-tu sûr de vouloir quitter ?")
        yes_no = input("Moi : ...").lower()

        if yes_no in confir:
            self.running = False
        else:
            print(f"\n{self.name} : Annulé. Je suis toujours là")



    def handle_event(self):
        ans = self.Ans

        # D'abord vérifier si on est dans un jeu
        if self.game_state and self.game.game_current is not None:
            # Si on est en mode jeu, la priorité est au jeu
            if self.game.update_game_current():
                return
            else:
                # Si le jeu ne reconnaît pas la commande, on essaie les autres handlers
                pass

        # On essaye chaque handle
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
        elif not handled and self.game_state:
            print(f"{self.name} : Je n'ai pas compris. Tape 'pile', 'face' ou 'stop'.\n")




    def run(self):
        while self.running:
            self.dialog()




DUM_E()