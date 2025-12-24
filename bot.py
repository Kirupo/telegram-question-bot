from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

# 🔴 REPLACE THESE
BOT_TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"
ADMIN_ID = 1974614381  # <-- your Telegram numeric ID

# ---------- KEYBOARDS ----------

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Question", callback_data="question")],
        [InlineKeyboardButton("💡 Suggestion", callback_data="suggestion")],
        [InlineKeyboardButton("🚀 Idea", callback_data="idea")],
    ])

def done_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Done", callback_data="done")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])

# ---------- COMMANDS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "What do you want to send?",
        reply_markup=main_menu()
    )

# ---------- BUTTON HANDLER ----------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data in ["question", "suggestion", "idea"]:
        context.user_data["type"] = data
        await query.edit_message_text(
            f"Send your {data} now:"
        )

    elif data == "done":
        context.user_data.clear()
        await query.edit_message_text(
            "Choose again:",
            reply_markup=main_menu()
        )

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text(
            "Cancelled. Choose again:",
            reply_markup=main_menu()
        )

# ---------- MESSAGE HANDLER ----------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "type" not in context.user_data:
        await update.message.reply_text(
            "Please choose an option first.",
            reply_markup=main_menu()
        )
        return

    user = update.message.from_user
    msg_type = context.user_data["type"]
    text = update.message.text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    admin_text = (
        f"📩 NEW MESSAGE\n\n"
        f"👤 Username: @{user.username or 'N/A'}\n"
        f"📛 Name: {user.first_name}\n"
        f"🕒 Time: {timestamp}\n"
        f"📂 Type: {msg_type.upper()}\n\n"
        f"💬 Message:\n{text}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    await update.message.reply_text(
        "Message sent. What next?",
        reply_markup=done_menu()
    )

# ---------- MAIN ----------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot running...")
    app.run_polling(poll_interval=0.5)

if __name__ == "__main__":
    main()
