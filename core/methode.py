
#methode.py
import string
import difflib


def clean_input(user_input):
    user_input = user_input.lower()
    user_input = user_input.translate(str.maketrans("", "", string.punctuation))
    user_input = user_input.strip()
    return user_input


def close_match(ans, keywords, threshold=0.7):
    if isinstance(ans, str):
        words = ans.split()
    else:
        words = ans

    for token in words:
        for kw in keywords:
            if difflib.SequenceMatcher(None, token, kw).ratio() >= threshold:
                return kw

    return None


def tokenize(text):
    return text.split()


def detect_intent(ans):
    tokens = tokenize(ans)

    # Vérifier les phrases complètes d'abord
    if "rappel moi" in ans or "rappel-moi" in ans:
        return "REMINDER"

    if "créer rappel" in ans or "creer rappel" in ans:
        return "REMINDER"

    for word in tokens:
        if close_match(word, ["salut", "bonjour", "hello", "coucou", "holla", "yo", "hey"]):
            return "SALUTATION"

        if close_match(word, ["help", "aide", "liste", "commandes"]):
            return "HELP"

        if close_match(word, ["fin", "exit", "quitter", "au revoir", "bye", "stop"]):
            return "EXIT"

        if close_match(word, ["appelle"]) and "je m'appelle" in ans:
            return "GET_NAME"

        if close_match(word, ["nom"]) and ("mon nom" in ans or "monnom" in ans):
            return "GIVE_NAME"

        if close_match(word, ["oublie"]) and "mon nom" in ans:
            return "FORGET_NAME"

        if close_match(word, ["heure", "horaire"]):
            return "TIME"

        if close_match(word, ["date"]):
            return "DATE"

        if close_match(word, ["aujourd'hui", "aujourdhui", "jour"]):
            return "DAY"

        if close_match(word, ["status", "état", "etat"]):
            return "STATUS"

        if close_match(word, ["debug"]):
            return "DEBUG"

        if close_match(word, ["version"]):
            return "VERSION"

        if close_match(word, ["historique", "history", "his"]):
            return "HISTORIQUE"

        if close_match(word, ["jeu", "jouer", "game", "play"]):
            return "GAME_START"

    return "UNKNOWN"