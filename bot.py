from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
import time
from datetime import datetime

TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
ADMIN_ID = 1974614381

# Keyboard buttons
menu_buttons = [['Question', 'Suggestion', 'Idea']]
done_button = [['Done', 'Cancel']]

# Track current conversation type per user
user_type = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome! Please choose one:",
        reply_markup=ReplyKeyboardMarkup(menu_buttons, one_time_keyboard=True)
    )

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    text = update.message.text

    # Handle menu selection
    if text in ['Question', 'Suggestion', 'Idea']:
        user_type[user_id] = text
        update.message.reply_text(
            f"You chose {text}. Send your message below.",
            reply_markup=ReplyKeyboardMarkup(done_button, one_time_keyboard=True)
        )
        return

    # Handle Done / Cancel
    if text == 'Done':
        update.message.reply_text(
            "Do you have any more questions, suggestions, or ideas?",
            reply_markup=ReplyKeyboardMarkup(menu_buttons, one_time_keyboard=True)
        )
        if user_id in user_type:
            del user_type[user_id]
        return
    elif text == 'Cancel':
        update.message.reply_text(
            "Conversation cancelled.",
            reply_markup=ReplyKeyboardMarkup(menu_buttons, one_time_keyboard=True)
        )
        if user_id in user_type:
            del user_type[user_id]
        return

    # Forward message to admin with timestamp
    if user_id in user_type:
        msg_type = user_type[user_id]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"[{timestamp}] {msg_type} from {name} (@{username}):\n{text}"
        )

# Retry loop to avoid crashes
while True:
    try:
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        print("Bot is running...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print("Network error:", e)
        print("Retrying in 10 seconds...")
        time.sleep(10)
