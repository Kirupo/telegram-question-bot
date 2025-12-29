from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)
from datetime import datetime

TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"

ADMIN_IDS = [7348815216, 1974614381]  # replace

QUESTION_OPTIONS = [
    "Prayer", "Confession", "Scripture/Bible Verse", "Relationships",
    "Orthodox Practice", "Communion", "General Theology", "Fasting",
    "Sin", "Saints and Intercession", "Saint Mary", "Others"
]

SUGGESTION_OPTIONS = ["Discussion", "General"]

user_sessions = {}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello!\n"
        "I am *Korea_gbi_gubae_bot*\n"
        "Your messages are *anonymous*.",
        parse_mode="Markdown"
    )

    keyboard = [
        [InlineKeyboardButton("Question", callback_data="question")],
        [InlineKeyboardButton("Suggestion", callback_data="suggestion")]
    ]

    await update.message.reply_text(
        "Please choose one:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTONS ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if uid not in user_sessions:
        user_sessions[uid] = {"type": "", "category": "", "texts": []}

    data = query.data

    if data == "question":
        user_sessions[uid]["type"] = "Question"
        kb = [[InlineKeyboardButton(x, callback_data=f"q_{x}")] for x in QUESTION_OPTIONS]
        await query.edit_message_text("Select question category:", reply_markup=InlineKeyboardMarkup(kb))

    elif data == "suggestion":
        user_sessions[uid]["type"] = "Suggestion"
        kb = [[InlineKeyboardButton(x, callback_data=f"s_{x}")] for x in SUGGESTION_OPTIONS]
        await query.edit_message_text("Select suggestion category:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith(("q_", "s_")):
        cat = data[2:]
        user_sessions[uid]["category"] = cat

        kb = [
            [InlineKeyboardButton("Done", callback_data="done")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ]

        await query.edit_message_text(
            f"✍️ Send your message.\nPress *Done* when finished.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data == "done":
        text = "\n".join(user_sessions[uid]["texts"])
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = (
            f"📩 NEW MESSAGE\n"
            f"🕒 {time}\n"
            f"📂 {user_sessions[uid]['type']} - {user_sessions[uid]['category']}\n\n"
            f"💬 {text}"
        )

        for admin in ADMIN_IDS:
            await context.bot.send_message(admin, msg)

        hour = datetime.now().hour
        greet = "day" if hour < 18 else "evening"

        await query.edit_message_text(f"🙏 Thank you! Have a nice {greet}.")
        user_sessions.pop(uid)

    elif data == "cancel":
        user_sessions.pop(uid, None)
        await query.edit_message_text("❌ Cancelled. You can start again with /start")

# ---------------- TEXT ----------------
async def collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid in user_sessions:
        user_sessions[uid]["texts"].append(update.message.text)

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect))

    print("✅ Bot running")
    app.run_polling(
    poll_interval=0.5,
    timeout=5,
    drop_pending_updates=True
)


if __name__ == "__main__":
    main()
