# memo.py
import json
from pathlib import Path
import datetime as dt


class Memo:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.memory_file = self.base_path / "dum_e_memory.json"

        # Charger ou créer la mémoire avec la structure fixe
        self.data = self.load_memory()

    def load_memory(self):
        """Charge la mémoire depuis le fichier JSON avec structure fixe"""
        # Structure par défaut
        default_structure = {
            "user": {
                "name": "",
                "language": "fr"
            },
            "preferences": {
                "color": "",
                "city": ""
            },
            "agenda": {
                "taches": []
            },

            "history": {
                "commands": []
            },
            "games": {
                "devine_nombre": {
                    "best_score": None,
                    "played": 0
                }
            },
            "system": {
                "version": "0.3"
            }
        }

        # Si le fichier n'existe pas, créer avec structure par défaut
        if not self.memory_file.exists():
            self.save_memory(default_structure)
            return default_structure

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)

                # Fusionner avec la structure par défaut pour garder toutes les clés
                # Cela préserve les nouvelles valeurs tout en gardant la structure
                return self.merge_with_default(loaded_data, default_structure)

        except (json.JSONDecodeError, IOError):
            # En cas d'erreur, retourner la structure par défaut
            return default_structure

    def merge_with_default(self, loaded, default):
        """Fusionne les données chargées avec la structure par défaut"""
        result = default.copy()  # Commence avec la structure par défaut

        # Pour chaque section dans les données chargées
        for section in loaded:
            if section in result:
                if isinstance(result[section], dict) and isinstance(loaded[section], dict):
                    # Fusionner récursivement les dictionnaires
                    for key in loaded[section]:
                        result[section][key] = loaded[section][key]
                else:
                    # Si ce n'est pas un dict, remplacer complètement
                    result[section] = loaded[section]
            else:
                # Garder les sections supplémentaires
                result[section] = loaded[section]

        return result

    def save_memory(self, data=None):
        """Sauvegarde la mémoire dans le fichier JSON"""
        if data is None:
            data = self.data

        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def update_user_name(self, name):
        """Met à jour uniquement le nom de l'utilisateur"""
        self.data["user"]["name"] = name
        self.save_memory()

    def update_agenda(self, enonce, date_info):
        if date_info["type"] == "exacte":
            # Date exacte
            self.data["agenda"]["taches"].append({
                "rappel": enonce,
                "jour": date_info["jour"],
                "mois": date_info["mois"],
                "annee": date_info["annee"],
                "type": date_info["type"]
            })

        elif date_info["type"] == "semaine":
            # Jour de la semaine
            self.data["agenda"]["taches"].append({
                "rappel": enonce,
                "jour_nom": date_info["jour_nom"],
                "type": date_info["type"]
            })

        elif date_info["type"] == "relative":
            # Date relative (demain, etc.)
            self.data["agenda"]["taches"].append({
                "rappel": enonce,
                "jour": date_info["jour"],
                "mois": date_info["mois"],
                "annee": date_info["annee"],
                "type": date_info["type"]
            })
        self.save_memory()

    def clean_old_agenda(self):
        """
        Supprime les tâches dont la date est passée
        Retourne True si des tâches ont été supprimées
        """
        today = dt.datetime.now().date()
        tasks_to_keep = []
        tasks_deleted = 0

        for task in self.data["agenda"]["taches"]:
            if task.get("type") == "exacte" or task.get("type") == "relative":
                # Vérifier si la date est passée
                try:
                    task_date = dt.date(
                        task["annee"],
                        task["mois"],
                        task["jour"]
                    )

                    if task_date < today:
                        tasks_deleted += 1
                        continue  # Ne pas garder cette tâche

                except (KeyError, ValueError):
                    # Si la date est invalide, on garde la tâche
                    pass

            # Pour les tâches par jour de semaine, on ne les supprime pas automatiquement
            # (elles pourraient se répéter chaque semaine)
            tasks_to_keep.append(task)

        # Mettre à jour les tâches seulement si certaines ont été supprimées
        if tasks_deleted > 0:
            self.data["agenda"]["taches"] = tasks_to_keep
            self.save_memory()
            return True

        return False

    def get_agenda(self):
        return self.data["agenda"]["taches"]

    def update_preference(self, key, value):
        """Met à jour une préférence"""
        if key in self.data["preferences"]:
            self.data["preferences"][key] = value
            self.save_memory()

    def add_command_to_history(self, command):
        """Ajoute une commande à l'historique"""
        self.data["history"]["commands"].append({
            "command": command,
            "timestamp": dt.datetime.now().isoformat()
        })
        # Garder seulement les 50 dernières commandes
        if len(self.data["history"]["commands"]) > 50:
            self.data["history"]["commands"] = self.data["history"]["commands"][-50:]
        self.save_memory()

    def get_user_name(self):
        """Récupère le nom de l'utilisateur"""
        return self.data["user"].get("name", "")

    def update_game_score(self, game_name, score=0):
        """Met à jour le score d'un jeu"""
        if game_name not in self.data["games"]:
            self.data["games"][game_name] = {"best_score": None, "played": 0}

        # Mettre à jour le meilleur score si nécessaire
        current_best = self.data["games"][game_name]["best_score"]
        if current_best is None or score > current_best:
            self.data["games"][game_name]["best_score"] = score

        # Incrémenter le nombre de parties jouées
        self.data["games"][game_name]["played"] += 1

        self.save_memory()

    def get_game_stats(self, game_name):
        """Récupère les statistiques d'un jeu"""
        return self.data["games"].get(game_name, {"best_score": None, "played": 0})