from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

# Replace these with your Telegram IDs
ADMIN_IDS = [7348815216, 1974614381]  # You can add two admin IDs

# Options
suggestion_keyboard = [
    [InlineKeyboardButton("Discussion", callback_data="suggestion_discussion")],
    [InlineKeyboardButton("General", callback_data="suggestion_general")],
    [InlineKeyboardButton("Cancel", callback_data="cancel")],
]

question_keyboard = [
    [InlineKeyboardButton("Prayer", callback_data="question_prayer")],
    [InlineKeyboardButton("Confession", callback_data="question_confession")],
    [InlineKeyboardButton("Scripture/Bible Verse", callback_data="question_scripture")],
    [InlineKeyboardButton("Relationships", callback_data="question_relationships")],
    [InlineKeyboardButton("Orthodox Practice", callback_data="question_orthodox")],
    [InlineKeyboardButton("Communion", callback_data="question_communion")],
    [InlineKeyboardButton("General Theology", callback_data="question_general_theology")],
    [InlineKeyboardButton("Fasting", callback_data="question_fasting")],
    [InlineKeyboardButton("Sin", callback_data="question_sin")],
    [InlineKeyboardButton("Saints & Intercession", callback_data="question_saints")],
    [InlineKeyboardButton("Saint Mary", callback_data="question_mary")],
    [InlineKeyboardButton("Others", callback_data="question_others")],
    [InlineKeyboardButton("Cancel", callback_data="cancel")],
]

done_keyboard = [
    [InlineKeyboardButton("Done", callback_data="done")],
    [InlineKeyboardButton("Cancel", callback_data="cancel")],
]

# Store user messages temporarily
user_data = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data[user.id] = {"type": None, "messages": []}
    await update.message.reply_text(
        "Hello 👋\nWelcome to 📖 Korea_gbi_gubae_bot\nThis bot is completely anonymous.\n\nPlease choose:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Question", callback_data="type_question")],
            [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")],
        ]),
    )

# Handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    # Cancel
    if query.data == "cancel":
        user_data[user.id] = {"type": None, "messages": []}
        await query.edit_message_text(
            "Your request has been cancelled. Choose again:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Question", callback_data="type_question")],
                [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")],
            ]),
        )
        return

    # Choosing type
    if query.data.startswith("type_"):
        type_chosen = query.data.split("_")[1]
        user_data[user.id]["type"] = type_chosen
        if type_chosen == "question":
            await query.edit_message_text(
                "Please choose a category for your question:",
                reply_markup=InlineKeyboardMarkup(question_keyboard)
            )
        elif type_chosen == "suggestion":
            await query.edit_message_text(
                "Please choose a category for your suggestion:",
                reply_markup=InlineKeyboardMarkup(suggestion_keyboard)
            )
        return

    # Choosing suggestion category
    if query.data.startswith("suggestion_"):
        user_data[user.id]["current_category"] = query.data
        await query.edit_message_text(
            "Please type your suggestion now. When done, press Done.",
            reply_markup=InlineKeyboardMarkup(done_keyboard)
        )
        return

    # Choosing question category
    if query.data.startswith("question_"):
        user_data[user.id]["current_category"] = query.data
        await query.edit_message_text(
            "Please type your question now. When done, press Done.",
            reply_markup=InlineKeyboardMarkup(done_keyboard)
        )
        return

    # Done
    if query.data == "done":
        messages = user_data[user.id]["messages"]
        category = user_data[user.id].get("current_category", "N/A")
        type_ = user_data[user.id].get("type", "N/A")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = "\n".join(messages)

        send_text = f"📩 NEW MESSAGE\n🕒 Time: {timestamp}\n📂 Type: {type_.capitalize()}\n💬 Category: {category}\n\n💬 Message:\n{full_message}"

        for admin_id in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin_id, text=send_text)

        # Reset user data
        user_data[user.id] = {"type": None, "messages": []}

        await query.edit_message_text("Thank you 🙏. Have a nice day!")
        return

# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    if user.id not in user_data:
        user_data[user.id] = {"type": None, "messages": []}

    # Only store message if a type/category is chosen
    if user_data[user.id].get("type") and user_data[user.id].get("current_category"):
        user_data[user.id]["messages"].append(text)
        await update.message.reply_text("Message recorded. Press Done when finished or Cancel to discard.")
    else:
        await update.message.reply_text("Please choose Question or Suggestion first using the buttons.")

# Main
def main():
    TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
