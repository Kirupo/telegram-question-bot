from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from datetime import datetime

# Replace with your Telegram admin IDs
ADMIN_IDS = [7348815216, 1974614381]

# Options
SUGGESTION_OPTIONS = ["Discussion", "General"]
QUESTION_OPTIONS = [
    "Prayer", "Confession", "Scripture/Bible Verse", "Relationships", "Orthodox Practice",
    "Communion", "General Theology", "Fasting", "Sin", "Saints and Intercession",
    "Saint Mary", "Others"
]

# To store user messages temporarily
user_messages = {}

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I’m Korea_gbi_gubae_bot. Your messages are anonymous."
    )
    keyboard = [
        [InlineKeyboardButton("Question", callback_data="type_question")],
        [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]
    ]
    await update.message.reply_text(
        "Please choose an option:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Handle inline button presses ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # Initialize user message storage
    if user_id not in user_messages:
        user_messages[user_id] = {"type": "", "category": "", "texts": []}

    # Choose type
    if data == "type_question":
        user_messages[user_id]["type"] = "Question"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"question_{opt}")] for opt in QUESTION_OPTIONS]
        await query.edit_message_text("Choose a question category:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "type_suggestion":
        user_messages[user_id]["type"] = "Suggestion"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"suggestion_{opt}")] for opt in SUGGESTION_OPTIONS]
        await query.edit_message_text("Choose a suggestion category:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Choose suggestion category
    elif data.startswith("suggestion_"):
        category = data.split("_")[1]
        user_messages[user_id]["category"] = category
        keyboard = [
            [InlineKeyboardButton("Done", callback_data="done")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            f"Write your {category} suggestion below. Press Done when finished or Cancel to cancel.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Choose question category
    elif data.startswith("question_"):
        category = data.split("_")[1]
        user_messages[user_id]["category"] = category
        keyboard = [
            [InlineKeyboardButton("Done", callback_data="done")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            f"Write your {category} question below. Press Done when finished or Cancel to cancel.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Done
    elif data == "done":
        if not user_messages[user_id]["texts"]:
            await query.edit_message_text("No message was written. Operation cancelled.")
            user_messages.pop(user_id, None)
        else:
            combined_text = "\n".join(user_messages[user_id]["texts"])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_type = user_messages[user_id]["type"]

            # Forward messages to admins
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 NEW MESSAGE\n🕒 Time: {timestamp}\n📂 Type: {message_type} - {user_messages[user_id]['category']}\n\n💬 Message:\n{combined_text}"
                )

            # Send thank-you message to user
            await query.edit_message_text(
                f"☦️\n🙏 Thank you!\nYour question/suggestion will be answered in upcoming discussions or sermons.\nHave a blessed time and stay tuned!\n\n———\n\n🙏 እናመሰግናለን!\nጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\nቡሩክ ጊዜ ይቆዩ እና ይከታትሉ!"
            )

            user_messages.pop(user_id, None)

        # Show main menu again
        keyboard = [
            [InlineKeyboardButton("Question", callback_data="type_question")],
            [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]
        ]
        await context.bot.send_message(
            chat_id=user_id,
            text="Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Cancel
    elif data == "cancel":
        await query.edit_message_text("We have cancelled your request. We are here if you need anything else.")
        user_messages.pop(user_id, None)
        keyboard = [
            [InlineKeyboardButton("Question", callback_data="type_question")],
            [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]
        ]
        await context.bot.send_message(
            chat_id=user_id,
            text="Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

# --- Collect text messages ---
async def collect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id in user_messages:
        user_messages[user_id]["texts"].append(text)
        # Do not send "Message saved" reply anymore

# --- Main ---
def main():
    TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"  # <-- Replace with your bot token
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_message))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.COMMAND, lambda update, context: update.message.reply_text("Use /start to begin.")))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
