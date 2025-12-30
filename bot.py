import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ---------------------------- CONFIGURATION ----------------------------
TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"

# Admin IDs: replace with your Telegram numeric IDs
ADMIN_IDS = [7348815216, 1974614381]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------- BOT STATE CLASS ----------------------------
class UserSession:
    """Tracks each user's session state"""
    def __init__(self):
        self.stage = "start"  # start, choosing_main, choosing_sub, writing, finished
        self.answers = []
        self.current_option = None
        self.current_suboption = None
        self.last_message_id = None

        # Main options
        self.main_options = ["Question", "Suggestion"]

        # Sub-options for Question
        self.sub_options_question = [
            "Prayer", "Confession", "Scripture/Bible verse", "Relationships",
            "Orthodox practice", "Communion", "General theology", "Fasting",
            "Sin", "Saints and intercession", "Saint Mary", "Others"
        ]

        # Sub-options for Suggestion
        self.sub_options_suggestion = ["General", "Discussion"]

sessions = {}

# ---------------------------- INLINE KEYBOARD HELPERS ----------------------------
def main_options_inline():
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"main_{opt.lower()}")] for opt in ["Question", "Suggestion"]]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)

def sub_options_inline(session: UserSession):
    if session.current_option == "question":
        options = session.sub_options_question
    elif session.current_option == "suggestion":
        options = session.sub_options_suggestion
    else:
        options = []

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"sub_{idx}")] for idx, opt in enumerate(options)]
    keyboard.append([InlineKeyboardButton("Back", callback_data="back"),
                     InlineKeyboardButton("Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)

def restart_inline():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Restart", callback_data="restart")]])

# ---------------------------- MESSAGE FORMATTING ----------------------------
def format_message(user_text, main_type, sub_type):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""📩 NEW MESSAGE
🕒 Time: {now}
📂 Type: {main_type} - {sub_type}

💬 Message:
{user_text}"""

# ---------------------------- HANDLERS ----------------------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    session = sessions[user_id]
    session.stage = "choosing_main"
    session.answers = []

    # Send intro message
    intro_text = (
        "☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን፡፡☦️\n\n"
        "👋 ሰላም!\n"
        "እኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።\n"
        "እነዚያ መልዕክቶች ስም-አልባ ናቸው እና\n"
        "ማንነትህ በአስተዳዳሪዎች አይታይም።\n\n"
        "———\n\n"
        "👋 Hello!\n"
        "I am Korea_gbi_gubae_bot.\n"
        "Your messages are anonymous.\n\n"
        "Please choose an option to continue:"
    )

    msg = await update.message.reply_text(intro_text, reply_markup=main_options_inline())
    session.last_message_id = msg.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in sessions:
        sessions[user_id] = UserSession()
    session = sessions[user_id]

    # Delete last inline for clean interface except for intro
    if session.last_message_id and session.stage not in ["start", "choosing_main"]:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
        except:
            pass

    data = query.data

    # ----------------- CANCEL -----------------
    if data == "cancel":
        session.stage = "finished"
        outro_text = (
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
        msg = await context.bot.send_message(chat_id=user_id, text=outro_text, reply_markup=restart_inline())
        session.last_message_id = msg.message_id
        session.answers = []
        return

    # ----------------- RESTART -----------------
    if data == "restart":
        # Delete previous outro
        if session.last_message_id:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
            except:
                pass
        await start_handler(update, context)
        return

    # ----------------- MAIN OPTIONS -----------------
    if data.startswith("main_"):
        session.current_option = data.split("_")[1]
        session.stage = "choosing_sub"
        msg = await context.bot.send_message(chat_id=user_id, text=f"You chose: {session.current_option.title()}\nPlease select a sub-option:", reply_markup=sub_options_inline(session))
        session.last_message_id = msg.message_id
        return

    # ----------------- SUB OPTIONS -----------------
    if data.startswith("sub_"):
        sub_idx = int(data.split("_")[1])
        if session.current_option == "question":
            session.current_suboption = session.sub_options_question[sub_idx]
        elif session.current_option == "suggestion":
            session.current_suboption = session.sub_options_suggestion[sub_idx]

        session.stage = "writing"
        msg = await context.bot.send_message(chat_id=user_id, text=f"You chose sub-option: {session.current_suboption}\nPlease write your message below. Press Done when finished.", reply_markup=back_cancel_inline())
        session.last_message_id = msg.message_id
        return

    # ----------------- BACK -----------------
    if data == "back":
        session.stage = "choosing_main"
        session.current_option = None
        session.current_suboption = None
        msg = await context.bot.send_message(chat_id=user_id, text="Please choose an option:", reply_markup=main_options_inline())
        session.last_message_id = msg.message_id
        return

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in sessions:
        sessions[user_id] = UserSession()
    session = sessions[user_id]

    if session.stage == "writing":
        # Send to admin(s) in requested format
        formatted_message = format_message(text, session.current_option.title(), session.current_suboption)
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin_id, text=formatted_message)

        # Send outro to user
        outro_text = (
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
        msg = await update.message.reply_text(outro_text, reply_markup=restart_inline())
        session.last_message_id = msg.message_id
        session.stage = "finished"
        session.answers = []

# ---------------------------- MAIN FUNCTION ----------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
