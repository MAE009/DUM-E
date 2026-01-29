from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from core.dum_e import DUM_E

# Stocker les instances DUM-E par utilisateur
dum_e_instances = {}


async def setup_handlers(app):
    """Configurer les handlers Telegram"""
    from telegram.ext import CommandHandler, MessageHandler, filters

    # Commandes
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("list_agenda", agenda_command))
    app.add_handler(CommandHandler("cancel", cancel_command))  # NOUVEAU

    # Messages texte
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    # Gestion d'erreurs
    app.add_error_handler(error_handler)


def get_dum_e_instance(chat_id: int, username: str = ""):
    """Obtenir ou créer une instance DUM-E pour un utilisateur"""
    if chat_id not in dum_e_instances:
        # Créer une nouvelle instance DUM-E pour cet utilisateur
        dum_e_instances[chat_id] = DUM_E(
            telegram_mode=True,
            chat_id=chat_id
        )
        # Définir le nom d'utilisateur si fourni
        if username:
            dum_e_instances[chat_id].username = username
    return dum_e_instances[chat_id]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour /start"""
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Créer une instance DUM-E pour cet utilisateur
    dum_e_instance = get_dum_e_instance(chat_id, user.first_name)

    # Envoyer le message de bienvenue
    welcome = dum_e_instance.salutation()
    await update.message.reply_text(
        f"{welcome}\n\n"
        "Tape /help pour voir toutes mes fonctionnalités."
    )


async def agenda_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour /help"""
    chat_id = update.effective_chat.id
    dum_e_instance = get_dum_e_instance(chat_id)

    # Récupérer le texte d'aide
    agenda_list = await dum_e_instance.agenda()
    await update.message.reply_text(agenda_list, parse_mode='Markdown')




async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour /help"""
    chat_id = update.effective_chat.id
    dum_e_instance = get_dum_e_instance(chat_id)

    # Récupérer le texte d'aide
    help_text = await dum_e_instance.handle.handle_system_async("help")
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour /status"""
    chat_id = update.effective_chat.id
    dum_e_instance = get_dum_e_instance(chat_id)

    # Récupérer le statut via handle_debug_async
    status_text = await dum_e_instance.handle.handle_debug_async("status")
    await update.message.reply_text(status_text)


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour /stop"""
    chat_id = update.effective_chat.id
    if chat_id in dum_e_instances:
        # Réinitialiser l'instance
        dum_e_instances[chat_id].game_state = False
        dum_e_instances[chat_id].game.reset_game()

    await update.message.reply_text(
        "🔄 Conversation réinitialisée. "
        "Tape /start pour recommencer."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gérer tous les messages texte"""
    chat_id = update.effective_chat.id
    user_message = update.message.text

    # Obtenir l'instance DUM-E pour cet utilisateur
    dum_e_instance = get_dum_e_instance(chat_id)


    # Traiter le message via DUM-E
    response = await dum_e_instance.process_message(user_message, chat_id)

    # Envoyer la réponse
    await update.message.reply_text(response)



# AJOUTEZ AUSSI UN HANDLER POUR ANNULER
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour annuler une action en cours"""
    chat_id = update.effective_chat.id

    # Nettoyer les conversations en cours
    dum_e_instance = get_dum_e_instance(chat_id)
    if hasattr(dum_e_instance.handle, '_cleanup_conversation'):
        dum_e_instance.handle._cleanup_conversation(chat_id)

    await update.message.reply_text("✅ Action annulée. Tape /help pour les commandes.")



async def error_handler(update: Update, context: CallbackContext):
    """Gérer les erreurs"""
    error = context.error
    print(f"❌ Erreur Telegram: {error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Une erreur est survenue. Veuillez réessayer."
        )