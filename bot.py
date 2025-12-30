from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

# ================= CONFIG =================
TOKEN = "BOT_TOKEN_HERE"
ADMIN_IDS = [123456789, 987654321]

# ================= DATA =================
QUESTION_CATEGORIES = [
    "Prayer", "Confession", "Scripture / Bible Verse", "Relationships",
    "Orthodox Practice", "Communion", "General Theology", "Fasting",
    "Sin", "Saints and Intercession", "Saint Mary", "Others"
]

SUGGESTION_CATEGORIES = ["Discussion", "General"]

user_sessions = {}

# ================= KEYBOARDS =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Question", callback_data="question")],
        [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")]
    ])

def done_cancel_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Done", callback_data="done")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions.pop(update.effective_user.id, None)

    intro_text = (
        "👋 ሰላም!\n"
        "እኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።\n"
        "እነዚያ መልዕክቶች ስም-አልባ ናቸው እና\n"
        "ማንነትህ በአስተዳዳሪዎች አይታይም።\n\n"
        "👋 Hello!\n"
        "I am Korea_gbi_gubae_bot.\n"
        "Your messages are anonymous."
    )

    await update.message.reply_text(intro_text, reply_markup=main_menu())

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    user_sessions.setdefault(user_id, {"type": "", "category": "", "messages": []})

    if data == "question":
        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f"q_{cat}")]
            for cat in QUESTION_CATEGORIES
        ]
        await query.edit_message_text(
            "Choose a question category:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data == "suggestion":
        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f"s_{cat}")]
            for cat in SUGGESTION_CATEGORIES
        ]
        await query.edit_message_text(
            "Choose a suggestion type:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith(("q_", "s_")):
        user_sessions[user_id]["type"] = "Question" if data.startswith("q_") else "Suggestion"
        user_sessions[user_id]["category"] = data[2:]

        await query.edit_message_text(
            "Please write your message below.\n"
            "Press ✅ Done when finished or ❌ Cancel to cancel.",
            reply_markup=done_cancel_menu(),
        )

    elif data == "done":
        session = user_sessions.get(user_id)
        if not session or not session["messages"]:
            await query.edit_message_text("No message received.")
            return

        combined = "\n".join(session["messages"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        admin_text = (
            "📩 NEW MESSAGE\n"
            f"🕒 Time: {timestamp}\n"
            f"📂 Type: {session['type']} – {session['category']}\n\n"
            "💬 Message:\n"
            f"{combined}"
        )

        for admin in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin, text=admin_text)

        await query.edit_message_text(
            "☦️\n"
            "🙏 Thank you!\n"
            "Your question/suggestion will be answered in upcoming discussions or sermons.\n"
            "Have a blessed time and stay tuned!\n\n"
            "———\n\n"
            "🙏 እናመሰግናለን!\n"
            "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
            "ቡሩክ ጊዜ ይቆዩ እና ይከታትለው!\n"
            "☦️",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Start Again", callback_data="restart")]
            ])
        )

        user_sessions.pop(user_id, None)

    elif data == "cancel":
        user_sessions.pop(user_id, None)
        await query.edit_message_text(
            "☦️\n"
            "❌ Your message has been cancelled.\n"
            "Have a blessed time.\n\n"
            "———\n\n"
            "❌ መልእክትዎ ተሰርዟል።\n"
            "የተባረከ ጊዜ ይሁንላችሁ።\n"
            "☦️",
            reply_markup=main_menu(),
        )

    elif data == "restart":
        await start(update, context)

# ================= TEXT COLLECTOR =================
async def collect_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_sessions:
        user_sessions[user_id]["messages"].append(update.message.text)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_text))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
