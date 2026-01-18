import os
import asyncio
import nest_asyncio
from flask import Flask
from telegram.ext import Application
from telegram.error import TelegramError
from dotenv import load_dotenv

# Appliquer nest_asyncio
nest_asyncio.apply()

# Charger les variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN manquant")

# Flask app
flask_app = Flask(__name__)


@flask_app.route('/')
def home():
    return "✅ DUM-E Bot v0.3 en ligne !"


@flask_app.route('/health')
def health():
    return "🟢 Healthy", 200


@flask_app.route('/status')
def status():
    return {"status": "online", "service": "DUM-E"}


async def run_bot():
    """Fonction pour exécuter le bot Telegram"""
    print("🤖 Initialisation du bot Telegram...")

    # Créer l'application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Importer et configurer les handlers
    from core.telegram_handler import setup_handlers
    await setup_handlers(application)

    print("✅ Bot initialisé, démarrage du polling...")

    # Démarrer le bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print("🔍 Bot en écoute...")

    # Garder le bot en cours d'exécution
    await asyncio.Event().wait()


async def run_flask():
    """Fonction pour exécuter Flask"""
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Démarrage du serveur web sur le port {port}")

    # Configurer Flask pour qu'il tourne dans asyncio
    import threading
    from werkzeug.serving import make_server

    class FlaskThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.daemon = True
            self.server = make_server('0.0.0.0', port, flask_app, threaded=True)

        def run(self):
            print(f"🚀 Flask démarré sur http://0.0.0.0:{port}")
            self.server.serve_forever()

        def shutdown(self):
            self.server.shutdown()

    flask_thread = FlaskThread()
    flask_thread.start()

    # Attendre indéfiniment
    await asyncio.Event().wait()


async def main():
    """Fonction principale asynchrone"""
    print("🚀 Démarrage de DUM-E...")

    # Lancer Flask et le bot en parallèle
    flask_task = asyncio.create_task(run_flask())
    bot_task = asyncio.create_task(run_bot())

    # Attendre que l'une des tâches échoue
    done, pending = await asyncio.wait(
        [flask_task, bot_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Annuler les tâches restantes
    for task in pending:
        task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Arrêt de DUM-E...")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()