import datetime as dt
from Config import salutations, exits, helps, time_days, memo

# pour separer en different handle :
#         handle_base(),
#         handle_system(),
#         handle_memo(),
#         handle_time()
from handle_main import HandleMain

class DUM_E:
    def __init__(self):
        self.running = True
        self.name = "DUM-E"
        self.version = 0.1
        self.type = "Assistant intelligent basé sur des règles"
        self.language = "Python"

        # Nom de l'utilisateur
        self.username = ""
        # reponse de l'utilisateur
        self.Ans = ""

        #Permet de passer a une autre preoccupation
        self.Go = False

        # Créer l’instance handle en lui passant self
        self.handle = HandleMain(self)

        # Maintenir DUM-E
        self.run()




    def salutation(self):
        print(f"Salut je suis {self.name} {self.version} \n")


    def dialog(self):
        print(f"{self.name} : Comment puis je t'aider ?")
        self.Ans = input("Moi : ...").lower()
        self.handle_event()


    def exit(self):
        self.running = False


    def handle_event(self):
        ans = self.Ans
        # On essaye chaque handle
        handled = (self.handle.handle_base(ans) or
                   self.handle.handle_system(ans) or
                   self.handle.handle_memo(ans) or
                   self.handle.handle_time(ans))
        if not handled:
            print("Commande non reconnue. Tape 'help' pour voir tout mes fonctionnalités\n")



    def run(self):
        while self.running:
            self.dialog()




DUM_E()