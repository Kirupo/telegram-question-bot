from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

# ================= CONFIG =================
TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"

ADMINS = [7348815216, 1974614381]

# ================= USER SESSION =================
class UserSession:
    def __init__(self):
        self.stage = "start"
        self.main_type = None
        self.sub_type = None
        self.messages = []
        self.last_message_id = None

QUESTION_SUBS = [
    "Prayer",
    "Confession",
    "Scripture/Bible Verse",
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

SUGGESTION_SUBS = [
    "General",
    "Discussion",
]

sessions = {}

def get_session(user_id):
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

# ================= KEYBOARDS =================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Question", callback_data="main_question")],
        [InlineKeyboardButton("Suggestion", callback_data="main_suggestion")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")],
    ])

def sub_keyboard(options):
    keyboard = []
    for opt in options:
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"sub_{opt}")])

    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)

def writing_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Done", callback_data="done")],
        [InlineKeyboardButton("Back", callback_data="back")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")],
    ])

def restart_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Restart", callback_data="restart")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    session.__init__()

    text = (
        "☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን፡፡☦️\n\n"
        "👋 ሰላም!\n"
        "እኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።\n"
        "መልዕክቶችዎ ስም-አልባ ናቸው።\n\n"
        "———\n\n"
        "👋 Hello!\n"
        "I am Korea_gbi_gubae_bot.\n"
        "Your messages are anonymous."
    )

    msg = await update.message.reply_text(text, reply_markup=main_keyboard())
    session.last_message_id = msg.message_id
    session.stage = "choose_main"

# ================= CALLBACK HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    session = get_session(user_id)
    data = query.data

    async def replace(text, keyboard):
        if session.last_message_id:
            try:
                await context.bot.delete_message(user_id, session.last_message_id)
            except:
                pass
        msg = await context.bot.send_message(user_id, text, reply_markup=keyboard)
        session.last_message_id = msg.message_id

    # -------- CANCEL --------
    if data == "cancel":
        await replace(
            "☦️\n🙏 Thank you!\nYour question/suggestion will be answered in upcoming discussions or sermons.\n\n"
            "———\n\n"
            "🙏 እናመሰግናለን!\n"
            "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
            "☦️",
            restart_keyboard(),
        )
        return

    # -------- RESTART --------
    if data == "restart":
        await start(update, context)
        return

    # -------- MAIN CHOICE --------
    if data == "main_question":
        session.main_type = "Question"
        session.stage = "choose_sub"
        await replace("Select a category:", sub_keyboard(QUESTION_SUBS))
        return

    if data == "main_suggestion":
        session.main_type = "Suggestion"
        session.stage = "choose_sub"
        await replace("Select a category:", sub_keyboard(SUGGESTION_SUBS))
        return

    # -------- SUB CHOICE --------
    if data.startswith("sub_"):
        session.sub_type = data.replace("sub_", "")
        session.stage = "writing"
        session.messages = []
        await replace(
            "✍️ Write your message below.\nYou may send multiple messages.\nPress *Done* when finished.",
            writing_keyboard(),
        )
        return

    # -------- BACK --------
    if data == "back":
        if session.stage == "writing":
            await replace("Select a category:", sub_keyboard(
                QUESTION_SUBS if session.main_type == "Question" else SUGGESTION_SUBS
            ))
            session.stage = "choose_sub"
        return

    # -------- DONE --------
    if data == "done":
        combined = "\n".join(session.messages).strip()
        if not combined:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        admin_text = (
            "📩 NEW MESSAGE\n"
            f"🕒 Time: {now}\n"
            f"📂 Type: {session.main_type} - {session.sub_type}\n\n"
            "💬 Message:\n"
            f"{combined}"
        )

        for admin in ADMINS:
            await context.bot.send_message(admin, admin_text)

        await replace(
            "☦️\n🙏 Thank you!\nYour question/suggestion will be answered in upcoming discussions or sermons.\n\n"
            "———\n\n"
            "🙏 እናመሰግናለን!\n"
            "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
            "☦️",
            restart_keyboard(),
        )
        return

# ================= MESSAGE HANDLER =================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)

    if session.stage == "writing":
        session.messages.append(update.message.text)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
