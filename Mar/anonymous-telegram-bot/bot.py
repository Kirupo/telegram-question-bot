"""
Anonymous Bot for Korea GBI - Webhook Version
Original logic preserved EXACTLY
"""

import logging
import asyncio
import os
from datetime import datetime
from flask import Flask, request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN, ADMIN_IDS

# ====================== LOGGING ======================
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# ====================== FLASK ======================
web = Flask(__name__)
PORT = int(os.environ.get("PORT", 10000))

# ====================== TELEGRAM APP ======================
app = Application.builder().token(TOKEN).build()

# ====================== MESSAGES ======================
WELCOME = """☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን፡፡☦️

👋 ሰላም!
እኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።
እነዚያ መልዕክቶች ስም-አልባ ናቸው እና
ማንነትህ በአስተዳዳሪዎች አይታይም።

———

👋 Hello!
I am Korea_gbi_gubae_bot.
Your messages are anonymous.

Please choose an option to continue:"""

THANK_YOU = """☦️
🙏 Thank you!
Your question/suggestion will be answered in upcoming discussions or sermons.

———

🙏 እናመሰግናለን!
ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።
☦️"""

CANCEL_MSG = """❌ Operation cancelled.
You can start again anytime with /start.

God bless! ☦️"""

# ====================== KEYBOARDS ======================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Question", callback_data="question")],
        [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")]
    ])

def question_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🙏 Prayer", callback_data="q_prayer")],
        [InlineKeyboardButton("🕊 Confession", callback_data="q_confession")],
        [InlineKeyboardButton("📖 Scripture", callback_data="q_scripture")],
        [InlineKeyboardButton("❤️ Relationships", callback_data="q_relationships")],
        [InlineKeyboardButton("⛪ Orthodox Practice", callback_data="q_practice")],
        [InlineKeyboardButton("🍞 Communion", callback_data="q_communion")],
        [InlineKeyboardButton("📚 Theology", callback_data="q_theology")],
        [InlineKeyboardButton("🥗 Fasting", callback_data="q_fasting")],
        [InlineKeyboardButton("⚠️ Sin", callback_data="q_sin")],
        [InlineKeyboardButton("👼 Saints", callback_data="q_saints")],
        [InlineKeyboardButton("🌹 Saint Mary", callback_data="q_mary")],
        [InlineKeyboardButton("📌 Others", callback_data="q_others")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

def suggestion_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 General", callback_data="s_general")],
        [InlineKeyboardButton("💬 Discussion", callback_data="s_discussion")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

def writing_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Done", callback_data="done")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_cat")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

# ====================== HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(WELCOME, reply_markup=main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "question":
        context.user_data["type"] = "Question"
        await query.edit_message_text("📂 Choose a category:", reply_markup=question_keyboard())

    elif data == "suggestion":
        context.user_data["type"] = "Suggestion"
        await query.edit_message_text("📂 Choose a category:", reply_markup=suggestion_keyboard())

    elif data.startswith("q_") or data.startswith("s_"):
        context.user_data["category"] = data
        context.user_data["messages"] = []
        await query.edit_message_text(
            "✍️ *Write your message now:*\n\n"
            "• You can send multiple messages\n"
            "• Press ✅ Done when finished\n"
            "• Your messages are anonymous",
            reply_markup=writing_keyboard(),
            parse_mode="Markdown"
        )

    elif data == "back_main":
        context.user_data.clear()
        await query.edit_message_text(WELCOME, reply_markup=main_keyboard())

    elif data == "back_cat":
        if context.user_data.get("type") == "Question":
            await query.edit_message_text("📂 Choose a category:", reply_markup=question_keyboard())
        else:
            await query.edit_message_text("📂 Choose a category:", reply_markup=suggestion_keyboard())

    elif data == "done":
        messages = context.user_data.get("messages", [])
        if not messages:
            await query.answer("⚠️ No message received", show_alert=True)
            return

        full_text = " ".join(messages)
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        admin_msg = f"""
📬 NEW {context.user_data.get('type')}
⏰ {time_str}
📂 {context.user_data.get('category')}

💬 {full_text}
        """

        for admin in ADMIN_IDS:
            await context.bot.send_message(admin, admin_msg)

        await query.edit_message_text(THANK_YOU)
        context.user_data.clear()

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text(CANCEL_MSG)

async def collect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "messages" in context.user_data:
        context.user_data["messages"].append(update.message.text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=True)

# ====================== REGISTER ======================
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_message))
app.add_error_handler(error_handler)

# ====================== WEBHOOK ======================
@web.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    asyncio.run(app.process_update(update))
    return "OK", 200

@web.route("/")
def index():
    return "Bot is running", 200

# ====================== START ======================
if __name__ == "__main__":
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        app.bot.set_webhook(f"{url}/webhook")
        logger.info("Webhook set")

    web.run(host="0.0.0.0", port=PORT)
