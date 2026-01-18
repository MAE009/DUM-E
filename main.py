import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from bot.telegram_handler import TelegramHandler

# Charger les variables d'environnement
load_dotenv()


class DUM_E_Bot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            print("❌ ERREUR: TELEGRAM_BOT_TOKEN non trouvé dans .env")
            print("➡️ Créez un fichier .env avec: TELEGRAM_BOT_TOKEN=votre_token_ici")
            exit(1)

        self.application = Application.builder().token(self.token).build()

        # Initialiser le gestionnaire Telegram
        self.telegram_handler = TelegramHandler(self.application)

        # Configurer les handlers
        self.setup_handlers()

    def setup_handlers(self):
        """Configurer les handlers de commandes et messages"""
        # Commandes
        self.application.add_handler(CommandHandler("start", self.telegram_handler.start_command))
        self.application.add_handler(CommandHandler("help", self.telegram_handler.help_command))
        self.application.add_handler(CommandHandler("status", self.telegram_handler.status_command))
        self.application.add_handler(CommandHandler("stop", self.telegram_handler.stop_command))

        # Messages textuels
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.telegram_handler.handle_message
        ))

    def run(self):
        """Démarrer le bot"""
        print("🤖 Démarrage de DUM-E Telegram Bot...")
        print(f"✅ Token chargé: {self.token[:10]}...")
        self.application.run_polling(allowed_updates=None)


if __name__ == "__main__":
    bot = DUM_E_Bot()
    bot.run()