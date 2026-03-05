"""
Anonymous Bot for Korea GBI - Optimized for Termux/Phone
Simple, reliable version with better error handling
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

# ====================== CONFIG ======================

TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
ADMIN_IDS = [7348815216, 1974614381]

# Setup logging for Termux

logging.basicConfig(
format='%(asctime)s - %(levelname)s - %(message)s',
level=logging.INFO,
handlers=[
logging.StreamHandler(),
logging.FileHandler('bot.log')
]
)
logger = logging.getLogger(__name__)

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
You can start again anytime with /start
☦️"""

CANCEL_MSG = """❌ Operation cancelled.
You can start again anytime with /start.

God bless! ☦️"""

# ====================== KEYBOARD FUNCTIONS ======================

def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Ask Question", callback_data="ask")],
        [InlineKeyboardButton("Help", callback_data="help")]
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


# ====================== BOT HANDLERS ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'user_data' in context.__dict__:
        context.user_data.clear()

    await update.message.reply_text(
        WELCOME,
        reply_markup=main_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "question":
        context.user_data["type"] = "Question"
        await query.edit_message_text(
            "📂 Choose a category:",
            reply_markup=question_keyboard()
        )

    elif data == "suggestion":
        context.user_data["type"] = "Suggestion"
        await query.edit_message_text(
            "📂 Choose a category:",
            reply_markup=suggestion_keyboard()
        )

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
        await query.edit_message_text(
            WELCOME,
            reply_markup=main_keyboard()
        )

    elif data == "back_cat":
        msg_type = context.user_data.get("type", "Question")

        if msg_type == "Question":
            await query.edit_message_text(
                "📂 Choose a category:",
                reply_markup=question_keyboard()
            )
        else:
            await query.edit_message_text(
                "📂 Choose a category:",
                reply_markup=suggestion_keyboard()
            )

    elif data == "done":
        messages = context.user_data.get("messages", [])

        if not messages:
            await query.answer("⚠️ No message received", show_alert=True)
            return

        full_text = " ".join(messages)
        msg_type = context.user_data.get("type", "Unknown")
        category = context.user_data.get("category", "unknown")
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        admin_msg = f"""
📬 NEW {msg_type.upper()}
⏰ {time_str}
📂 {category.replace('_', ' ').title()}

💬 {full_text}
"""

        sent_count = 0

        for admin_id in ADMIN_IDS:
            try:
                await asyncio.wait_for(
                    context.bot.send_message(admin_id, admin_msg),
                    timeout=10.0
                )
                sent_count += 1
                logger.info(f"Sent to admin {admin_id}")

            except Exception as e:
                logger.error(f"Failed to send to admin {admin_id}: {e}")

        await query.edit_message_text(THANK_YOU)
        context.user_data.clear()

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text(CANCEL_MSG)


async def collect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "messages" in context.user_data:
        text = update.message.text.strip()

        if text:
            context.user_data["messages"].append(text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=True)


# ====================== NEW FIXED START FUNCTION ======================

async def start_bot(app):
    await app.initialize()
    await app.start()
    print("🤖 Bot is running! Press Ctrl+C to stop")

    try:
        # Keep the bot running indefinitely
        await asyncio.Event().wait()
    finally:
        await app.stop()
        await app.shutdown()
        print("❌ Bot stopped")


# ====================== MAIN FUNCTION ======================

def main():
    print("🤖 Starting bot...")
    print("📱 Running on Termux (Phone Server)")
    print("⚠️ Keep this app running in background")
    print("────────────────────────────────────")

    try:
        app = Application.builder().token(TOKEN).build()

        # Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_message))
        app.add_error_handler(error_handler)

        print("✅ Bot is running!")
        print("❌ Press Ctrl+C to stop")
        print("\n📊 Logs are saved to 'bot.log'")

        # Run polling safely
        app.run_polling(timeout=60)

    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        print(f"❌ Bot crashed: {e}")


if __name__ == "__main__":
    print("🔍 Checking requirements...")

    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please replace TOKEN with your bot token!")
        exit(1)

    print("────────────────────────────────────")

    main()
