import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
from dotenv import load_dotenv
import datetime
import random

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()


class DUM_E_Bot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN non trouvé dans .env")
            raise ValueError("TELEGRAM_BOT_TOKEN manquant")

        # Créer l'application
        self.application = Application.builder().token(self.token).build()

        # Configurer les handlers
        self.setup_handlers()

        # Stockage simple en mémoire (pour l'exemple)
        self.user_data = {}

    def setup_handlers(self):
        """Configurer les handlers de commandes et messages"""

        # Commandes
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(CommandHandler("stop", self.stop))
        self.application.add_handler(CommandHandler("jeu", self.jeu))

        # Messages textuels
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))

        # Gestion des erreurs
        self.application.add_error_handler(self.error_handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour /start"""
        user = update.effective_user
        salutations = [
            f"Salut {user.first_name} ! Je suis DUM-E v0.3 🤖",
            f"Hey 👋 {user.first_name} ! DUM-E à ton service.",
            f"Bonjour {user.first_name} ! Prêt pour bosser ensemble ? 😊"
        ]

        welcome = random.choice(salutations)
        help_text = "\n\nTape /help pour voir toutes mes fonctionnalités."

        await update.message.reply_text(welcome + help_text)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour /help"""
        help_text = """
🤖 *COMMANDES DUM-E*

*Commandes de base*
/start - Démarrer le bot
/help - Afficher cette aide
/status - État du bot
/stop - Réinitialiser la conversation
/jeu - Jouer à un jeu

*Commandes texte*
• "salut", "bonjour" - Saluer
• "date" - Date actuelle
• "heure" - Heure actuelle
• "je m'appelle [nom]" - Définir ton nom
• "mon nom" - Afficher ton nom
• "pile" ou "face" - Jouer à pile ou face
• "rappel [quoi] [quand]" - Créer un rappel
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour /status"""
        await update.message.reply_text("✅ DUM-E est en ligne et opérationnel !")

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour /stop"""
        user_id = update.effective_user.id
        if user_id in self.user_data:
            del self.user_data[user_id]
        await update.message.reply_text("🔄 Conversation réinitialisée. Tape /start pour recommencer.")

    async def jeu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour /jeu"""
        await update.message.reply_text(
            "🎮 Veux-tu jouer à :\n"
            "• Pile ou Face : tape 'pile' ou 'face'\n"
            "• Devine le nombre : tape 'nombre'"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gérer les messages textuels"""
        user_message = update.message.text.lower()
        user_id = update.effective_user.id
        response = ""

        logger.info(f"Message de {user_id}: {user_message}")

        # Gestion des salutations
        if any(word in user_message for word in ["salut", "bonjour", "hello", "hi", "coucou", "yo"]):
            response = f"Salut {update.effective_user.first_name} ! 😊"

        # Date
        elif "date" in user_message:
            today = datetime.datetime.now()
            response = f"Nous sommes le {today.strftime('%d/%m/%Y')}"

        # Heure
        elif "heure" in user_message or "horaire" in user_message:
            now = datetime.datetime.now()
            response = f"Il est {now.strftime('%H:%M:%S')}"

        # Nom utilisateur
        elif "je m'appelle" in user_message:
            parts = user_message.split("je m'appelle")
            if len(parts) > 1:
                name = parts[1].strip()
                self.user_data[user_id] = {'name': name}
                response = f"Enchanté {name} ! Je m'appelle DUM-E 🤖"
            else:
                response = "Format: 'je m'appelle [ton nom]'"

        elif "mon nom" in user_message:
            if user_id in self.user_data and 'name' in self.user_data[user_id]:
                response = f"Tu t'appelles {self.user_data[user_id]['name']}"
            else:
                response = "Je ne connais pas encore ton nom. Dis-moi avec 'je m'appelle [ton nom]'"

        # Jeu pile ou face
        elif "pile" in user_message or "face" in user_message:
            result = random.choice(["Pile", "Face"])
            user_choice = "pile" if "pile" in user_message else "face"

            if user_choice == result.lower():
                response = f"🎉 Bravo ! C'est {result}. Tu as gagné !"
            else:
                response = f"😅 Dommage ! C'est {result}. Tu as perdu !"

            # Proposer de rejouer
            response += "\n\nEncore une fois ? 'pile' ou 'face'"

        # Rappels
        elif "rappel" in user_message:
            parts = user_message.split("rappel", 1)
            if len(parts) > 1 and parts[1].strip():
                reminder_text = parts[1].strip()
                response = f"✅ Rappel enregistré : '{reminder_text}'"
            else:
                response = "Format: 'rappel [ce que tu dois faire] [quand]'"

        # Si rien ne correspond
        else:
            response = (
                "Je n'ai pas compris. 🤔\n"
                "Essaie :\n"
                "• 'salut' pour me dire bonjour\n"
                "• 'date' pour la date\n"
                "• 'heure' pour l'heure\n"
                "• /help pour plus d'options"
            )

        await update.message.reply_text(response)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gérer les erreurs"""
        logger.error(f"Erreur: {context.error}")

        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Une erreur est survenue. Veuillez réessayer."
            )

    def run(self):
        """Démarrer le bot"""
        logger.info("🤖 Démarrage de DUM-E Telegram Bot...")
        logger.info(f"✅ Token: {self.token[:10]}...")

        # Lancer le bot
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )


def main():
    """Fonction principale"""
    try:
        bot = DUM_E_Bot()
        bot.run()
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        print(f"❌ Erreur: {e}")
        print("➡️ Vérifiez votre token Telegram dans le fichier .env")


if __name__ == "__main__":
    main()