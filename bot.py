import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ---------------------------- CONFIGURATION ----------------------------
TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"

# Admin IDs: either single or multiple
# Single admin:
# ADMIN_IDS = [123456789]

# Multiple admins:
ADMIN_IDS = [7348815216, 1974614381]  # replace with your actual Telegram numeric IDs

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------- BOT STATE CLASS ----------------------------
class UserSession:
    """Tracks each user's session state"""
    def __init__(self):
        self.stage = "start"
        self.answers = []
        self.current_option_index = 0
        self.options = ["Sin", "Question", "Suggestion"]  # Example options
        self.last_message_id = None

sessions = {}

# ---------------------------- INLINE KEYBOARD HELPERS ----------------------------
def start_inline():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Start", callback_data="start")]])

def options_inline(session: UserSession):
    keyboard = []
    for idx, option in enumerate(session.options):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"option_{idx}")])
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)

def back_cancel_inline():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="back"),
         InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])

def restart_inline():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Restart", callback_data="restart")]])

# ---------------------------- MESSAGE FORMATTING ----------------------------
def format_message(user_text, msg_type):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""📩 NEW MESSAGE
🕒 Time: {now}
📂 Type: {msg_type}

💬 Message:
{user_text}"""

# ---------------------------- HANDLERS ----------------------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sessions[user_id] = UserSession()
    session = sessions[user_id]

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
        "Your messages are anonymous."
    )

    msg = await update.message.reply_text(intro_text, reply_markup=start_inline())
    session.last_message_id = msg.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in sessions:
        sessions[user_id] = UserSession()
    session = sessions[user_id]

    # Delete last inline message for "disappearing" effect
    if session.last_message_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
        except:
            pass

    data = query.data

    # ----------------- START -----------------
    if data == "start" or data == "restart":
        session.stage = "choosing"
        msg = await context.bot.send_message(chat_id=user_id, text="Please choose an option:", reply_markup=options_inline(session))
        session.last_message_id = msg.message_id
        return

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

    # ----------------- OPTIONS -----------------
    if data.startswith("option_"):
        idx = int(data.split("_")[1])
        session.current_option_index = idx
        session.stage = "writing"
        option_name = session.options[idx]
        msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"You chose: {option_name}\nPlease write your message below:",
            reply_markup=back_cancel_inline()
        )
        session.last_message_id = msg.message_id
        return

    # ----------------- BACK -----------------
    if data == "back":
        session.stage = "choosing"
        msg = await context.bot.send_message(chat_id=user_id, text="Please choose an option:", reply_markup=options_inline(session))
        session.last_message_id = msg.message_id
        return

    # ----------------- RESTART -----------------
    if data == "restart":
        await start_handler(update, context)
        return

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in sessions:
        sessions[user_id] = UserSession()
    session = sessions[user_id]

    if session.stage == "writing":
        # Send to admin(s) in requested format
        option_name = session.options[session.current_option_index]
        formatted_message = format_message(text, option_name)

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
