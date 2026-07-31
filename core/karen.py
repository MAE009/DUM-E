"""
karen.py

KAREN - le cerveau / orchestrateur de DUM-E.

Rôle de KAREN :
1. Recevoir le texte de l'utilisateur (transmis par DUM-E)
2. Détecter l'intention (intent) + extraire les infos utiles (slots)
3. Gérer les conversations multi-tours (ex: un rappel demandé en 2 étapes)
4. Déléguer au bon worker (Agenda, Game, Memo, System, Time...)
5. Retourner une Response à DUM-E

RÈGLE D'OR : KAREN ne fait JAMAIS de print() ni d'input() ici.
Comme ça, plus tard, on pourra brancher KAREN derrière Telegram, un site
web, une appli vocale... sans rien changer dans ce fichier.
"""
from shared.methode import clean_input, close_match
from core.response import Response
from core.personality_responses import get_response
import difflib


# Intents qui ont besoin de PLUSIEURS infos avant de pouvoir agir.
# Format : intent -> liste de (nom_du_slot, question_a_poser)
# Pour ajouter un nouvel intent multi-tours plus tard, il suffit d'ajouter
# une ligne ici, aucun autre fichier à toucher.
REQUIRED_SLOTS = {
    "SET_REMINDER": [
        ("texte", "Que dois-je te rappeler ?"),
        ("date", "Pour quand ? (ex: 15/01/2025, demain, lundi)"),
    ],
}

# Nombre max de fois où on redemande un même slot avant d'abandonner
# (évite une boucle infinie si l'utilisateur tape n'importe quoi).
MAX_SLOT_RETRIES = 2


