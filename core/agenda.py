#agenda.py
import datetime as dt


class Agenda:
    def __init__(self, dum_e):
        self.priority_reminder = []
        self.reminders = []
        self.time = dum_e.now
        self.dum_e = dum_e

        self.mois_fr = {
            "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
            "juin": 6, "juillet": 7, "août": 8, "aout": 8, "septembre": 9,
            "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
        }

    def parse_date(self, date_str):
        """
        Analyse une date sous différents formats :
        - "15/01/2025" (jour/mois/année)
        - "15 janvier 2025"
        - "lundi 15 janvier"
        - "lundi prochain"
        """

        # Nettoyer avant d'ajouter une nouvelle tâche
        self.dum_e.memo.clean_old_agenda()

        date_str = date_str.lower().strip()

        # 1. Format jour/mois/année (15/01/2025)
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                try:
                    jour = int(parts[0].strip())
                    mois = int(parts[1].strip())
                    annee = int(parts[2].strip())
                    return {"jour": jour, "mois": mois, "annee": annee, "type": "exacte"}
                except ValueError:
                    pass

        # 2. Format "15 janvier 2025" ou "15 janvier"
        words = date_str.split()

        # Vérifier si c'est un jour de la semaine
        jours_semaine = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        for jour_nom in jours_semaine:
            if jour_nom in date_str:
                # Pour simplifier, on va considérer "lundi" = prochain lundi
                # Vous pourriez améliorer ça avec datetime
                return {"jour_nom": jour_nom, "type": "semaine"}

        # 3. Format avec mois en lettres
        mois_trouve = None
        jour_trouve = None
        annee_trouve = None

        for word in words:
            # Chercher un jour (nombre)
            if word.isdigit():
                num = int(word)
                if 1 <= num <= 31:
                    jour_trouve = num

            # Chercher un mois
            elif word in self.mois_fr:
                mois_trouve = self.mois_fr[word]

            # Chercher une année (4 chiffres)
            elif word.isdigit() and len(word) == 4:
                annee_trouve = int(word)

        if jour_trouve and mois_trouve:
            return {
                "jour": jour_trouve,
                "mois": mois_trouve,
                "annee": annee_trouve or dt.datetime.now().year,
                "type": "exacte"
            }

        # 4. Mots spéciaux
        special_words = {
            "demain": 1,
            "après-demain": 2,
            "apres-demain": 2,
            "aujourd'hui": 0,
            "aujourdhui": 0
        }

        for word, jours_ajoutes in special_words.items():
            if word in date_str:
                aujourdhui = dt.datetime.now()
                date_rappel = aujourdhui + dt.timedelta(days=jours_ajoutes)
                return {
                    "jour": date_rappel.day,
                    "mois": date_rappel.month,
                    "annee": date_rappel.year,
                    "type": "relative"
                }

        # Si rien n'est trouvé
        return None

    async def update_reminder_async(self, message):
        """Version async pour créer un rappel"""
        # Nettoyer le message
        message = message.strip()

        # Détecter le format
        if "rappel " in message.lower():
            # Supprimer le mot "rappel" du début
            message = message.lower().replace("rappel ", "", 1).strip()

        # Séparer le texte et la date (simplifié)
        words = message.split()
        date_keywords = ["demain", "lundi", "mardi", "mercredi", "jeudi", "vendredi",
                         "samedi", "dimanche", "aujourd'hui", "semaine", "mois"]

        # Trouver où commence la date
        date_start = None
        for i, word in enumerate(words):
            if any(date_word in word for date_word in date_keywords) or '/' in word:
                date_start = i
                break

        if date_start is None:
            # Aucune date détectée, prendre le dernier mot comme date ?
            # Ou demander plus d'info
            return (
                f"Je n'ai pas détecté de date dans votre message.\n"
                f"Message reçu: '{message}'\n"
                f"Format attendu: '[rappel] [date]'\n"
                f"Exemple: 'réunion demain' ou 'anniversaire 15/01/2025'"
            )

        # Extraire rappel et date
        rappel_text = " ".join(words[:date_start])
        date_input = " ".join(words[date_start:])

        if not rappel_text:
            rappel_text = "Rappel sans description"

        # Analyser la date
        date_info = self.parse_date(date_input)

        if date_info is None:
            return (
                f"Je n'ai pas compris la date '{date_input}'.\n"
                "Formats acceptés:\n"
                "- demain, après-demain, aujourd'hui\n"
                "- lundi, mardi, etc.\n"
                "- 15/01/2025\n"
                "- 15 janvier 2025"
            )

        # Sauvegarder dans la mémoire
        self.dum_e.memo.update_agenda(rappel_text, date_info)

        # Message de confirmation
        if date_info["type"] == "exacte":
            mois_nom = list(self.mois_fr.keys())[list(self.mois_fr.values()).index(date_info["mois"])]
            return f"✅ Rappel '{rappel_text}' ajouté pour le {date_info['jour']} {mois_nom} {date_info['annee']}"

        elif date_info["type"] == "semaine":
            return f"✅ Rappel '{rappel_text}' ajouté pour {date_info['jour_nom'].capitalize()}"

        elif date_info["type"] == "relative":
            return f"✅ Rappel '{rappel_text}' ajouté pour le {date_info['jour']}/{date_info['mois']}/{date_info['annee']}"

        return f"✅ Rappel '{rappel_text}' enregistré."



    # sera appelle au demarrage
    def reminder_priority(self):
        # Nettoyer d'abord
        self.dum_e.memo.clean_old_agenda()

        # Récupérer l'agenda
        all_tasks = self.dum_e.memo.get_agenda()

        if all_tasks:
            # Séparer les tâches urgentes (dans les 7 prochains jours) et futures
            today = dt.datetime.now().date()
            urgent_tasks = []
            future_tasks = []

            for task in all_tasks:
                if task.get("type") in ["exacte", "relative"]:
                    try:
                        task_date = dt.date(
                            task["annee"],
                            task["mois"],
                            task["jour"]
                        )

                        # Calculer la différence en jours
                        delta = (task_date - today).days

                        if 0 <= delta <= 7:  # Dans les 7 prochains jours
                            urgent_tasks.append(task)
                        elif delta > 7:  # Plus loin dans le futur
                            future_tasks.append(task)

                    except (KeyError, ValueError):
                        # Tâche avec date invalide, on la met dans futures
                        future_tasks.append(task)
                else:
                    # Tâches par jour de semaine
                    urgent_tasks.append(task)  # On considère comme urgentes

            # Afficher les tâches urgentes
            if urgent_tasks:
                print(f"\n{self.dum_e.name} : 📌 RAPPELS URGENTS (7 prochains jours) :")
                for i, rappel in enumerate(urgent_tasks, 1):
                    if rappel.get("type") == "exacte" or rappel.get("type") == "relative":
                        # Calculer combien de jours restent
                        task_date = dt.date(rappel["annee"], rappel["mois"], rappel["jour"])
                        days_left = (task_date - today).days
                        if days_left == 0:
                            days_str = "AUJOURD'HUI"
                        elif days_left == 1:
                            days_str = "DEMAIN"
                        else:
                            days_str = f"dans {days_left} jours"

                        print(
                            f"  {i}. {rappel['rappel']} - le {rappel['jour']}/{rappel['mois']}/{rappel['annee']} ({days_str})")
                    elif rappel.get("type") == "semaine":
                        print(f"  {i}. {rappel['rappel']} - {rappel['jour_nom'].capitalize()}")

            # Afficher les tâches futures
            if future_tasks:
                print(f"\n{self.dum_e.name} : 📅 TÂCHES FUTURES :")
                for i, rappel in enumerate(future_tasks, 1):
                    if rappel.get("type") == "exacte" or rappel.get("type") == "relative":
                        print(f"  {i}. {rappel['rappel']} - le {rappel['jour']}/{rappel['mois']}/{rappel['annee']}")

            if urgent_tasks or future_tasks:
                print()

        else:
            print(f"{self.dum_e.name} : Aucun rappel dans l'agenda.\n")