"""
Anonymous Bot for Korea GBI - Secure & Production Ready
Environment variables handled via config.py
"""

import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import get_token, get_admin_ids

# ====================== CONFIG ======================
TOKEN = get_token()
ADMIN_IDS = get_admin_ids()

# ====================== LOGGING ======================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log"),
    ],
)

logger = logging.getLogger(__name__)

# ====================== MESSAGES ======================
WELCOME = """☦️ በስመአብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን፡፡☦️

👋 ሰላም!
እኔ የኮሪያ_ጊቢ_ጉባኤ_ቦት ነኝ።
መልዕክቶችዎ ስም-አልባ ናቸው።

———

👋 Hello!
I am Korea_gbi_gubae_bot.
Your messages are anonymous.

Please choose an option to continue:
"""

THANK_YOU = """☦️
🙏 Thank you!
Your message has been delivered anonymously.

———

🙏 እናመሰግናለን!
መልዕክትዎ በስም-አልባ ተልኳል።
☦️
"""

CANCEL_MSG = """❌ Operation cancelled.
Use /start to begin again.
☦️"""

# ====================== KEYBOARDS ======================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Question", callback_data="question")],
        [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")]
    ])

def question_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🙏 Prayer", callback_data="q_prayer")],
        [InlineKeyboardButton("📖 Scripture", callback_data="q_scripture")],
        [InlineKeyboardButton("📚 Theology", callback_data="q_theology")],
        [InlineKeyboardButton("⚠️ Sin", callback_data="q_sin")],
        [InlineKeyboardButton("📌 Others", callback_data="q_others")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])

def suggestion_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 General", callback_data="s_general")],
        [InlineKeyboardButton("💬 Discussion", callback_data="s_discussion")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])

def writing_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Done", callback_data="done")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_cat")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
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
        await query.edit_message_text("Choose a category:", reply_markup=question_keyboard())

    elif data == "suggestion":
        context.user_data["type"] = "Suggestion"
        await query.edit_message_text("Choose a category:", reply_markup=suggestion_keyboard())

    elif data.startswith("q_") or data.startswith("s_"):
        context.user_data["category"] = data
        context.user_data["messages"] = []
        await query.edit_message_text(
            "✍️ Write your message.\nYou can send multiple messages.\nPress ✅ Done when finished.",
            reply_markup=writing_keyboard()
        )

    elif data == "done":
        messages = context.user_data.get("messages", [])
        if not messages:
            await query.answer("No message received.", show_alert=True)
            return

        full_text = " ".join(messages)
        msg_type = context.user_data.get("type")
        category = context.user_data.get("category")
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        admin_msg = f"""
📬 NEW {msg_type.upper()}
⏰ {time_str}
📂 {category.replace("_", " ").title()}

💬 {full_text}
        """

        for admin_id in ADMIN_IDS:
            try:
                await asyncio.wait_for(
                    context.bot.send_message(admin_id, admin_msg),
                    timeout=10,
                )
            except Exception as e:
                logger.error(f"Failed to send to admin {admin_id}: {e}")

        await query.edit_message_text(THANK_YOU)
        context.user_data.clear()

    elif data == "back_main":
        context.user_data.clear()
        await query.edit_message_text(WELCOME, reply_markup=main_keyboard())

    elif data == "back_cat":
        if context.user_data.get("type") == "Question":
            await query.edit_message_text("Choose a category:", reply_markup=question_keyboard())
        else:
            await query.edit_message_text("Choose a category:", reply_markup=suggestion_keyboard())

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text(CANCEL_MSG)

async def collect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "messages" in context.user_data:
        context.user_data["messages"].append(update.message.text.strip())

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Error occurred", exc_info=context.error)

# ====================== MAIN ======================
def main():
    print("🤖 Bot starting securely...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_message))
    app.add_error_handler(error_handler)

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
