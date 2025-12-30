from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from datetime import datetime

# Replace with your Telegram admin IDs
ADMIN_IDS = [7348815216, 1974614381]

# Options
SUGGESTION_OPTIONS = ["Discussion", "General"]
QUESTION_OPTIONS = [
    "Prayer", "Confession", "Scripture/Bible Verse", "Relationships", "Orthodox Practice",
    "Communion", "General Theology", "Fasting", "Sin", "Saints and Intercession",
    "Saint Mary", "Others"
]

# Temporary storage for user messages
user_messages = {}

# --- Initial inline /start ---
async def send_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("/start", callback_data="start")]]
    await update.message.reply_text(
        "Press /start to begin:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Start handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user_messages.pop(user_id, None)  # clear previous messages if any

    await query.edit_message_text(
        "Hello! I’m Korea_gbi_gubae_bot. Your messages are anonymous."
    )

    keyboard = [
        [InlineKeyboardButton("Question", callback_data="type_question")],
        [InlineKeyboardButton("Suggestion", callback_data="type_suggestion")]
    ]
    await context.bot.send_message(
        chat_id=user_id,
        text="Please choose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Handle inline button presses ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_messages:
        user_messages[user_id] = {"type": "", "category": "", "texts": []}

    if data == "start":
        await start(update, context)
        return

    if data == "type_question":
        user_messages[user_id]["type"] = "Question"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"question_{opt}")] for opt in QUESTION_OPTIONS]
        await query.edit_message_text("Choose a question category:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "type_suggestion":
        user_messages[user_id]["type"] = "Suggestion"
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"suggestion_{opt}")] for opt in SUGGESTION_OPTIONS]
        await query.edit_message_text("Choose a suggestion category:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("suggestion_"):
        category = data.split("_")[1]
        user_messages[user_id]["category"] = category
        keyboard = [
            [InlineKeyboardButton("Done", callback_data="done")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            f"Write your {category} suggestion below. Press Done when finished or Cancel to cancel.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("question_"):
        category = data.split("_")[1]
        user_messages[user_id]["category"] = category
        keyboard = [
            [InlineKeyboardButton("Done", callback_data="done")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            f"Write your {category} question below. Press Done when finished or Cancel to cancel.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "done":
        if not user_messages[user_id]["texts"]:
            await query.edit_message_text("No message was written. Operation cancelled.")
            user_messages.pop(user_id, None)
        else:
            combined_text = "\n".join(user_messages[user_id]["texts"])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_type = user_messages[user_id]["type"]

            # Forward to admins
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 NEW MESSAGE\n🕒 Time: {timestamp}\n📂 Type: {message_type} - {user_messages[user_id]['category']}\n\n💬 Message:\n{combined_text}"
                )

            # Thank-you message with Amharic + inline /start button
            keyboard = [[InlineKeyboardButton("/start", callback_data="start")]]
            await query.edit_message_text(
                f"☦️\n🙏 Thank you!\nYour question/suggestion will be answered in upcoming discussions or sermons.\nHave a blessed time and stay tuned!\n\n———\n\n🙏 እናመሰግናለን!\nጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\nቡሩክ ጊዜ ይቆዩ እና ይከታትሉ!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            user_messages.pop(user_id, None)

    elif data == "cancel":
        keyboard = [[InlineKeyboardButton("/start", callback_data="start")]]
        await query.edit_message_text(
            "We have cancelled your request. We are here if you need anything else.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        user_messages.pop(user_id, None)

# --- Collect text messages ---
async def collect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id in user_messages:
        user_messages[user_id]["texts"].append(text)
        # No intermediate "Message saved" reply

# --- Main ---
def main():
    TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"  # <-- Replace with your bot token
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r"^/start$"), send_start_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_message))
    app.add_handler(CallbackQueryHandler(button))

    print("✅ Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
