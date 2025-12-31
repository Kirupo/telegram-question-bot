import logging
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== CONFIG ==================
TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"

ADMIN_IDS = [7348815216, 1974614381]

logging.basicConfig(level=logging.INFO)

# ================== TEXTS ==================
INTRO_TEXT = (
    "☦️\n"
    "🙏 እንኳን ደህና መጡ!\n"
    "ጥያቄዎን ወይም አስተያየትዎን እዚህ ማስገባት ይችላሉ።\n\n"
    "———\n\n"
    "🙏 Welcome!\n"
    "You may submit your question or suggestion here.\n"
    "☦️"
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
    "Your message has been cancelled.\n"
    "We will be here waiting if you have any question or suggestion.\n"
    "Have a blessed time! ☦️"
)

# ================== KEYBOARDS ==================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Question", callback_data="question")],
        [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

def question_subs():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🙏 Prayer", callback_data="q_prayer")],
        [InlineKeyboardButton("🕊 Confession", callback_data="q_confession")],
        [InlineKeyboardButton("📖 Scripture / Bible Verse", callback_data="q_scripture")],
        [InlineKeyboardButton("❤️ Relationships", callback_data="q_relationships")],
        [InlineKeyboardButton("⛪ Orthodox Practice", callback_data="q_practice")],
        [InlineKeyboardButton("🍞 Communion", callback_data="q_communion")],
        [InlineKeyboardButton("📚 General Theology", callback_data="q_theology")],
        [InlineKeyboardButton("🥗 Fasting", callback_data="q_fasting")],
        [InlineKeyboardButton("⚠️ Sin", callback_data="q_sin")],
        [InlineKeyboardButton("👼 Saints & Intercession", callback_data="q_saints")],
        [InlineKeyboardButton("🌹 Saint Mary", callback_data="q_mary")],
        [InlineKeyboardButton("📌 Others", callback_data="q_others")],
        [InlineKeyboardButton("⬅ Back", callback_data="back_main"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

def suggestion_subs():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 General", callback_data="s_general")],
        [InlineKeyboardButton("💬 Discussion", callback_data="s_discussion")],
        [InlineKeyboardButton("⬅ Back", callback_data="back_main"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

def writing_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Done", callback_data="done")],
        [InlineKeyboardButton("⬅ Back", callback_data="back_sub"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

# ================== BOT LOGIC ==================
class QuestionBot:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        await update.message.reply_text(INTRO_TEXT, reply_markup=main_keyboard())

    async def main_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()

        if q.data == "question":
            context.user_data["type"] = "Question"
            await q.edit_message_text("Choose a question category:", reply_markup=question_subs())

        elif q.data == "suggestion":
            context.user_data["type"] = "Suggestion"
            await q.edit_message_text("Choose a suggestion category:", reply_markup=suggestion_subs())

    async def sub_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()

        context.user_data["sub"] = q.data
        context.user_data["messages"] = []

        await q.edit_message_text(
            "You may now write your message.\nSend as many messages as you want.",
            reply_markup=writing_keyboard()
        )

    async def collect_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if "messages" in context.user_data:
            context.user_data["messages"].append(update.message.text)

    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()

        msgs = context.user_data.get("messages", [])
        if not msgs:
            await q.edit_message_text("No message received.", reply_markup=main_keyboard())
            return

        full_text = " ".join(msgs)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        admin_msg = (
            f"📩 NEW MESSAGE\n"
            f"🕒 Time: {now}\n"
            f"📂 Type: {context.user_data['type']}\n"
            f"📌 Sub: {context.user_data['sub']}\n\n"
            f"💬 Message:\n{full_text}"
        )

        for admin in ADMIN_IDS:
            await context.bot.send_message(admin, admin_msg)

        context.user_data.clear()
        await q.edit_message_text(OUTRO_TEXT)

    async def back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()

        if q.data == "back_main":
            context.user_data.clear()
            await q.edit_message_text(INTRO_TEXT, reply_markup=main_keyboard())

        elif q.data == "back_sub":
            if context.user_data.get("type") == "Question":
                await q.edit_message_text("Choose a question category:", reply_markup=question_subs())
            else:
                await q.edit_message_text("Choose a suggestion category:", reply_markup=suggestion_subs())

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        context.user_data.clear()
        await q.edit_message_text(CANCEL_TEXT)

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    bot = QuestionBot()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.main_choice, pattern="^(question|suggestion)$"))
    app.add_handler(CallbackQueryHandler(bot.sub_selected, pattern="^(q_|s_)"))
    app.add_handler(CallbackQueryHandler(bot.done, pattern="^done$"))
    app.add_handler(CallbackQueryHandler(bot.back, pattern="^back_"))
    app.add_handler(CallbackQueryHandler(bot.cancel, pattern="^cancel$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.collect_text))

    app.run_polling()

if __name__ == "__main__":
    main()
