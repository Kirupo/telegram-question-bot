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

# ================== CONFIG ==================
TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
ADMIN_IDS = [7348815216, 1974614381]  # replace with your Telegram ID(s)

QUESTION_OPTIONS = [
    "Prayer",
    "Confession",
    "Scripture / Bible Verse",
    "Relationships",
    "Orthodox Practice",
    "Communion",
    "General Theology",
    "Fasting",
    "Sin",
    "Saints and Intercession",
    "Saint Mary",
    "Others",
]

SUGGESTION_OPTIONS = ["Discussion", "General"]

# Store user states
user_data_store = {}

# ================== TEXTS ==================
INTRO_TEXT = (
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

THANK_YOU_TEXT = (
    "☦️\n"
    "🙏 Thank you!\n"
    "Your question/suggestion will be answered in upcoming discussions or sermons.\n"
    "Have a blessed time and stay tuned!\n\n"
    "———\n\n"
    "🙏 እናመሰግናለን!\n"
    "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
    "ቡሩክ ጊዜ ይቆዩ እና ይከታትሉ!\n"
    "☦️"
)

CANCEL_TEXT = (
    "☦️\n"
    "❌ Your message has been cancelled.\n"
    "Have a blessed time.\n\n"
    "———\n\n"
    "❌ መልእክትዎ ተሰርዟል።\n"
    "የተባረከ ጊዜ ይሁንላችሁ።\n"
    "☦️"
)

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store.pop(user_id, None)

    keyboard = [
        [InlineKeyboardButton("❓ Question", callback_data="type_question")],
        [InlineKeyboardButton("💡 Suggestion", callback_data="type_suggestion")],
    ]

    await update.message.reply_text(INTRO_TEXT)
    await update.message.reply_text(
        "Please choose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if user_id not in user_data_store:
        user_data_store[user_id] = {"type": "", "category": "", "texts": []}

    if data == "type_question":
        user_data_store[user_id]["type"] = "Question"
        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"q_{opt}")]
            for opt in QUESTION_OPTIONS
        ]
        await query.edit_message_text(
            "Choose a question category:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data == "type_suggestion":
        user_data_store[user_id]["type"] = "Suggestion"
        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"s_{opt}")]
            for opt in SUGGESTION_OPTIONS
        ]
        await query.edit_message_text(
            "Choose a suggestion category:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith(("q_", "s_")):
        category = data.split("_", 1)[1]
        user_data_store[user_id]["category"] = category

        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="done")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            f"Write your {category} message below.\n"
            "Press Done when finished or Cancel to cancel.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data == "done":
        stored = user_data_store.get(user_id)
        if not stored or not stored["texts"]:
            await query.edit_message_text("No message was written.")
            return

        text = "\n".join(stored["texts"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for admin in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin,
                text=(
                    "📩 NEW MESSAGE\n"
                    f"🕒 {timestamp}\n"
                    f"📂 {stored['type']} - {stored['category']}\n\n"
                    f"{text}"
                ),
            )

        await query.edit_message_text(THANK_YOU_TEXT)

        start_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔄 Start Again", callback_data="restart")]]
        )
        await context.bot.send_message(
            chat_id=user_id,
            text="",
            reply_markup=start_keyboard,
        )

        user_data_store.pop(user_id, None)

    elif data == "cancel":
        await query.edit_message_text(CANCEL_TEXT)
        user_data_store.pop(user_id, None)

    elif data == "restart":
        await start(update, context)


async def collect_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data_store:
        user_data_store[user_id]["texts"].append(update.message.text)
        await update.message.reply_text(
            "✍️ Message saved. Continue typing or press Done."
        )


# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_text))

    print("✅ Bot running")
    app.run_polling()


if __name__ == "__main__":
    main()
