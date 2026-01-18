import os
import asyncio
import nest_asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv

# Appliquer nest_asyncio pour Flask + Telegram
nest_asyncio.apply()

# Charger les variables d'environnement
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN manquant dans .env")

# Créer l'app Flask
flask_app = Flask(__name__)


@flask_app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 DUM-E Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 600px;
                margin: 0 auto;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
            }
            .status {
                font-size: 1.5em;
                margin: 20px 0;
                padding: 10px;
                background: rgba(0, 255, 0, 0.2);
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 DUM-E v0.3</h1>
            <div class="status">✅ Bot Telegram en ligne !</div>
            <p>Assistant intelligent basé sur des règles</p>
            <p>Connectez-vous sur Telegram pour interagir</p>
        </div>
    </body>
    </html>
    """


@flask_app.route('/health')
def health():
    return "🟢 Healthy", 200


@flask_app.route('/status')
def status():
    return {
        "status": "online",
        "service": "DUM-E Telegram Bot",
        "version": "0.3",
        "endpoints": ["/", "/health", "/status"]
    }


# Import des handlers Telegram
from core.telegram_handler import setup_handlers


async def run():
    """Fonction principale async pour lancer le bot"""
    print("🤖 Initialisation de DUM-E Telegram Bot...")
    print(f"✅ Token: {TELEGRAM_TOKEN[:10]}...")

    # Créer l'application Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Configurer les handlers
    await setup_handlers(app)

    # Initialiser et démarrer
    await app.initialize()
    await app.start()
    print("✅ Bot Telegram initialisé")

    # Démarrer le polling
    await app.updater.start_polling()
    print("🔍 Polling démarré - Bot prêt à recevoir des messages")

    # Démarrer Flask dans un thread séparé
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Serveur web sur le port {port}")

    # Exécuter Flask dans l'event loop
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: flask_app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False
        )
    )


if __name__ == '__main__':
    # Lancer l'app asynchrone
    asyncio.run(run())