from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

# Replace with your Telegram ID to receive messages
ADMIN_ID = 1974614381

# Options for user input
options_keyboard = [["Question", "Suggestion", "Idea"], ["Cancel"]]
done_keyboard = [["Done", "Cancel"]]

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(options_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Hello! What do you want to send?", reply_markup=keyboard
    )

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    chat_id = update.message.chat_id

    # Cancel button
    if text.lower() == "cancel":
        keyboard = ReplyKeyboardMarkup(options_keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Operation cancelled. Choose again:", reply_markup=keyboard
        )
        return

    # Check if user pressed Done
    if text.lower() == "done":
        keyboard = ReplyKeyboardMarkup(options_keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Thank you! Choose what you want to send next:", reply_markup=keyboard
        )
        return

    # Send message to admin
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"From: {user.username or user.first_name}\nTime: {timestamp}\nType: {text}",
    )

    # Ask if they have more
    keyboard = ReplyKeyboardMarkup(done_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Do you have any more questions, suggestions, or ideas?",
        reply_markup=keyboard,
    )

# Main function
def main():
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
