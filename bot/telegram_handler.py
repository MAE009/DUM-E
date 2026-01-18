from telegram import Update
from telegram.ext import ContextTypes
from core.dum_e import DUM_E
import random


class TelegramHandler:
    def __init__(self, application):
        self.application = application
        self.dum_e_instances = {}  # Stocker une instance DUM-E par chat_id

    def get_dum_e_instance(self, chat_id):
        """Obtenir ou créer une instance DUM-E pour un chat spécifique"""
        if chat_id not in self.dum_e_instances:
            self.dum_e_instances[chat_id] = DUM_E(telegram_mode=True, chat_id=chat_id)
        return self.dum_e_instances[chat_id]

    def reset_conversation(self, chat_id):
        """Réinitialiser la conversation pour un chat"""
        if chat_id in self.dum_e_instances:
            del self.dum_e_instances[chat_id]

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour la commande /start"""
        chat_id = update.effective_chat.id

        # Salutations aléatoires
        salutations = [
            f"Salut {update.effective_user.first_name}! Je suis DUM-E v0.3. Prêt à t'aider 😄",
            f"Hey 👋 {update.effective_user.first_name}! DUM-E à ton service.",
            f"Yo! C'est DUM-E. Dis-moi ce que tu veux faire, {update.effective_user.first_name}.",
            f"Hello 😎 Je suis DUM-E version 0.3. Content de te voir!",
            f"Bonjour {update.effective_user.first_name}! Prêt pour bosser ensemble ?"
        ]

        welcome_message = random.choice(salutations)
        welcome_message += "\n\nTape /help pour voir toutes mes fonctionnalités."

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour la commande /help"""
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
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /status pour vérifier l'état du bot"""
        await update.message.reply_text("🤖 DUM-E est en ligne et opérationnel !")

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /stop pour arrêter une conversation"""
        chat_id = update.effective_chat.id
        self.reset_conversation(chat_id)
        await update.message.reply_text("🔄 Conversation réinitialisée. Tapez /start pour recommencer.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour les messages textuels"""
        chat_id = update.effective_chat.id
        user_message = update.message.text

        # Obtenir l'instance DUM-E pour ce chat
        dum_e_instance = self.get_dum_e_instance(chat_id)

        # Traiter le message via DUM-E
        response = await dum_e_instance.process_message(user_message)

        # Envoyer la réponse
        await update.message.reply_text(response)