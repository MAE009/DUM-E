# Methode pour nettoyer ans(reponse de user)
# clean_input("Salut !")        # "salut"
# clean_input("Bonjour tout le monde") # "bonjour tout le monde"
import string

def clean_input(user_input):
    # tout en minuscule
    user_input = user_input.lower()
    # enlever ponctuation
    user_input = user_input.translate(str.maketrans("", "", string.punctuation))
    # enlever espaces superflus
    user_input = user_input.strip()
    return user_input



# close_match("salu", salutations)  # renvoie "salut"
# close_match("bonjor", salutations) # renvoie "bonjour"
# 0.7 signifie : la chaîne doit ressembler à au moins 70% au mot-clé
import difflib

def close_match(ans, keywords):
    for word in keywords:
        if difflib.SequenceMatcher(None, ans, word).ratio() > 0.7:
            return word
    return None