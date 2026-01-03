from Program.methode import clean_input, close_match
import random


class GameMain:
    def __init__(self,dum_e):
        # On garde une référence sur l'instance DUM-E
        self.dum_e = dum_e

        self.game_current = None
        self.score = 0



        self.feedback_pos = ["Oh Bravos",
                             "Hum magnique"]

        self.feedback_neg = ["ah Ah Ah perdu",
                             "Mon intelecte est au dessus de tout"]

    def reset_game(self):
        self.game_current = None
        self.score = 0
        self.dum_e.game_state = False

    def update_game_current(self):
        # 🟡 CHOIX DU JEU
        ans_clean = clean_input(self.dum_e.Ans)

        if self.game_current == "waiting_choice":
            if "pile" in ans_clean or close_match(ans_clean, ["pile"] ) or close_match(ans_clean, ["face"]) or "face" in ans_clean:
                self.game_current = "pile_face"

                return True
            elif "stop" in ans_clean or close_match(ans_clean, ["stop", "quitter"]):
                print(f"{self.dum_e.name} : Jeu annulé.\n")
                self.game_current = None
                self.score = 0
                self.dum_e.game_state = False
                return True
            else:
                print(f"{self.dum_e.name} : Je ne connais pas ce jeu. Tape 'stop' pour annuler.\n")
                return True

        # Si on est déjà dans un jeu
        elif self.game_current == "pile_face":
            if "pile" in ans_clean or "face" in ans_clean:
                # Le jeu se lance ici
                self.pile_face(ans_clean)
                return True
            elif "stop" in ans_clean or close_match(ans_clean, ["stop", "quitter"]):
                print(f"{self.dum_e.name} : Jeu terminé ! Score final: {self.score}\n")
                self.game_current = None
                self.score = 0
                self.dum_e.game_state = False
                self.reset_game()
                return True



        return False


    def pile_face(self, user_choice):

        print(f"\n{self.dum_e.name} : Tu as choisi {user_choice}. Je lance la pièce...")
        dume_choice = random.choice(["pile", "face"])
        print(f"{self.dum_e.name} : C'est {dume_choice} !")

        if user_choice == dume_choice:
            self.score += 1
            print(f"{self.dum_e.name} : {random.choice(self.feedback_pos)} Score: {self.score}\n")
        else:
            print(f"{self.dum_e.name} : {random.choice(self.feedback_neg)} Score: {self.score}\n")

        # Proposer de rejouer
        print(f"{self.dum_e.name} : Encore une fois ? (pile/face) ou 'stop' pour arrêter")

        # Définir le flag pour éviter l'affichage double
        self.dum_e.just_played = True
        return True


