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
# 🔐 ADMINS IDS (ADD YOUR TELEGRAM USER IDS HERE)
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
# CONSTANTS
# =========================================================
STATE_MAIN = "main"
STATE_Q_SUB = "question_sub"
STATE_S_SUB = "suggestion_sub"
STATE_WRITING = "writing"

# =========================================================
# BOT CLASS
# =========================================================
class QuestionBot:

    def __init__(self):
        pass

    # -----------------------------------------------------
    # START / RESTART
    # -----------------------------------------------------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()

        intro_text = (
            "👋 Welcome!\n\n"
            "Please choose what you want to send."
        )

        keyboard = [
            [InlineKeyboardButton("❓ Question", callback_data="question")],
            [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")],
        ]

        message = await update.message.reply_text(
            intro_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["intro_message_id"] = message.message_id
        context.user_data["state"] = STATE_MAIN

    # -----------------------------------------------------
    # MAIN MENU HANDLER
    # -----------------------------------------------------
    async def main_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        context.user_data["type"] = query.data
        context.user_data["messages"] = []

        if query.data == "question":
            await self.show_question_subs(query, context)
        else:
            await self.show_suggestion_subs(query, context)

    # -----------------------------------------------------
    # QUESTION SUBS
    # -----------------------------------------------------
    async def show_question_subs(self, query, context):
        keyboard = [
            [InlineKeyboardButton("🙏 Prayer", callback_data="q_prayer")],
            [InlineKeyboardButton("✝️ Confession", callback_data="q_confession")],
            [InlineKeyboardButton("📖 Scripture / Bible Verse", callback_data="q_scripture")],
            [InlineKeyboardButton("❤️ Relationships", callback_data="q_relationships")],
            [InlineKeyboardButton("⛪ Orthodox Practice", callback_data="q_practice")],
            [InlineKeyboardButton("🍞 Communion", callback_data="q_communion")],
            [InlineKeyboardButton("📚 General Theology", callback_data="q_theology")],
            [InlineKeyboardButton("🥗 Fasting", callback_data="q_fasting")],
            [InlineKeyboardButton("⚠️ Sin", callback_data="q_sin")],
            [InlineKeyboardButton("👼 Saints & Intercession", callback_data="q_saints")],
            [InlineKeyboardButton("🌸 Saint Mary", callback_data="q_mary")],
            [InlineKeyboardButton("📌 Others", callback_data="q_others")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            "Choose question category:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_Q_SUB

    # -----------------------------------------------------
    # SUGGESTION SUBS
    # -----------------------------------------------------
    async def show_suggestion_subs(self, query, context):
        keyboard = [
            [InlineKeyboardButton("💡 General", callback_data="s_general")],
            [InlineKeyboardButton("💬 Discussion", callback_data="s_discussion")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            "Choose suggestion category:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_S_SUB

    # -----------------------------------------------------
    # SUB SELECTED → WRITING MODE
    # -----------------------------------------------------
    async def sub_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        context.user_data["sub"] = query.data

        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="done")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_sub")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]

        await query.edit_message_text(
            "✍️ Write your message.\n"
            "You can send as many messages as you want.\n"
            "Press DONE when finished.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["state"] = STATE_WRITING

    # -----------------------------------------------------
    # COLLECT USER TEXT
    # -----------------------------------------------------
    async def collect_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("state") != STATE_WRITING:
            return

        context.user_data["messages"].append(update.message.text)

    # -----------------------------------------------------
    # DONE → SEND TO ADMINS
    # -----------------------------------------------------
    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        combined_text = "\n".join(context.user_data["messages"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        final_message = (
            "📩 NEW MESSAGE\n"
            f"🕒 Time: {now}\n"
            f"📂 Type: {context.user_data['type'].capitalize()}\n\n"
            "💬 Message:\n"
            f"{combined_text}"
        )

        for admin_id in ADMIN_IDS:
            await context.bot.send_message(admin_id, final_message)

        keyboard = [
            [InlineKeyboardButton("🔁 Restart", callback_data="restart")]
        ]

        await query.edit_message_text(
            "✅ Message sent successfully.\nThank you!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # -----------------------------------------------------
    # BACK HANDLING
    # -----------------------------------------------------
    async def back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "back_main":
            await self.start(update, context)
        else:
            if context.user_data["type"] == "question":
                await self.show_question_subs(query, context)
            else:
                await self.show_suggestion_subs(query, context)

    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        keyboard = [
            [InlineKeyboardButton("🔁 Restart", callback_data="restart")]
        ]

        await query.edit_message_text(
            "❌ Cancelled.\nThank you for visiting.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # -----------------------------------------------------
    # RESTART (FIXED)
    # -----------------------------------------------------
    async def restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        context.user_data.clear()

        await query.edit_message_text(
            "🔄 Restarting..."
        )

        await self.start(update, context)


# =========================================================
# MAIN
# =========================================================
def main():
    app = Application.builder().token("8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY").build()

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
