"""
SystemWorker - commandes utilitaires : help, exit, debug, historique.
"""
from core.response import Response
from core.worker_base import Worker


class SystemWorker(Worker):
    name = "system"

    def __init__(self, dum_e_info, histo):
        self.info = dum_e_info   # dict : name, version, type, language, time_demarrage, username
        self.histo = histo       # référence PARTAGÉE à self.histo de DUM-E

    def can_handle(self, intent):
        return intent in ("HELP", "EXIT", "DEBUG", "HISTORY")

    def handle(self, intent, slots, context):
        if intent == "HELP":
            return Response(text=self._help_text(), params={})

        if intent == "EXIT":
            return Response(text="Es-tu sûr de vouloir quitter ?", data={"awaiting_exit_confirm": True})

        if intent == "DEBUG":
            sous_commande = slots.get("sous_commande", "status")
            return Response(
                text=self._debug_text(sous_commande),
                params={
                    "sous_commande": sous_commande,
                    "name": self.info["name"],
                    "version": self.info["version"],
                    "username": self.info.get("username") or "inconnu",
                    "nb_commandes": len(self.histo),
                    "demarrage": self.info["time_demarrage"],
                    "type": self.info["type"],
                    "language": self.info["language"],
                    "dernier": self.histo[-1] if self.histo else None,
                }
            )

        if intent == "HISTORY":
            return Response(
                text=self._history_text(),
                params={"nb_commandes": len(self.histo), "lignes": self._history_lignes()}
            )

        return Response(text="Commande système inconnue.")

    def _history_lignes(self):
        return [f"{i}. [{h['heure']}] {h['type']} → {h['commande']}" for i, h in enumerate(self.histo, 1)]

    def _help_text(self):
        return (
            "📘 AIDE — DUM-E\n"
            "salut/bonjour : saluer\n"
            "help/aide : cette aide\n"
            "fin/exit/quitter : quitter\n"
            "date/heure/jour : infos temps\n"
            "je m'appelle <nom> / mon nom / oublie mon nom : gestion du prénom\n"
            "jeu / jouer : mini-jeux\n"
            "his / historique : historique des commandes\n"
            "rappel moi : créer un rappel"
        )

    def _debug_text(self, sous_commande):
        if sous_commande == "status":
            return (
                f"Nom : {self.info['name']} | Version : {self.info['version']}\n"
                f"Utilisateur : {self.info.get('username') or 'inconnu'}\n"
                f"Commandes exécutées : {len(self.histo)}\n"
                f"Démarré à : {self.info['time_demarrage']}"
            )
        if sous_commande == "debug":
            dernier = self.histo[-1] if self.histo else "Aucune commande enregistrée"
            return f"Dernière commande : {dernier}"
        if sous_commande == "version":
            return f"Version {self.info['version']} — {self.info['type']} ({self.info['language']})"
        return "Sous-commande debug inconnue."

    def _history_text(self):
        if not self.histo:
            return "L'historique est vide."
        lignes = [f"{i}. [{h['heure']}] {h['type']} → {h['commande']}" for i, h in enumerate(self.histo, 1)]
        return "Historique des commandes :\n" + "\n".join(lignes)