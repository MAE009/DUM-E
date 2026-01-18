
#game.py
from core.methode import clean_input, close_match
import random


class GameMain:
    def __init__(self, dum_e):
        self.dum_e = dum_e
        self.game_current = None
        self.score = 0

        self.feedback_pos = [
            "Oh Bravo ! 🎉",
            "Hum magnifique ! ✨",
            "Excellent ! 👏",
            "Tu es trop fort ! 🏆"
        ]

        self.feedback_neg = [
            "Ah ah ah perdu ! 😄",
            "Mon intellect est au-dessus de tout ! 🧠",
            "Essaie encore ! 💪",
            "Presque ! Mais pas assez 😉"
        ]

    def reset_game(self):
        self.game_current = None
        self.score = 0
        self.dum_e.game_state = False

    def update_game_current(self):
        ans_clean = clean_input(self.dum_e.Ans)

        if self.game_current == "waiting_choice":
            if ("pile" in ans_clean or "face" in ans_clean or
                    close_match(ans_clean, ["pile"]) or
                    close_match(ans_clean, ["face"])):
                self.game_current = "pile_face"
                return True

            elif "stop" in ans_clean or close_match(ans_clean, ["stop", "quitter"]):
                print(f"{self.dum_e.name} : Jeu annulé.\n")
                self.reset_game()
                return True

            else:
                print(f"{self.dum_e.name} : Je ne connais pas ce jeu. Tape 'stop' pour annuler.\n")
                return True

        elif self.game_current == "pile_face":
            if "pile" in ans_clean or "face" in ans_clean:
                self.pile_face(ans_clean)
                return True

            elif "stop" in ans_clean or close_match(ans_clean, ["stop", "quitter"]):
                print(f"{self.dum_e.name} : Jeu terminé ! Score final: {self.score}\n")
                self.dum_e.memo.update_game_score(self.game_current, self.score)
                print(f"{self.dum_e.name}: {self.dum_e.memo.get_game_stats(self.game_current)}")
                self.reset_game()
                return True

        return False

    async def update_game_current_async(self, user_input):
        ans_clean = clean_input(user_input)

        if self.game_current == "waiting_choice":
            if ("pile" in ans_clean or "face" in ans_clean or
                    close_match(ans_clean, ["pile"]) or
                    close_match(ans_clean, ["face"])):
                self.game_current = "pile_face"
                return (
                    f"{self.dum_e.name} : Parfait ! On joue à Pile ou Face.\n"
                    f"{self.dum_e.name} : Choisis 'pile' ou 'face' :"
                )

            elif "stop" in ans_clean or close_match(ans_clean, ["stop", "quitter"]):
                self.reset_game()
                return f"{self.dum_e.name} : Jeu annulé."

            else:
                return (
                    f"{self.dum_e.name} : Je ne connais pas ce jeu.\n"
                    "Jeux disponibles: 'pile' ou 'face'\n"
                    "Tape 'stop' pour annuler."
                )

        elif self.game_current == "pile_face":
            if "pile" in ans_clean or "face" in ans_clean:
                return await self.pile_face_async(ans_clean)

            elif "stop" in ans_clean or close_match(ans_clean, ["stop", "quitter"]):
                result = f"{self.dum_e.name} : Jeu terminé ! Score final: {self.score}"
                self.dum_e.memo.update_game_score(self.game_current, self.score)
                stats = self.dum_e.memo.get_game_stats(self.game_current)
                result += f"\nStatistiques: {stats}"
                self.reset_game()
                return result

        return None

    def pile_face(self, user_choice):
        print(f"\n{self.dum_e.name} : Tu as choisi {user_choice}. Je lance la pièce...")
        dume_choice = random.choice(["pile", "face"])
        print(f"{self.dum_e.name} : C'est {dume_choice} !")

        if user_choice == dume_choice:
            self.score += 1
            print(f"{self.dum_e.name} : {random.choice(self.feedback_pos)} Score: {self.score}\n")
        else:
            print(f"{self.dum_e.name} : {random.choice(self.feedback_neg)} Score: {self.score}\n")

        print(f"{self.dum_e.name} : Encore une fois ? (pile/face) ou 'stop' pour arrêter")
        return True

    async def pile_face_async(self, user_choice):
        result = f"{self.dum_e.name} : Tu as choisi {user_choice}. Je lance la pièce...\n"
        dume_choice = random.choice(["pile", "face"])
        result += f"{self.dum_e.name} : C'est {dume_choice} !\n"

        if user_choice == dume_choice:
            self.score += 1
            result += f"{self.dum_e.name} : {random.choice(self.feedback_pos)} Score: {self.score}\n"
        else:
            result += f"{self.dum_e.name} : {random.choice(self.feedback_neg)} Score: {self.score}\n"

        result += f"{self.dum_e.name} : Encore une fois ? (pile/face) ou 'stop' pour arrêter"
        return result