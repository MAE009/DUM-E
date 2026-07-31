"""
personality_responses.py

Associe à chaque (Personnalite, intent) une façon de reformuler la
réponse d'un worker. Si aucune entrée n'existe pour un couple donné,
KAREN garde le texte par défaut du worker (dette technique assumée,
comme d'habitude, pour les intents pas encore "habillés").

Format : PERSONALITY_RESPONSES[personnalite][intent] = fonction(**params) -> str
Les params viennent de Response.params, remplis par chaque worker.
"""
import random
from core.personnalite import Personnalite


PERSONALITY_RESPONSES = {
    Personnalite.SECRETAIRE: {
        "GREETING": lambda **p: random.choice([
            "Bonjour ! Que puis-je organiser pour toi aujourd'hui ?",
            "Ravie de te retrouver, je suis prête à t'aider.",
        ]),
        "TIME": lambda sous_intent="heure", valeur="", **p: {
            "heure": f"Il est {valeur}.",
            "date": f"Nous sommes le {valeur}.",
            "jour": f"Nous sommes {valeur}.",
        }.get(sous_intent, valeur),
        "SET_REMINDER": lambda texte="", **p: f"C'est noté : « {texte} ». Je m'en occupe.",
        "GAME_START": lambda **p: "Un jeu ? Pourquoi pas, si ça ne prend pas trop de temps.",

        "HELP": lambda **p: (
            "Voici ce que je sais faire : dire l'heure/la date, gérer tes rappels, "
            "retenir ton prénom, tenir l'historique, et te distraire avec un petit jeu. "
            "Tape 'his' pour l'historique ou 'rappel moi' pour un rappel."
        ),
        "DEBUG": lambda sous_commande="status", name="", version="", username="",
                        nb_commandes=0, demarrage="", type="", language="", dernier=None, **p: {
            "status": f"Tout tourne normalement. {nb_commandes} commande(s) traitée(s) depuis {demarrage}. "
                      f"Tu es enregistré comme {username}.",
            "debug": f"Dernière commande : {dernier}." if dernier else "Rien à signaler pour l'instant.",
            "version": f"Version {version}, comme d'habitude bien à jour.",
        }.get(sous_commande, "Rien de particulier à signaler."),
        "HISTORY": lambda nb_commandes=0, lignes=None, **p: (
            "\n".join(lignes) if lignes else "On n'a encore rien fait ensemble aujourd'hui."
        ),
    },
    Personnalite.MAJORDOME: {
        "GREETING": lambda **p: random.choice([
            "Bonjour Monsieur. Je suis à votre entière disposition.",
            "Bienvenue. Comment puis-je vous assister ?",
        ]),
        "TIME": lambda sous_intent="heure", valeur="", **p: {
            "heure": f"Il est précisément {valeur}, Monsieur.",
            "date": f"Nous sommes le {valeur}, Monsieur.",
            "jour": f"Nous sommes {valeur}, Monsieur.",
        }.get(sous_intent, valeur),
        "SET_REMINDER": lambda texte="", **p: f"Rappel noté et enregistré : « {texte} ».",
        "GAME_START": lambda **p: "Un jeu, Monsieur ? Fort bien, si vous le souhaitez.",

        "HELP": lambda **p: (
            "Voici, Monsieur, la liste de mes services : l'heure et la date, la gestion "
            "de vos rappels, la mémorisation de votre prénom, l'historique de nos échanges, "
            "et quelques divertissements si vous le souhaitez."
        ),
        "DEBUG": lambda sous_commande="status", name="", version="", username="",
                        nb_commandes=0, demarrage="", type="", language="", dernier=None, **p: {
            "status": f"Tout est en ordre, Monsieur. {nb_commandes} commande(s) exécutée(s) "
                      f"depuis {demarrage}. Vous êtes enregistré sous le nom de {username}.",
            "debug": f"Dernière commande consignée : {dernier}." if dernier else "Aucune commande à consigner, Monsieur.",
            "version": f"Version {version}, conforme aux dernières spécifications.",
        }.get(sous_commande, "Rien à signaler, Monsieur."),
        "HISTORY": lambda nb_commandes=0, lignes=None, **p: (
            "Voici le registre de nos échanges, Monsieur :\n" + "\n".join(lignes)
            if lignes else "Le registre est vide pour l'instant, Monsieur."
        ),
    },
    Personnalite.COMPAGNON: {
        "GREETING": lambda **p: random.choice([
            "Hey ! Content de te revoir 😄",
            "Yo ! On continue les projets ou on attaque un truc nouveau ?",
        ]),
        "TIME": lambda sous_intent="heure", valeur="", **p: {
            "heure": f"Il est {valeur} ! Parfait pour une petite pause jeu, non ?",
            "date": f"On est le {valeur}.",
            "jour": f"On est {valeur}.",
        }.get(sous_intent, valeur),
        "SET_REMINDER": lambda texte="", **p: f"Noté : « {texte} » ! Bon, on joue maintenant ?",
        "GAME_START": lambda **p: "ENFIN ! J'attendais que tu me le demandes !",

        "HELP": lambda **p: (
            "Alors, je peux te donner l'heure/la date, gérer tes rappels, retenir ton "
            "prénom, garder l'historique... et surtout, jouer avec toi 😄 Tape 'jeu' quand tu veux !"
        ),
        "DEBUG": lambda sous_commande="status", name="", version="", username="",
                        nb_commandes=0, demarrage="", type="", language="", dernier=None, **p: {
            "status": f"Tout roule ! {nb_commandes} commande(s) depuis {demarrage}. "
                      f"T'es {username} pour moi.",
            "debug": f"Dernier truc que t'as tapé : {dernier}." if dernier else "Rien à debug, on vient de commencer !",
            "version": f"Version {version}, ça tourne nickel.",
        }.get(sous_commande, "Rien à signaler, tout va bien !"),
        "HISTORY": lambda nb_commandes=0, lignes=None, **p: (
            "On a fait ça ensemble :\n" + "\n".join(lignes)
            if lignes else "On n'a encore rien fait, allez on s'y met !"
        ),
    },
}


def get_response(personnalite, intent, **params):
    """Renvoie le texte habillé pour (personnalite, intent), ou None si
    cette combinaison n'a pas encore de réponse personnalisée."""
    intent_map = PERSONALITY_RESPONSES.get(personnalite, {})
    handler = intent_map.get(intent)
    if handler is None:
        return None
    return handler(**params)