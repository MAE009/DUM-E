# handle_main.py

import datetime as dt

class HandleMain:
    def __init__(self, dum_e):
        # On garde une référence sur l'instance DUM-E
        self.dum_e = dum_e

    # ----- Handle Base -----
    def handle_base(self, ans):
        if ans in ("salut", "bonjour", "hello", "coucou"):
            self.dum_e.salutation()
            return True
        return False

    # ----- Handle System -----
    def handle_system(self, ans):
        if ans in ("help", "aide", "liste", "commandes"):
            self.show_help()
            return True
        elif ans in ("fin", "exit", "quitter", "au revoir"):
            self.dum_e.exit()
            return True
        return False

    def show_help(self):
        print("Commandes disponibles :")
        print("- salut / bonjour / hello / coucou")
        print("- fin / exit / quitter / au revoir")
        print("- help / aide / liste / commandes")
        print("- date / heure / temps / jour")
        print("- je m'appelle <nom> / mon nom / oublie mon nom\n")

    # ----- Handle Memo -----
    def handle_memo(self, ans):
        if "je m'appelle" in ans.lower():
            self.dum_e.username = ans[11:].strip()
            print(f"{self.dum_e.name} : Enchanté {self.dum_e.username} !\n")
            return True
        elif ans.lower() == "mon nom":
            if self.dum_e.username:
                print(f"{self.dum_e.name} : Tu t'appelles {self.dum_e.username}.\n")
            else:
                print(f"{self.dum_e.name} : Je ne connais pas encore ton nom.\n")
            return True
        elif ans.lower() == "oublie mon nom":
            self.dum_e.username = ""
            print(f"{self.dum_e.name} : J'ai oublié ton nom.\n")
            return True
        return False

    # ----- Handle Time -----
    def handle_time(self, ans):
        if ans in ("date", "heure", "temps", "jour"):
            now = dt.datetime.now()
            print(f"{self.dum_e.name} : Il est {now.strftime('%H:%M:%S')} le {now.strftime('%d/%m/%Y')}\n")
            return True
        return False
