from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
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

# Temporary storage for user messages
user_messages = {}

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # Initialize storage
    user_messages[user_id] = {"type": "", "category": "", "texts": []}

    intro_text = (
        "☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን፡፡☦️\n\n"
        "👋 ሰላም!\n"
        "እኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።\n"
        "እነዚያ መልዕክቶች ስም-አልባ ናቸው እና\n"
        "ማንነትህ በአስተዳዳሪዎች አይታይም።\n\n"
        "———\n\n"
        "👋 Hello!\n"
        "I am Korea_gbi_gubae_bot.\n"
        "Your messages are anonymous."
    )
    await update.message.reply_text(intro_text)

    keyboard = [
        [InlineKeyboardButton("Question", callback_data="type_question")],
        [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]
    ]
    await update.message.reply_text("Please choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- Inline button handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_messages:
        user_messages[user_id] = {"type": "", "category": "", "texts": []}

    # Type selection
    if data == "type_question":
        user_messages[user_id]["type"] = "Question"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"question_{opt}")] for opt in QUESTION_OPTIONS]
        await query.edit_message_text("Choose a question category:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "type_suggestion":
        user_messages[user_id]["type"] = "Suggestion"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"suggestion_{opt}")] for opt in SUGGESTION_OPTIONS]
        await query.edit_message_text("Choose a suggestion category:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Suggestion category
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
    
    # Question category
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
        combined_text = "\n".join(user_messages[user_id]["texts"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_type = user_messages[user_id]["type"]

        for admin_id in ADMIN_IDS:
            await context.bot.forward_message(
                chat_id=admin_id,
                from_chat_id=user_id,
                message_id=update.callback_query.message.message_id
            )
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 NEW MESSAGE\n🕒 Time: {timestamp}\n📂 Type: {message_type} - {user_messages[user_id]['category']}\n\n💬 Message:\n{combined_text}"
            )

        # Send outro to user
        outro_text = (
            "☦️\n🙏 Thank you!\n"
            "Your question/suggestion will be answered in upcoming discussions or sermons.\n"
            "Have a blessed time and stay tuned!\n\n"
            "———\n\n"
            "🙏 እናመሰግናለን!\n"
            "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
            "ቡሩክ ጊዜ ይቆዩ እና ይከታትሉ!\n☦️"
        )
        keyboard_restart = [[InlineKeyboardButton("/start", callback_data="restart")]]
        await context.bot.send_message(chat_id=user_id, text=outro_text, reply_markup=InlineKeyboardMarkup(keyboard_restart))
        user_messages.pop(user_id, None)

    # Cancel
    elif data == "cancel":
        await query.edit_message_text("We have cancelled your request. We are here if you need anything else.")
        user_messages.pop(user_id, None)
        keyboard = [
            [InlineKeyboardButton("Question", callback_data="type_question")],
            [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]
        ]
        await context.bot.send_message(user_id, "Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Restart from outro inline button
    elif data == "restart":
        await start(update, context)

# --- Collect text messages ---
async def collect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id in user_messages:
        user_messages[user_id]["texts"].append(text)
        # Do NOT send any confirmation message here (as requested)

# --- Main ---
def main():
    TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