class Karen:
    def __init__(self):
        self.workers = {}   # {"INTENT": worker}
        self.pending = None  # état en cours d'une collecte multi-tours (ou None)


    def register(self, intent_name, worker):
        """Associe un intent à un worker qui sait le traiter."""
        self.workers[intent_name] = worker

    # ---------------------------------------------------------
    # DETECTION D'INTENTION - version simple par mots-clés (config.py).
    # C'est la V1 de ta roadmap (KAREN v1.0 = Intent + Slots).
    # Plus tard tu pourras remplacer CETTE fonction par un vrai modèle NLP
    # sans toucher au reste de karen.py ni des workers.
    # ---------------------------------------------------------
    def detect_intent(self, texte):
        from shared.config import salutations, exits, helps, time_days

        ans_clean :str = clean_input(texte)
        # print("Debug:", ans_clean.split())
        intents = []



        if close_match(ans_clean, salutations) or any(k in ans_clean for k in salutations):
            # if ans_clean.startswith(salutations):
                # return "GREETING", {}, 0.9
            intents.append({
                "name": "GREETING",
                "priority": 10,
                "confidence": 0.9,
                "slots": {}
            })


        if close_match(ans_clean, exits) or any(k in ans_clean for k in exits):
            # if ans_clean.startswith(exits):
                # return "EXIT", {}, 0.9
            intents.append({
                "name": "EXIT",
                "priority": 5,
                "confidence": 0.9,
                "slots": {}
            })


        if close_match(ans_clean, helps) or any(k in ans_clean for k in helps):
            # if ans_clean.startswith(helps):
                # return "HELP", {}, 0.9
            intents.append({
                "name": "HELP",
                "priority": 20,
                "confidence": 0.9,
                "slots": {}
            })

        if any(k in ans_clean for k in time_days):
            if "heure" in ans_clean:
                # return "TIME", {"sous_intent": "heure"}, 0.9
                intents.append({
                    "name": "TIME",
                    "priority": 30,
                    "confidence": 0.9,
                    "slots": {"sous_intent": "heure"}
                })

            if "date" in ans_clean:
                # return "TIME", {"sous_intent": "date"}, 0.9
                intents.append({
                    "name": "TIME",
                    "priority": 30,
                    "confidence": 0.9,
                    "slots": {"sous_intent": "date"}
                })


            # return "TIME", {"sous_intent": "jour"}, 0.9
            intents.append({
                "name": "TIME",
                "priority": 30,
                "confidence": 0.9,
                "slots": {"sous_intent": "jour"}
            })

        # ⚠️ Testé AVANT la détection de prénom, car "rappel moi" contient
        # la sous-chaîne "appel" et serait sinon pris pour "je m'appelle".
        if "rappel moi" in ans_clean or "rappel-moi" in ans_clean:
            # return "SET_REMINDER", {}, 0.85
            intents.append({
                "name": "SET_REMINDER",
                "priority": 100,
                "confidence": 0.85,
                "slots": {}
            })

        # "oublie" AVANT "mon nom", car "oublie mon nom" contient "mon nom".
        if "oublie" in ans_clean:
            # return "FORGET_NAME", {}, 0.8
            intents.append({
                "name": "FORGET_NAME",
                "priority": 90,
                "confidence": 0.8,
                "slots": {}
            })

        # Détection tolérante du prénom : on compare chaque mot (par
        # similarité, pas par sous-chaîne) au radical "appelle". Ça
        # rattrape les fautes de frappe même quand les lettres sont
        # inversées (ex: "apple" au lieu de "appelle"), ce qu'une simple
        # recherche de sous-chaîne ne peut pas faire.
        # On exclut explicitement les mots contenant "rappel" pour ne
        # pas confondre avec un rappel/agenda.
        mots = ans_clean.split()
        idx_appel = None
        for i, mot in enumerate(mots[:4]):
            if "rappel" in mot or len(mot) < 4:
                continue
            similarite = difflib.SequenceMatcher(None, mot, "appelle").ratio()
            if similarite > 0.6:
                idx_appel = i
                break

        if idx_appel is not None:
            nom = " ".join(mots[idx_appel + 1:]).strip()
            # return "SET_NAME", {"nom": nom}, 0.85
            intents.append({
                "name": "SET_NAME",
                "priority": 80,
                "confidence": 0.85,
                "slots": {"nom": nom}
            })

        if "mon nom" in ans_clean:
            # return "GET_NAME", {}, 0.8
            intents.append({
                "name": "GET_NAME",
                "priority": 70,
                "confidence": 0.8,
                "slots": {}
            })

        if ans_clean in ("historique", "history", "his"):
            # return "HISTORY", {}, 0.9
            intents.append({
                "name": "HISTORY",
                "priority": 50,
                "confidence": 0.9,
                "slots": {}
            })

        if ans_clean in ("status", "debug", "version"):
            # return "DEBUG", {"sous_commande": ans_clean}, 0.9
            intents.append({
                "name": "DEBUG",
                "priority": 60,
                "confidence": 0.9,
                "slots": {"sous_commande": ans_clean}
            })

        if "jeu" in ans_clean or close_match(ans_clean, ["jouer"]):
            # return "GAME_START", {}, 0.8
            intents.append({
                "name": "GAME_START",
                "priority": 40,
                "confidence": 0.8,
                "slots": {}
            })

        # return "UNKNOWN", {}, 0.0

        # Changement de personnalité : "deviens secretaire", "mode majordome"...
        modes_personnalite = {"secretaire": "secretaire", "secrétaire": "secretaire",
                              "majordome": "majordome", "compagnon": "compagnon"}
        if any(mot in ans_clean for mot in ("deviens", "mode", "passe en")):
            for mot_cle, mode in modes_personnalite.items():
                if mot_cle in ans_clean:
                    intents.append({
                        "name": "SET_PERSONALITY",
                        "priority": 95,
                        "confidence": 0.9,
                        "slots": {"mode": mode}
                    })
                    break

        return intents

    def resolve_intents(self, intents):
        greetings = [i for i in intents if i["name"] == "GREETING"]
        others = [i for i in intents if i["name"] != "GREETING"]

        others = sorted(others, key=lambda i: i["priority"], reverse=True)

        return greetings + others

    # ---------------------------------------------------------
    # POINT D'ENTREE PRINCIPAL - appelé par DUM-E à chaque message.
    # context : dict transmis par DUM-E, ex {"game_state": True}
    # ---------------------------------------------------------
    def process(self, texte, context=None):
        context = context or {}
        personnalite = context.get("personnalite")

        if context.get("game_state") and "GAME_INPUT" in self.workers:
            resp = self.workers["GAME_INPUT"].handle("GAME_INPUT", {"texte": texte}, context)
            if resp is not None:
                return resp

        if self.pending is not None:
            return self._continue_pending(texte, personnalite)

        raw_intents = self.detect_intent(texte)
        ordered_intents = self.resolve_intents(raw_intents)

        if not ordered_intents:
            return Response(text=None)

        # Un intent multi-tours (ex: SET_REMINDER) passe devant tout le
        # reste, MAIS on garde la salutation si elle était aussi présente
        # dans le même message, pour ne pas la perdre silencieusement.
        slot_intent = next((i for i in ordered_intents if i["name"] in REQUIRED_SLOTS), None)
        if slot_intent:
            slot_response = self._start_slot_collection(slot_intent["name"], slot_intent["slots"])
            greeting_present = any(i["name"] == "GREETING" for i in ordered_intents)
            if greeting_present:
                habillage = get_response(personnalite, "GREETING")
                if habillage:
                    slot_response.text = f"{habillage}\n{slot_response.text}"
            return slot_response

        responses = []
        for intent_data in ordered_intents:
            if intent_data["confidence"] < 0.5:
                continue
            worker = self.workers.get(intent_data["name"])
            if worker is None:
                continue
            resp = worker.handle(intent_data["name"], intent_data["slots"], context)
            if resp and resp.text:
                habillage = get_response(personnalite, intent_data["name"], **resp.params)
                if habillage:
                    resp.text = habillage
                responses.append(resp)

        if not responses:
            return Response(text="Je comprends ce que tu veux, mais je n'ai pas encore le module pour ça.")

        texte_final = "\n\t".join(r.text for r in responses)
        data_finale = {}
        for r in responses:
            data_finale.update(r.data)

        return Response(text=texte_final, data=data_finale)

    def _start_slot_collection(self, intent, slots_deja_connus):
        self.pending = {
            "intent": intent,
            "collected": dict(slots_deja_connus),
            "restants": [s for s in REQUIRED_SLOTS[intent] if s[0] not in slots_deja_connus],
            "retry_count": 0,  # nombre de fois où un slot a dû être redemandé
        }
        return self._ask_next_slot()

    def _ask_next_slot(self, reask_text=None):
        nom_slot, question = self.pending["restants"][0]
        # Si on est en train de RE-demander suite à une erreur, on colle
        # le message d'erreur du worker avant la question.
        texte = f"{reask_text}\n{question}" if reask_text else question
        return Response(text=texte, data={"awaiting_slot": nom_slot})

    def _continue_pending(self, texte, personnalite=None):
        nom_slot, _question = self.pending["restants"].pop(0)
        self.pending["collected"][nom_slot] = texte.strip()

        if self.pending["restants"]:
            return self._ask_next_slot()

        intent = self.pending["intent"]
        slots = self.pending["collected"]
        retry_count = self.pending["retry_count"]
        self.pending = None

        worker = self.workers.get(intent)
        if worker is None:
            return Response(text="Je n'ai pas de module pour traiter ça.")

        response = worker.handle(intent, slots, {})

        retry_slot = response.data.get("retry_slot")
        if retry_slot:
            if retry_count >= MAX_SLOT_RETRIES:
                return Response(text="Bon, on laisse tomber ce rappel pour l'instant. Tu pourras réessayer plus tard.")
            self._reopen_slot(intent, slots, retry_slot, retry_count)
            return self._ask_next_slot(reask_text=response.text)

        habillage = get_response(personnalite, intent, **response.params)
        if habillage:
            response.text = habillage
        return response

    def _reopen_slot(self, intent, collected_slots, retry_slot, previous_retry_count):
        # On enlève le slot invalide des infos déjà collectées, et on le
        # remet seul dans la file d'attente pour le redemander.
        collected = dict(collected_slots)
        collected.pop(retry_slot, None)

        question = dict(REQUIRED_SLOTS[intent])[retry_slot]
        self.pending = {
            "intent": intent,
            "collected": collected,
            "restants": [(retry_slot, question)],
            "retry_count": previous_retry_count + 1,
        }