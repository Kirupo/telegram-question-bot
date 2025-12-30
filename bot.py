from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, CommandHandler, ContextTypes, filters
from datetime import datetime

# ----------------- CONFIG -----------------
TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
ADMINS = [7348815216, 1974614381]  # Put your admin IDs here

# ----------------- SESSION CLASS -----------------
class UserSession:
    def __init__(self):
        self.stage = "start"  # start -> choosing -> sub_option -> writing -> done
        self.current_option = None
        self.current_suboption = None
        self.message_text = ""
        self.last_message_id = None
        self.sub_options_question = [
            "Prayer", "Confession", "Scripture/Bible Verse", "Relationships",
            "Orthodox Practice", "Communion", "General Theology", "Fasting",
            "Saints and Intercession", "Saint Mary", "Others"
        ]
        self.sub_options_suggestion = [
            "General", "Discussion"
        ]

sessions = {}

# ----------------- HELPERS -----------------
def get_session(user_id):
    if user_id not in sessions:
        sessions[user_id] = UserSession()
    return sessions[user_id]

def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Question", callback_data="option_question"),
         InlineKeyboardButton("Suggestion", callback_data="option_suggestion")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])

def build_sub_keyboard(option):
    if option == "question":
        buttons = [[InlineKeyboardButton(x, callback_data=f"sub_{i}") for i, x in enumerate(UserSession().sub_options_question)]]
    else:
        buttons = [[InlineKeyboardButton(x, callback_data=f"sub_{i}") for i, x in enumerate(UserSession().sub_options_suggestion)]]
    # Add back and cancel
    buttons.append([InlineKeyboardButton("Back", callback_data="back"),
                    InlineKeyboardButton("Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)

# ----------------- COMMANDS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    session.stage = "choosing"
    session.current_option = None
    session.current_suboption = None
    session.message_text = ""

    msg = await context.bot.send_message(
        chat_id=user_id,
        text="☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን፡፡☦️\n\n"
             "👋 Hello! I am Korea_Gibi_Gubae_bot.\nYour messages are anonymous.\n\n"
             "👋 ሰላም!\nእኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።\n"
             "እነዚያ መልዕክቶች ስም-አልባ ናቸው እና\n"
             "ማንነትህ በአስተዳዳሪዎች አይታይም።",
        reply_markup=build_main_keyboard()
    )
    session.last_message_id = msg.message_id

# ----------------- CALLBACK HANDLER -----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    session = get_session(user_id)

    # ----------------- CANCEL -----------------
    if data == "cancel":
        session.stage = "done"
        session.current_option = None
        session.current_suboption = None
        session.message_text = ""
        if session.last_message_id:
            try: await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
            except: pass
        msg = await context.bot.send_message(
            chat_id=user_id,
            text="☦️\n🙏 Thank you!\nYour question/suggestion will be answered in upcoming discussions or sermons.\nHave a blessed time and stay tuned!\n\n"
                 "🙏 እናመሰግናለን!\nጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
                 "ቡሩክ ጊዜ ይቆዩ እና ይከታትሉ!\n",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Restart", callback_data="restart")]])
        )
        session.last_message_id = msg.message_id
        return

    # ----------------- RESTART -----------------
    if data == "restart":
        await start(update, context)
        return

    # ----------------- MAIN OPTION -----------------
    if data.startswith("option_"):
        session.current_option = data.split("_")[1]
        session.stage = "sub_option"
        if session.last_message_id:
            try: await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
            except: pass
        msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"You chose: {session.current_option.title()}\nSelect a sub-option:",
            reply_markup=build_sub_keyboard(session.current_option)
        )
        session.last_message_id = msg.message_id
        return

    # ----------------- SUB OPTION -----------------
    if data.startswith("sub_") and session.stage == "sub_option":
        sub_idx = int(data.split("_")[1])
        if session.current_option == "question":
            session.current_suboption = session.sub_options_question[sub_idx]
        else:
            session.current_suboption = session.sub_options_suggestion[sub_idx]

        session.stage = "writing"
        if session.last_message_id:
            try: await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
            except: pass
        msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"You chose: {session.current_option.title()} - {session.current_suboption}\n\nWrite your message below. Press Done when finished.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data="back"),
                 InlineKeyboardButton("Cancel", callback_data="cancel")]
            ])
        )
        session.last_message_id = msg.message_id
        return

    # ----------------- BACK -----------------
    if data == "back":
        if session.stage == "writing":
            session.stage = "sub_option"
            if session.last_message_id:
                try: await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
                except: pass
            msg = await context.bot.send_message(
                chat_id=user_id,
                text=f"You chose: {session.current_option.title()}\nSelect a sub-option:",
                reply_markup=build_sub_keyboard(session.current_option)
            )
            session.last_message_id = msg.message_id
        elif session.stage == "sub_option":
            await start(update, context)
        return

# ----------------- MESSAGE HANDLER -----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    session = get_session(user_id)

    if session.stage == "writing":
        session.message_text = text
        session.stage = "done"

        if session.last_message_id:
            try: await context.bot.delete_message(chat_id=user_id, message_id=session.last_message_id)
            except: pass

        # Format message for admin
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"📩 NEW MESSAGE\n🕒 Time: {now}\n📂 Type: {session.current_option.title()} - {session.current_suboption}\n\n💬 Message:\n{session.message_text}"

        for admin_id in ADMINS:
            await context.bot.send_message(chat_id=admin_id, text=formatted)

        # Send outro
        msg = await context.bot.send_message(
            chat_id=user_id,
            text="☦️\n🙏 Thank you!\nYour question/suggestion will be answered in upcoming discussions or sermons.\nHave a blessed time and stay tuned!\n\n"
                 "🙏 እናመሰግናለን!\nጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
                 "ቡሩክ ጊዜ ይቆዩ እና ይከታትሉ!\n",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Restart", callback_data="restart")]])
        )
        session.last_message_id = msg.message_id

# ----------------- MAIN -----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
