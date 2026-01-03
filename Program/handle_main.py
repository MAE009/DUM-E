# handle_main.py
from Config import salutations, exits, helps, time_days, memo
import datetime as dt
from methode import clean_input, close_match
from Game.game import GameMain



class HandleMain:
    def __init__(self, dum_e, game_instance):
        # On garde une référence sur l'instance DUM-E
        self.dum_e = dum_e

        self.game = game_instance

        # Historique
        self.histo = []

        # Time
        self.now = dt.datetime.now()


        # Pour handle time
        self.jours = {
            "Monday": "Lundi",
            "Tuesday": "Mardi",
            "Wednesday": "Mercredi",
            "Thursday": "Jeudi",
            "Friday": "Vendredi",
            "Saturday": "Samedi",
            "Sunday": "Dimanche"
        }


    # pour collecter les commandes appellees
    def add_histo(self, handle, commande):
        self.histo.append({
            "type": handle,
            "commande": commande,
            "heure": f"{self.now.strftime('%H:%M:%S')}"
        })

        if len(self.histo) > 5:
            self.histo.pop(0)



    # ----- Handle Base -----
    # Modifier
    def handle_base(self, ans):
        # Nettoyer l'entrée
        ans_clean = clean_input(ans)

        # Vérifier si un mot-clé de salutations correspond
        mot_trouve = close_match(ans_clean, salutations)
        if mot_trouve:
            self.dum_e.salutation()

            self.add_histo("salutation", ans_clean)

            return True
        return False


    # ----- Handle System -----
    # Modifier
    def handle_system(self, ans):
        # Nettoyer l'entrée
        ans_clean = clean_input(ans)

        # Vérifier les commandes help/aide
        mot_trouve = close_match(ans_clean, helps)
        if mot_trouve:
            self.show_help()
            self.add_histo("helps", ans_clean)


            return True

        # Vérifier les commandes exit/fin
        mot_trouve = close_match(ans_clean, exits)
        if mot_trouve:
            self.dum_e.exit()
            self.add_histo("exit", ans_clean)


            return True

        return False

    def show_help(self):
        print("\n" + "=" * 40)
        print("        📘 AIDE — DUM-E v0.1")
        print("=" * 40)

        print("\n🔹 Commandes de base")
        print("  • salut | bonjour | hello | coucou")
        print("    → Saluer DUM-E")

        print("\n🔹 Commandes système")
        print("  • help | aide | liste | commandes")
        print("    → Afficher cette aide")
        print("  • fin | exit | quitter | au revoir")
        print("    → Quitter DUM-E")

        print("\n🔹 Commandes temps")
        print("  • date | heure | temps | jour")
        print("    → Afficher la date et l'heure actuelles")

        print("\n🔹 Mémoire utilisateur")
        print("  • je m'appelle <nom>")
        print("    → Enregistrer ton prénom")
        print("  • mon nom")
        print("    → Afficher ton prénom")
        print("  • oublie mon nom")
        print("    → Supprimer ton prénom")

        print("\n🔹 Game Funny")
        print(f"{"=" * 5}Jeu disponible{"=" * 5}")
        print("  • Pile ou Face\n")

        print("\n" + "=" * 40 + "\n")


    # ----- Handle Memo -----
    def handle_memo(self, ans):
        # Nettoyer l'entrée
        ans_clean = clean_input(ans)

        # "je m'appelle" (avec tolérance aux petites fautes)
        if close_match("je m'appelle", [ans_clean]) or "je m'appelle" in ans_clean:
            self.add_histo("memo", ans_clean)


            # extraire le nom après "je m'appelle"
            name = ans_clean.replace("je m'appelle", "").strip()
            if name:  # vérifier qu'il y a bien un nom
                self.dum_e.username = name
                print(f"{self.dum_e.name} : Enchanté {name} !\n")
            else:
                print(f"{self.dum_e.name} : Je n'ai pas compris ton prénom.\n")
            return True

        # "mon nom"
        if close_match(ans_clean, ["mon nom"]) or "mon nom" in ans_clean:
            self.add_histo("memo", ans_clean)

            if self.dum_e.username:
                print(f"{self.dum_e.name} : Tu t'appelles {self.dum_e.username}.\n")
            else:
                print(f"{self.dum_e.name} : Je ne connais pas encore ton nom.\n")
            return True

        # "oublie mon nom"
        if close_match(ans_clean, ["oublie mon nom"]) or "oublie mon nom" in ans_clean:
            self.add_histo("memo", ans_clean)

            self.dum_e.username = ""
            print(f"{self.dum_e.name} : J'ai oublié ton nom.\n")
            return True

        return False


    # ----- Handle Time -----
    # Modifier
    def handle_time(self, ans):

        ans_clean = clean_input(ans)


        jour_en = self.jours[self.now.strftime("%A")]

        # Vérification "heure"
        if close_match(ans_clean, ["heure"]) or "heure" in ans_clean:
            self.add_histo("time", ans_clean)

            print(f"{self.dum_e.name} : Il est {self.now.strftime('%H:%M:%S')}\n")
            return True

        # Vérification "date"
        if close_match(ans_clean, ["date"]) or "date" in ans_clean:
            self.add_histo("time", ans_clean)


            print(f"{self.dum_e.name} : Aujourd'hui c'est le {self.now.strftime('%d/%m/%Y')}\n")
            return True

        # Vérification "jour"
        if close_match(ans_clean, ["jour"]) or "jour" in ans_clean:
            self.add_histo("time", ans_clean)


            print(f"{self.dum_e.name} : Aujourd'hui c'est {jour_en}\n")
            return True

        return False


    # New
    # ----- Handle Historique -----
    def handle_game(self, ans):
        ans_clean = clean_input(ans)

        # 🟢 AUCUN JEU EN COURS → on propose les jeux
        if self.game.game_current is None:
            if "jeu" in ans_clean or close_match(ans_clean, ["jouer"]):
                print(f"{self.dum_e.name} : Quel jeu te ferait plaisir ?")
                print("===== Jeux disponibles =====")
                print("\t🔹 Pile ou Face (tape 'pile' ou 'face')")
                print("\t🔹 Tape 'stop' pour quitter un jeu\n")
                self.dum_e.game_state = True
                self.game.game_current = "waiting_choice"
                return True

        # D'abord vérifier si on est dans un jeu
        if self.dum_e.game_state and self.game.game_current is not None:
            # Si on est en mode jeu, la priorité est au jeu
            if self.game.update_game_current():
                self.add_histo("game", self.game.game_current)
                # if self.game.game_current == "pile_face":
                #     self.game.pile_face(ans_clean)
                return True
            else:
                # Si le jeu ne reconnaît pas la commande, on essaie les autres handlers
                pass

        return False



    # ----- Handle debug -----
    def handle_debug(self, ans):
        ans_clean = clean_input(ans)

        if ans_clean == clean_input("status") or close_match(ans_clean, "status"):
            print(f"\n{self.dum_e.name}: {"-"*10} Status {"-"*10}")
            print(f"Nom de l’assistant : {self.dum_e.name}")
            print(f"Version : {self.dum_e.version}")
            print(f"Nom de l’utilisateur : {self.dum_e.username if self.dum_e.username != "" else "inconnu"}")
            print(f"Nombre de commandes exécutées: {len(self.histo)}")
            print(f"Heure de démarrage : {self.dum_e.time_demarrage}\n")
            print("_" * 25)
            return True

        elif ans_clean == clean_input("debug") or close_match(ans_clean, "debug"):
            print(f"\n{self.dum_e.name}: {"-"*10} Debug {"-"*10}")
            if self.histo:
                print(f"Dernière commande reçue : {self.histo[-1]}")
            else:
                print("Aucune commande enregistrée")

            print("_" * 25)
            return True

        elif ans_clean == clean_input("version") or close_match(ans_clean, "version"):
            print(f"\n{self.dum_e.name}: {"-"*10} Version {"-"*10}")
            print(f"Version : {self.dum_e.version}")
            print(f"Type d’assistant : {self.dum_e.type}")
            print(f"Langage utilisé : {self.dum_e.language}")
            print("_" * 25)
            return True

        return False


    # modifier
    # ----- Handle Historique -----
    def handle_historique(self, ans):
        ans_clean = clean_input(ans)
        if ans_clean in ("historique", "history", "his") :
            print("\nHistorique des commandes :")
            if len(self.histo) > 0:
                for i, h in enumerate(self.histo, start=1):
                    if isinstance(h, dict):
                        print(f"{i}. [{h['heure']}] {h['type']} → {h['commande']}")
                    else:
                        print(f"{i}. ⚠️ Entrée invalide : {h}")
                print("_"* (len(self.histo)//2),"\n")
                return True

            else:
                print(f"\t{self.dum_e.name} : On dirait que l'historique est vide !\n")
                return True

        return False