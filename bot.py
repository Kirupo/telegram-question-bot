import logging
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# 🔐 ADMINS IDS
# =========================================================
ADMIN_IDS = [7348815216, 1974614381]

# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# =========================================================
# STATES
# =========================================================
STATE_MAIN = "main"
STATE_Q_SUB = "question_sub"
STATE_S_SUB = "suggestion_sub"
STATE_WRITING = "writing"

# =========================================================
# TEXTS (LOCKED)
# =========================================================
INTRO_TEXT = (
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

OUTRO_TEXT = (
    "☦️\n"
    "🙏 Thank you!\n"
    "Your question/suggestion will be answered in upcoming discussions or sermons.\n\n"
    "———\n\n"
    "🙏 እናመሰግናለን!\n"
    "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
    "☦️"
)

CANCEL_TEXT = (
    "❌ Your message has been cancelled.\n"
    "We will be here waiting if you have any question or suggestion.\n"
    "Have a blessed time!"
)

# =========================================================
# BOT
# =========================================================
class QuestionBot:

    # ---------------- START ----------------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()

        keyboard = [
            [InlineKeyboardButton("📖 Question", callback_data="question")],
            [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await update.message.reply_text(
            INTRO_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_MAIN

    # ---------------- MAIN CHOICE ----------------
    async def main_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        context.user_data["type"] = query.data
        context.user_data["messages"] = []

        if query.data == "question":
            await self.show_question_subs(query, context)
        else:
            await self.show_suggestion_subs(query, context)

    # ---------------- QUESTION SUBS ----------------
    async def show_question_subs(self, query, context):
        keyboard = [
            [InlineKeyboardButton("🙏 Prayer", callback_data="q_prayer")],
            [InlineKeyboardButton("🕊 Confession", callback_data="q_confession")],
            [InlineKeyboardButton("📖 Scripture / Bible verse", callback_data="q_scripture")],
            [InlineKeyboardButton("❤️ Relationships", callback_data="q_relationships")],
            [InlineKeyboardButton("⛪ Orthodox practice", callback_data="q_practice")],
            [InlineKeyboardButton("🍞 Communion", callback_data="q_communion")],
            [InlineKeyboardButton("📚 General theology", callback_data="q_theology")],
            [InlineKeyboardButton("🥗 Fasting", callback_data="q_fasting")],
            [InlineKeyboardButton("⚠️ Sin", callback_data="q_sin")],
            [InlineKeyboardButton("👼 Saints & intercession", callback_data="q_saints")],
            [InlineKeyboardButton("🌹 Saint Mary", callback_data="q_mary")],
            [InlineKeyboardButton("📌 Others", callback_data="q_others")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_Q_SUB

    # ---------------- SUGGESTION SUBS ----------------
    async def show_suggestion_subs(self, query, context):
        keyboard = [
            [InlineKeyboardButton("💬 General", callback_data="s_general")],
            [InlineKeyboardButton("🗣 Discussion", callback_data="s_discussion")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_S_SUB

    # ---------------- SUB SELECTED ----------------
    async def sub_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        context.user_data["sub"] = query.data
        context.user_data["state"] = STATE_WRITING

        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="done")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_sub")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            "✍️ Write your message.\n"
            "You may send multiple messages.\n"
            "Press DONE when finished.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---------------- COLLECT TEXT ----------------
    async def collect_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("state") != STATE_WRITING:
            return

        context.user_data["messages"].append(update.message.text)

    # ---------------- DONE ----------------
    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        combined_text = " ".join(context.user_data["messages"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        final_message = (
            "📩 NEW MESSAGE\n"
            f"🕒 Time: {now}\n"
            f"📂 Type: {context.user_data['type'].capitalize()}\n"
            f"🏷 Category: {context.user_data['sub']}\n\n"
            "💬 Message:\n"
            f"{combined_text}"
        )

        for admin_id in ADMIN_IDS:
            await context.bot.send_message(admin_id, final_message)

        await query.edit_message_text(OUTRO_TEXT)

    # ---------------- BACK ----------------
    async def back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "back_main":
            keyboard = [
                [InlineKeyboardButton("📖 Question", callback_data="question")],
                [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
            ]
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.user_data["state"] = STATE_MAIN
        else:
            if context.user_data["type"] == "question":
                await self.show_question_subs(query, context)
            else:
                await self.show_suggestion_subs(query, context)

    # ---------------- CANCEL ----------------
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        keyboard = [
            [InlineKeyboardButton("🔁 Restart", callback_data="restart")]
        ]

        await query.edit_message_text(
            CANCEL_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---------------- RESTART ----------------
    async def restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data.clear()

        keyboard = [
            [InlineKeyboardButton("📖 Question", callback_data="question")],
            [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            INTRO_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =========================================================
# MAIN
# =========================================================
def main():
    app = Application.builder().token(
        "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
    ).build()

    bot = QuestionBot()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.main_choice, pattern="^(question|suggestion)$"))
    app.add_handler(CallbackQueryHandler(bot.sub_selected, pattern="^(q_|s_)"))
    app.add_handler(CallbackQueryHandler(bot.done, pattern="^done$"))
    app.add_handler(CallbackQueryHandler(bot.back, pattern="^back_"))
    app.add_handler(CallbackQueryHandler(bot.cancel, pattern="^cancel$"))
    app.add_handler(CallbackQueryHandler(bot.restart, pattern="^restart$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.collect_text))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
