import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= ADMIN IDS =================
ADMIN_IDS = [7348815216, 1974614381]

# ================= LOGGING ===================
logging.basicConfig(level=logging.INFO)

# ================= STATES ====================
STATE_MAIN = "main"
STATE_WRITING = "writing"

# ================= BOT =======================
class QuestionBot:

    # ---------- START ----------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        context.user_data["messages"] = []

        text = (
            "☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን ☦️\n\n"
            "👋 Hello!\n"
            "I am Korea_gbi_gubae_bot.\n"
            "Your messages are anonymous.\n\n"
            "Please choose an option to continue:"
        )

        keyboard = [
            [InlineKeyboardButton("❓ Question", callback_data="question")],
            [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_MAIN

    # ---------- MAIN CHOICE ----------
    async def main_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "question":
            context.user_data["type"] = "Question"
            await self.question_subs(query)

        elif query.data == "suggestion":
            context.user_data["type"] = "Suggestion"
            await self.suggestion_subs(query)

        else:
            await self.cancel_message(query)

    # ---------- QUESTION SUBS (UPDATED) ----------
    async def question_subs(self, query):
        keyboard = [
            [InlineKeyboardButton("🙏 Prayer", callback_data="Prayer")],
            [InlineKeyboardButton("✝️ Confession", callback_data="Confession")],
            [InlineKeyboardButton("📖 Scripture / Bible Verse", callback_data="Scripture / Bible Verse")],
            [InlineKeyboardButton("❤️ Relationships", callback_data="Relationships")],
            [InlineKeyboardButton("⛪ Orthodox Practice", callback_data="Orthodox Practice")],
            [InlineKeyboardButton("🍞 Communion", callback_data="Communion")],
            [InlineKeyboardButton("📚 General Theology", callback_data="General Theology")],
            [InlineKeyboardButton("🥗 Fasting", callback_data="Fasting")],
            [InlineKeyboardButton("⚠️ Sin", callback_data="Sin")],
            [InlineKeyboardButton("👼 Saints & Intercession", callback_data="Saints & Intercession")],
            [InlineKeyboardButton("🌸 Saint Mary", callback_data="Saint Mary")],
            [InlineKeyboardButton("📌 Others", callback_data="Others")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            "Choose a question category:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---------- SUGGESTION SUBS ----------
    async def suggestion_subs(self, query):
        keyboard = [
            [InlineKeyboardButton("💡 General", callback_data="General")],
            [InlineKeyboardButton("💬 Discussion", callback_data="Discussion")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            "Choose a suggestion category:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---------- SUB SELECT ----------
    async def sub_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        context.user_data["category"] = query.data

        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="done")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_sub")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            "✍️ Write your message.\n"
            "You may send multiple messages.\n"
            "Press DONE when finished.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_WRITING

    # ---------- COLLECT TEXT ----------
    async def collect_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("state") == STATE_WRITING:
            context.user_data["messages"].append(update.message.text)

    # ---------- DONE ----------
    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        message_text = "\n".join(context.user_data["messages"])
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        admin_message = (
            "📩 NEW MESSAGE\n"
            f"🕒 Time: {time_now}\n"
            f"📂 Type: {context.user_data['type']}\n"
            f"📌 Category: {context.user_data['category']}\n\n"
            "💬 Message:\n"
            f"{message_text}"
        )

        for admin in ADMIN_IDS:
            await context.bot.send_message(admin, admin_message)

        await query.edit_message_text(
            "☦️\n"
            "🙏 Thank you!\n"
            "Your question/suggestion will be answered in upcoming discussions or sermons.\n\n"
            "———\n\n"
            "🙏 እናመሰግናለን!\n"
            "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
            "☦️"
        )

    # ---------- CANCEL ----------
    async def cancel_message(self, query):
        await query.edit_message_text(
            "Your message has been cancelled.\n"
            "We will be here waiting if you have any question or suggestion.\n"
            "Have a blessed time ☦️"
        )

    # ---------- BACK ----------
    async def back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "back_main":
            await self.start(update, context)
        elif query.data == "back_sub":
            if context.user_data["type"] == "Question":
                await self.question_subs(query)
            else:
                await self.suggestion_subs(query)

# ================= MAIN ======================
def main():
    app = Application.builder().token("8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY").build()
    bot = QuestionBot()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.main_choice, pattern="^(question|suggestion|cancel)$"))
    app.add_handler(CallbackQueryHandler(bot.sub_selected))
    app.add_handler(CallbackQueryHandler(bot.done, pattern="^done$"))
    app.add_handler(CallbackQueryHandler(bot.back, pattern="^back_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.collect_text))

    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
