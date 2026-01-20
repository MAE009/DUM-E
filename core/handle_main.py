
#handle.
from core.methode import clean_input, close_match, detect_intent
import datetime as dt
import random


class HandleMain:
    def __init__(self, dum_e, game_instance, save, agenda):
        self.dum_e = dum_e
        self.game = game_instance
        self.memo = save
        self.agenda = agenda
        self.histo = []
        self.now = dt.datetime.now()

        self.jours = {
            "Monday": "Lundi",
            "Tuesday": "Mardi",
            "Wednesday": "Mercredi",
            "Thursday": "Jeudi",
            "Friday": "Vendredi",
            "Saturday": "Samedi",
            "Sunday": "Dimanche"
        }

        # AJOUTEZ CES ATTRIBUTS pour gérer les conversations
        self.conversation_states = {}  # chat_id -> état de conversation
        self.user_reminder_data = {} # chat_id -> données temporaires

    # ============================================
    # MÉTHODES SYNCHRONES (pour la console)
    # ============================================

    def add_histo(self, handle, commande):
        self.histo.append({
            "type": handle,
            "commande": commande,
            "heure": f"{self.now.strftime('%H:%M:%S')}"
        })

        if len(self.histo) > 5:
            self.histo.pop(0)

    def handle_base(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "SALUTATION":
            print(self.dum_e.salutation())
            self.add_histo("salutation", ans_clean)
            return True

        return False

    async def handle_base_async(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "SALUTATION":
            self.add_histo("salutation", ans_clean)
            return self.dum_e.salutation()

        return None

    def handle_reminder(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        # Détecter "rappel moi" ou "rappel-moi"
        if intention == "REMINDER":
            # Extraire la partie après "rappel moi"
            if "rappel moi" in ans_clean:
                parts = ans_clean.split("rappel moi")
            else:
                parts = ans_clean.split("rappel-moi")

            if len(parts) > 1:
                # Prendre tout ce qui vient après "rappel moi"
                reste = parts[1].strip()

                # Séparer le rappel et la date (on cherche le dernier mot qui pourrait être une date)
                # Pour simplifier, on pourrait demander séparément
                print(f"{self.dum_e.name} : Que dois-je te rappeler ?")
                rappel = input("Moi : ").strip()

                print(f"{self.dum_e.name} : Pour quand ? (ex: 15/01/2025, demain, lundi)")
                date_input = input("Moi : ").strip()

                # Appeler update_reminder
                return self.agenda.update_reminder(rappel, date_input)

        return False

    async def handle_reminder_async(self, ans, chat_id=None):
        """Version async pour Telegram - Gestion conversationnelle"""
        ans_clean = clean_input(ans)

        # Vérifier si on est déjà dans une conversation de rappel
        if chat_id and chat_id in self.conversation_states:
            state = self.conversation_states[chat_id]

            if state == "waiting_reminder_text":
                # L'utilisateur a envoyé le texte du rappel
                if ans_clean.lower() in ["annuler", "cancel", "stop"]:
                    self._cleanup_conversation(chat_id)
                    return f"{self.dum_e.name} : Création de rappel annulée."

                # Stocker le texte du rappel
                self.user_reminder_data[chat_id] = {"rappel": ans_clean}
                self.conversation_states[chat_id] = "waiting_reminder_date"

                return (
                    f"{self.dum_e.name} : Merci ! Pour quand ce rappel ?\n"
                    "Formats acceptés :\n"
                    "- 15/01/2025 (jour/mois/année)\n"
                    "- 15 janvier 2025\n"
                    "- lundi prochain\n"
                    "- demain\n"
                    "- après-demain\n\n"
                    "Ou tape 'annuler' pour arrêter."
                )

            elif state == "waiting_reminder_date":
                # L'utilisateur a envoyé la date
                if ans_clean.lower() in ["annuler", "cancel", "stop"]:
                    self._cleanup_conversation(chat_id)
                    return f"{self.dum_e.name} : Création de rappel annulée."

                # Récupérer le texte du rappel
                reminder_data = self.user_reminder_data.get(chat_id, {})
                rappel = reminder_data.get("rappel", "")

                if not rappel:
                    self._cleanup_conversation(chat_id)
                    return f"{self.dum_e.name} : Erreur : données perdues. Recommencez."

                # Traiter la date
                date_info = self.agenda.parse_date(ans_clean)

                if date_info is None:
                    return (
                        f"{self.dum_e.name} : Format de date non reconnu.\n"
                        "Essayez : 15/01/2025, demain, lundi prochain\n"
                        "Ou tape 'annuler' pour arrêter."
                    )

                # Sauvegarder dans la mémoire
                self.dum_e.memo.update_agenda(rappel, date_info)

                # Nettoyer l'état de conversation
                self._cleanup_conversation(chat_id)

                # Message de confirmation
                if date_info["type"] == "exacte":
                    mois_nom = list(self.agenda.mois_fr.keys())[
                        list(self.agenda.mois_fr.values()).index(date_info["mois"])
                    ]
                    return (
                        f"✅ Rappel ajouté !\n"
                        f"📝 : {rappel}\n"
                        f"📅 : {date_info['jour']} {mois_nom} {date_info['annee']}\n\n"
                        f"{self.dum_e.name} : Je te rappellerai à cette date !"
                    )

                elif date_info["type"] == "semaine":
                    return (
                        f"✅ Rappel ajouté !\n"
                        f"📝 : {rappel}\n"
                        f"📅 : {date_info['jour_nom'].capitalize()}\n\n"
                        f"{self.dum_e.name} : Je te rappellerai chaque semaine !"
                    )

                elif date_info["type"] == "relative":
                    return (
                        f"✅ Rappel ajouté !\n"
                        f"📝 : {rappel}\n"
                        f"📅 : {date_info['jour']}/{date_info['mois']}/{date_info['annee']}\n\n"
                        f"{self.dum_e.name} : Je te rappellerai à cette date !"
                    )

        # Détection initiale de la commande "rappel"
        intention = detect_intent(ans_clean)

        if intention == "REMINDER" or "rappel" in ans_clean:
            if chat_id:
                # Démarrer une conversation
                self.conversation_states[chat_id] = "waiting_reminder_text"
                return (
                    f"{self.dum_e.name} : Je vais créer un rappel pour toi !\n"
                    "Tape le texte de ton rappel :\n"
                    "Exemple: 'Réunion avec l'équipe'\n\n"
                    "Ou tape 'annuler' pour arrêter."
                )
            else:
                # Mode sans chat_id (erreur)
                return f"{self.dum_e.name} : Pour créer un rappel, je dois connaître ton identifiant."

        return None

    def _cleanup_conversation(self, chat_id):
        """Nettoyer l'état de conversation"""
        if chat_id in self.conversation_states:
            del self.conversation_states[chat_id]
        if chat_id in self.user_reminder_data:
            del self.user_reminder_data[chat_id]

    # AJOUTEZ AUSSI CETTE MÉTHODE POUR GÉRER LES COMMANDES
    async def handle_conversation(self, ans, chat_id):
        """Gérer les états de conversation"""
        if chat_id in self.conversation_states:
            state = self.conversation_states[chat_id]

            # Si on est en train de créer un rappel
            if state in ["waiting_reminder_text", "waiting_reminder_date"]:
                return await self.handle_reminder_async(ans, chat_id)

            # Autres types de conversations possibles...

        return None


    def handle_system(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "HELP":
            self.show_help()
            self.add_histo("helps", ans_clean)
            return True

        if intention == "EXIT":
            print(self.dum_e.exit())
            self.add_histo("exit", ans_clean)
            return True

        return False

    async def handle_system_async(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "HELP":
            self.add_histo("helps", ans_clean)
            return self.get_help_text()

        if intention == "EXIT":
            self.add_histo("exit", ans_clean)
            return self.dum_e.exit()

        return None

    def get_help_text(self):
        help_text = """
🤖 *COMMANDES DUM-E*

*Commandes de base*
• Salut / Bonjour / Hello → Saluer DUM-E
• Date / Heure / Jour → Informations temporelles

*Mémoire utilisateur*
• "Je m'appelle [nom]" → Enregistrer ton prénom
• "Mon nom" → Afficher ton prénom
• "Oublie mon nom" → Supprimer ton prénom

*Mini-jeux*
• "Jeu" ou "Jouer" → Lancer un mini-jeu
• Pile ou Face → Jouer à pile ou face

*Agenda*
• "Rappel moi" → Créer un rappel
• "Créer rappel" → Créer un rappel étape par étape

*Système*
• Status → État du système
• Debug → Informations de debug
• Historique → Commandes récentes

*Commandes Telegram*
• /start → Démarrer le bot
• /help → Afficher cette aide
• /status → Vérifier l'état du bot
• /stop → Réinitialiser la conversation
"""
        return help_text

    def show_help(self):
        print("\n" + "=" * 50)
        print("            📘 AIDE — DUM-E v0.1")
        print("=" * 50)
        print(self.get_help_text())
        print("=" * 50 + "\n")

    def handle_memo(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "GET_NAME":
            self.add_histo("memo", ans_clean)
            parts_name = ans_clean.split()

            if len(parts_name) < 3:
                print("Je n'ai pas compris ton nom 😅")
                return True

            name = " ".join(parts_name[2:])

            if name:
                self.dum_e.username = name
                self.dum_e.memo.update_user_name(name)
                print(f"{self.dum_e.name} : Enchanté {self.dum_e.username} !\n")
            else:
                print(f"{self.dum_e.name} : Je n'ai pas compris ton prénom.\n")
            return True

        if intention == "GIVE_NAME":
            self.add_histo("memo", ans_clean)

            if self.dum_e.username:
                print(f"{self.dum_e.name} : Tu t'appelles {self.dum_e.username}.\n")
            else:
                print(f"{self.dum_e.name} : Je ne connais pas encore ton nom.\n")
            return True

        if intention == "FORGET_NAME":
            self.add_histo("memo", ans_clean)
            self.dum_e.username = ""
            self.dum_e.memo.update_user_name("")
            print(f"{self.dum_e.name} : J'ai oublié ton nom.\n")
            return True

        return False

    async def handle_memo_async(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "GET_NAME":
            self.add_histo("memo", ans_clean)
            parts_name = ans_clean.split()

            if len(parts_name) < 3:
                return "Je n'ai pas compris ton nom 😅\nFormat: 'Je m'appelle [ton nom]'"

            name = " ".join(parts_name[2:])

            if name:
                self.dum_e.username = name
                self.dum_e.memo.update_user_name(name)
                return f"{self.dum_e.name} : Enchanté {self.dum_e.username} !"
            else:
                return f"{self.dum_e.name} : Je n'ai pas compris ton prénom."

        if intention == "GIVE_NAME":
            self.add_histo("memo", ans_clean)

            if self.dum_e.username:
                return f"{self.dum_e.name} : Tu t'appelles {self.dum_e.username}."
            else:
                return f"{self.dum_e.name} : Je ne connais pas encore ton nom."

        if intention == "FORGET_NAME":
            self.add_histo("memo", ans_clean)
            self.dum_e.username = ""
            self.dum_e.memo.update_user_name("")
            return f"{self.dum_e.name} : J'ai oublié ton nom."

        return None

    def handle_time(self, ans):
        ans_clean = clean_input(ans)
        jour_en = self.jours[self.now.strftime("%A")]
        intention = detect_intent(ans_clean)

        if intention == "TIME":
            self.add_histo("time", ans_clean)
            print(f"{self.dum_e.name} : Il est {self.now.strftime('%H:%M:%S')}\n")
            return True

        if intention == "DATE":
            self.add_histo("time", ans_clean)
            print(f"{self.dum_e.name} : Aujourd'hui c'est le {self.now.strftime('%d/%m/%Y')}\n")
            return True

        if intention == "DAY":
            self.add_histo("time", ans_clean)
            print(f"{self.dum_e.name} : Aujourd'hui c'est {jour_en}\n")
            return True

        return False

    async def handle_time_async(self, ans):
        ans_clean = clean_input(ans)
        jour_en = self.jours[self.now.strftime("%A")]
        intention = detect_intent(ans_clean)

        if intention == "TIME":
            self.add_histo("time", ans_clean)
            return f"{self.dum_e.name} : Il est {self.now.strftime('%H:%M:%S')}"

        if intention == "DATE":
            self.add_histo("time", ans_clean)
            return f"{self.dum_e.name} : Aujourd'hui c'est le {self.now.strftime('%d/%m/%Y')}"

        if intention == "DAY":
            self.add_histo("time", ans_clean)
            return f"{self.dum_e.name} : Aujourd'hui c'est {jour_en}"

        return None

    def handle_game(self, ans):
        ans_clean = clean_input(ans)

        if self.game.game_current is None:
            if "jeu" in ans_clean or close_match(ans_clean, ["jouer"]):
                print(f"{self.dum_e.name} : Quel jeu te ferait plaisir ?")
                print("===== Jeux disponibles =====")
                print("\t🔹 Pile ou Face (tape 'pile' ou 'face')")
                print("\t🔹 Tape 'stop' pour quitter un jeu\n")
                self.dum_e.game_state = True
                self.game.game_current = "waiting_choice"
                return True

        if self.dum_e.game_state and self.game.game_current is not None:
            if self.game.update_game_current():
                self.add_histo("game", self.game.game_current)
                return True

        return False

    async def handle_game_async(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if self.game.game_current is None:
            if intention == "GAME_START":
                self.dum_e.game_state = True
                self.game.game_current = "waiting_choice"
                self.add_histo("game", "demarrage")
                return (
                    f"{self.dum_e.name} : Quel jeu te ferait plaisir ?\n"
                    "===== Jeux disponibles =====\n"
                    "🔹 Pile ou Face (réponds 'pile' ou 'face')\n"
                    "🔹 Tape 'stop' pour quitter un jeu"
                )

        if self.dum_e.game_state and self.game.game_current is not None:
            game_response = await self.game.update_game_current_async(ans_clean)
            if game_response:
                self.add_histo("game", self.game.game_current)
                return game_response

        return None

    def handle_debug(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "STATUS":
            print(f"\n{self.dum_e.name}: {'-' * 10} Status {'-' * 10}")
            print(f"Nom de l'assistant : {self.dum_e.name}")
            print(f"Version : {self.dum_e.version}")
            print(f"Nom de l'utilisateur : {self.dum_e.username if self.dum_e.username != '' else 'inconnu'}")
            print(f"Nombre de commandes exécutées: {len(self.histo)}")
            print(f"Heure de démarrage : {self.dum_e.time_demarrage}\n")
            print("_" * 25)
            return True

        elif intention == "DEBUG":
            print(f"\n{self.dum_e.name}: {'-' * 10} Debug {'-' * 10}")
            if self.histo:
                print(f"Dernière commande reçue : {self.histo[-1]}")
            else:
                print("Aucune commande enregistrée")
            print("_" * 25)
            return True

        elif intention == "VERSION":
            print(f"\n{self.dum_e.name}: {'-' * 10} Version {'-' * 10}")
            print(f"Version : {self.dum_e.version}")
            print(f"Type d'assistant : {self.dum_e.type}")
            print(f"Langage utilisé : {self.dum_e.language}")
            print("_" * 25)
            return True

        return False

    async def handle_debug_async(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "STATUS":
            status_text = (
                f"{self.dum_e.name}: {'-' * 10} Status {'-' * 10}\n"
                f"Nom de l'assistant : {self.dum_e.name}\n"
                f"Version : {self.dum_e.version}\n"
                f"Nom de l'utilisateur : {self.dum_e.username if self.dum_e.username != '' else 'inconnu'}\n"
                f"Nombre de commandes exécutées: {len(self.histo)}\n"
                f"Heure de démarrage : {self.dum_e.time_demarrage}\n"
                f"{'_' * 25}"
            )
            return status_text

        elif intention == "DEBUG":
            debug_text = f"{self.dum_e.name}: {'-' * 10} Debug {'-' * 10}\n"
            if self.histo:
                debug_text += f"Dernière commande reçue : {self.histo[-1]}\n"
            else:
                debug_text += "Aucune commande enregistrée\n"
            debug_text += f"{'_' * 25}"
            return debug_text

        elif intention == "VERSION":
            version_text = (
                f"{self.dum_e.name}: {'-' * 10} Version {'-' * 10}\n"
                f"Version : {self.dum_e.version}\n"
                f"Type d'assistant : {self.dum_e.type}\n"
                f"Langage utilisé : {self.dum_e.language}\n"
                f"{'_' * 25}"
            )
            return version_text

        return None

    def handle_historique(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "HISTORIQUE":
            print("\nHistorique des commandes :")
            if len(self.histo) > 0:
                for i, h in enumerate(self.histo, start=1):
                    if isinstance(h, dict):
                        print(f"{i}. [{h['heure']}] {h['type']} → {h['commande']}")
                    else:
                        print(f"{i}. ⚠️ Entrée invalide : {h}")
                print("_" * (len(self.histo) // 2), "\n")
                return True
            else:
                print(f"\t{self.dum_e.name} : On dirait que l'historique est vide !\n")
                return True

        return False

    async def handle_historique_async(self, ans):
        ans_clean = clean_input(ans)
        intention = detect_intent(ans_clean)

        if intention == "HISTORIQUE":
            if len(self.histo) > 0:
                histo_text =  "📜 Historique des commandes :\n"
                for i, h in enumerate(self.histo, start=1):
                    if isinstance(h, dict):
                        histo_text += f"{i}. [{h['heure']}] {h['type']} → {h['commande']}\n"
                    else:
                        histo_text += f"{i}. ⚠️ Entrée invalide : {h}\n"
                histo_text += f"{'_' * (len(self.histo) // 2)}"
                return histo_text
            else:
                return f"{self.dum_e.name} : On dirait que l'historique est vide !"

        return None