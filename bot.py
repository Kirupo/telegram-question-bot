from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Replace with your Telegram admin IDs
ADMIN_IDS = [7348815216, 1974614381]

# Question and suggestion options
QUESTION_OPTIONS = [
    "Prayer", "Confession", "Scripture/Bible Verse", "Relationships", "Orthodox Practice",
    "Communion", "General Theology", "Fasting", "Sin", "Saints and Intercession",
    "Saint Mary", "Others"
]
SUGGESTION_OPTIONS = ["Discussion", "General"]

# Store user messages temporarily
user_messages = {}

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Question", callback_data="type_question")],
                [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]]
    intro_text = (
        "☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን፡፡☦️\n\n"
        "👋 ሰላም!\n"
        "እኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።\n"
        "መልዕክቶችህ ስም-አልባ ናቸው እና ማንነትህ በአስተዳዳሪዎች አይታይም።\n\n"
        "———\n\n"
        "👋 Hello!\n"
        "I am Korea_gbi_gubae_bot.\n"
        "Your messages are anonymous."
    )
    await update.message.reply_text(intro_text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- Handle Inline Buttons ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_messages:
        user_messages[user_id] = {"type": "", "category": "", "texts": []}

    # Select Type
    if data == "type_question":
        user_messages[user_id]["type"] = "Question"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"question_{opt}")] for opt in QUESTION_OPTIONS]
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_start"),
                         InlineKeyboardButton("Cancel", callback_data="cancel")])
        await query.edit_message_text("Choose a question category:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "type_suggestion":
        user_messages[user_id]["type"] = "Suggestion"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"suggestion_{opt}")] for opt in SUGGESTION_OPTIONS]
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_start"),
                         InlineKeyboardButton("Cancel", callback_data="cancel")])
        await query.edit_message_text("Choose a suggestion category:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Suggestion category selected
    elif data.startswith("suggestion_"):
        category = data.split("_")[1]
        user_messages[user_id]["category"] = category
        keyboard = [
            [InlineKeyboardButton("Done", callback_data="done")],
            [InlineKeyboardButton("Back", callback_data="type_suggestion")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            f"Write your {category} suggestion below. Press Done when finished or Cancel to cancel.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Question category selected
    elif data.startswith("question_"):
        category = data.split("_")[1]
        user_messages[user_id]["category"] = category
        keyboard = [
            [InlineKeyboardButton("Done", callback_data="done")],
            [InlineKeyboardButton("Back", callback_data="type_question")],
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
                text=f"📩 NEW MESSAGE\n🕒 Time: {timestamp}\n📂 Type: {message_type} - {user_messages[user_id]['category']}\n\n💬 Message:\n{combined_text}\n☦️\n🙏 Thank you!\nYour question/suggestion will be answered in upcoming discussions or sermons.\nHave a blessed time and stay tuned!\n\n———\n\n🙏 እናመሰግናለን!\nጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\nቡሩክ ጊዜ ይቆዩ እና ይከታትሉ!\n☦️"
            )

        user_messages.pop(user_id, None)

        keyboard = [[InlineKeyboardButton("/Start", callback_data="restart")]]
        await context.bot.send_message(
            chat_id=user_id,
            text="Press /Start to begin again:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Cancel
    elif data == "cancel":
        await query.edit_message_text("We have cancelled your request. We are here if you need anything else.")
        user_messages.pop(user_id, None)
        keyboard = [[InlineKeyboardButton("Question", callback_data="type_question")],
                    [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]]
        await context.bot.send_message(
            chat_id=user_id,
            text="Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Back to start
    elif data == "back_to_start" or data == "restart":
        user_messages.pop(user_id, None)
        keyboard = [[InlineKeyboardButton("Question", callback_data="type_question")],
                    [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]]
        await context.bot.send_message(
            chat_id=user_id,
            text="Please choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# --- Collect user text messages ---
async def collect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id in user_messages:
        user_messages[user_id]["texts"].append(text)

# --- Main Function ---
def main():
    TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
