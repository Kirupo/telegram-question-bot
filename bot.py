"""
Anonymous Question/Suggestion Bot for Korea GBI Church
Professional, clean, and fully functional version
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ====================== CONFIGURATION ======================
TOKEN = "8229992007:AAFrMlg0iI7mGC8acDvLi3Zy2CaVsVIfDQY"  # Replace with your bot token
ADMIN_IDS = [7348815216, 1974614381]  # Replace with actual admin Telegram IDs

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================== TEXT MESSAGES ======================
class Messages:
    """All bot messages in one place for easy maintenance"""
    
    WELCOME = (
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
    
    THANK_YOU = (
        "☦️\n"
        "🙏 Thank you!\n"
        "Your question/suggestion will be answered in upcoming discussions or sermons.\n\n"
        "———\n\n"
        "🙏 እናመሰግናለን!\n"
        "ጥያቄዎ/አስተያየትዎ በሚቀጥሉ ውይይቶች ወይም ስብከቶች ይመለሳል።\n"
        "☦️"
    )
    
    CANCELLED = (
        "❌ Operation cancelled.\n"
        "Feel free to start again anytime with /start\n\n"
        "God bless you! ☦️"
    )
    
    NO_MESSAGE = "⚠️ No message received. Please write your message first."
    
    CHOOSE_CATEGORY = "📂 Please choose a category:"
    
    WRITING_INSTRUCTIONS = (
        "✍️ *You can now write your message.*\n\n"
        "• Send as many messages as you need\n"
        "• Your messages are collected anonymously\n"
        "• Press ✅ Done when finished\n"
        "• Press ↩️ Back to change category\n"
        "• Press ❌ Cancel to stop"
    )
    
    @staticmethod
    def get_subject_name(category_code: str) -> str:
        """Convert category code to readable name"""
        subjects = {
            # Question categories
            "q_prayer": "🙏 Prayer",
            "q_confession": "🕊 Confession", 
            "q_scripture": "📖 Scripture",
            "q_relationships": "❤️ Relationships",
            "q_practice": "⛪ Orthodox Practice",
            "q_communion": "🍞 Communion",
            "q_theology": "📚 Theology",
            "q_fasting": "🥗 Fasting",
            "q_sin": "⚠️ Sin & Repentance",
            "q_saints": "👼 Saints",
            "q_mary": "🌹 Saint Mary",
            "q_others": "📌 Other Questions",
            
            # Suggestion categories
            "s_general": "📝 General Suggestion",
            "s_discussion": "💬 Discussion Topic",
        }
        return subjects.get(category_code, "📌 Unknown Category")

# ====================== KEYBOARD GENERATORS ======================
class KeyboardFactory:
    """Generate all inline keyboards for the bot"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Create main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("❓ Submit Question", callback_data="menu:question")],
            [InlineKeyboardButton("💡 Make Suggestion", callback_data="menu:suggestion")],
            [InlineKeyboardButton("❌ Cancel", callback_data="menu:cancel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def question_categories() -> InlineKeyboardMarkup:
        """Create question categories keyboard"""
        categories = [
            ("🙏 Prayer", "cat:q_prayer"),
            ("🕊 Confession", "cat:q_confession"),
            ("📖 Scripture / Bible", "cat:q_scripture"),
            ("❤️ Relationships", "cat:q_relationships"),
            ("⛪ Orthodox Practice", "cat:q_practice"),
            ("🍞 Communion", "cat:q_communion"),
            ("📚 General Theology", "cat:q_theology"),
            ("🥗 Fasting", "cat:q_fasting"),
            ("⚠️ Sin & Repentance", "cat:q_sin"),
            ("👼 Saints & Intercession", "cat:q_saints"),
            ("🌹 Saint Mary", "cat:q_mary"),
            ("📌 Other Questions", "cat:q_others"),
        ]
        
        # Create buttons (2 per row for better mobile view)
        buttons = []
        for i in range(0, len(categories), 2):
            row = []
            if i < len(categories):
                text1, data1 = categories[i]
                row.append(InlineKeyboardButton(text1, callback_data=data1))
            if i + 1 < len(categories):
                text2, data2 = categories[i + 1]
                row.append(InlineKeyboardButton(text2, callback_data=data2))
            if row:
                buttons.append(row)
        
        # Add navigation buttons
        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="nav:main"),
            InlineKeyboardButton("❌ Cancel", callback_data="menu:cancel")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def suggestion_categories() -> InlineKeyboardMarkup:
        """Create suggestion categories keyboard"""
        categories = [
            ("📝 General Suggestion", "cat:s_general"),
            ("💬 Discussion Topic", "cat:s_discussion"),
        ]
        
        buttons = [[InlineKeyboardButton(text, callback_data=data)] 
                  for text, data in categories]
        
        # Add navigation buttons
        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="nav:main"),
            InlineKeyboardButton("❌ Cancel", callback_data="menu:cancel")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def writing_controls() -> InlineKeyboardMarkup:
        """Create keyboard for message writing phase"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Done", callback_data="action:done")],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="nav:category"),
                InlineKeyboardButton("❌ Cancel", callback_data="menu:cancel")
            ]
        ])

# ====================== BOT HANDLER CLASS ======================
class AnonymousBot:
    """Main bot handler with all callback methods"""
    
    def __init__(self):
        self.app: Optional[Application] = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - Entry point"""
        # Clear any previous session data
        context.user_data.clear()
        
        # Store user info for logging (not shown to admins)
        user = update.effective_user
        logger.info(f"New user started: {user.id}, {user.full_name}")
        
        # Send welcome message
        await update.message.reply_text(
            Messages.WELCOME,
            reply_markup=KeyboardFactory.main_menu(),
            parse_mode=None  # Disable markdown to handle special characters
        )
    
    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle main menu selections"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "menu:question":
            # User selected Question
            context.user_data["type"] = "Question"
            await query.edit_message_text(
                Messages.CHOOSE_CATEGORY,
                reply_markup=KeyboardFactory.question_categories()
            )
            
        elif data == "menu:suggestion":
            # User selected Suggestion
            context.user_data["type"] = "Suggestion"
            await query.edit_message_text(
                Messages.CHOOSE_CATEGORY,
                reply_markup=KeyboardFactory.suggestion_categories()
            )
            
        elif data == "menu:cancel":
            # User selected Cancel
            context.user_data.clear()
            await query.edit_message_text(Messages.CANCELLED)
    
    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle category selection from question/suggestion menus"""
        query = update.callback_query
        await query.answer()
        
        # Extract category code (e.g., "q_prayer" from "cat:q_prayer")
        category_code = query.data.replace("cat:", "")
        context.user_data["category"] = category_code
        context.user_data["messages"] = []  # Initialize message storage
        
        # Show writing instructions
        await query.edit_message_text(
            Messages.WRITING_INSTRUCTIONS,
            reply_markup=KeyboardFactory.writing_controls(),
            parse_mode="Markdown"
        )
    
    async def handle_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle back navigation"""
        query = update.callback_query
        await query.answer()
        
        destination = query.data.replace("nav:", "")
        
        if destination == "main":
            # Go back to main menu
            context.user_data.clear()
            await query.edit_message_text(
                Messages.WELCOME,
                reply_markup=KeyboardFactory.main_menu()
            )
            
        elif destination == "category":
            # Go back to category selection
            msg_type = context.user_data.get("type", "Question")
            
            if msg_type == "Question":
                await query.edit_message_text(
                    Messages.CHOOSE_CATEGORY,
                    reply_markup=KeyboardFactory.question_categories()
                )
            else:
                await query.edit_message_text(
                    Messages.CHOOSE_CATEGORY,
                    reply_markup=KeyboardFactory.suggestion_categories()
                )
    
    async def collect_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Collect user messages during writing phase"""
        # Only collect if user is in writing phase
        if "messages" in context.user_data:
            user_message = update.message.text.strip()
            
            if user_message:
                context.user_data["messages"].append(user_message)
                logger.info(f"Collected message from user {update.effective_user.id}")
    
    async def handle_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle submission when user presses Done"""
        query = update.callback_query
        await query.answer()
        
        # Check if any messages were collected
        messages = context.user_data.get("messages", [])
        
        if not messages:
            await query.answer(Messages.NO_MESSAGE, show_alert=True)
            return
        
        # Prepare data for admin notification
        msg_type = context.user_data.get("type", "Unknown")
        category_code = context.user_data.get("category", "unknown")
        full_message = " ".join(messages)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert category code to readable name
        category_name = Messages.get_subject_name(category_code)
        
        # Format admin message
        admin_message = (
            f"📬 *NEW ANONYMOUS MESSAGE*\n"
            f"⏰ Time: `{timestamp}`\n"
            f"📋 Type: *{msg_type}*\n"
            f"📂 Category: {category_name}\n\n"
            f"📝 Message:\n"
            f"{full_message}\n\n"
            f"──────────────\n"
            f"👤 User ID: `{update.effective_user.id}`"
        )
        
        # Send to all admins
        success_count = 0
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode="Markdown"
                )
                success_count += 1
                logger.info(f"Message sent to admin {admin_id}")
            except Exception as e:
                logger.error(f"Failed to send to admin {admin_id}: {e}")
        
        # Clear user session
        context.user_data.clear()
        
        # Show thank you message to user
        await query.edit_message_text(Messages.THANK_YOU)
        
        logger.info(f"Submission completed. Sent to {success_count}/{len(ADMIN_IDS)} admins")
    
    def setup_handlers(self) -> None:
        """Setup all bot handlers"""
        if not self.app:
            raise ValueError("Application not initialized")
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start))
        
        # Callback query handlers
        self.app.add_handler(CallbackQueryHandler(self.handle_main_menu, pattern="^menu:"))
        self.app.add_handler(CallbackQueryHandler(self.handle_category_selection, pattern="^cat:"))
        self.app.add_handler(CallbackQueryHandler(self.handle_navigation, pattern="^nav:"))
        self.app.add_handler(CallbackQueryHandler(self.handle_done, pattern="^action:done$"))
        
        # Message handler (collect text messages)
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.collect_message)
        )
    
    def run(self) -> None:
        """Start the bot"""
        # Create application
        self.app = Application.builder().token(TOKEN).build()
        
        # Setup handlers
        self.setup_handlers()
        
        # Start bot
        logger.info("🤖 Bot is starting...")
        print("✅ Bot is running. Press Ctrl+C to stop.")
        self.app.run_polling(drop_pending_updates=True)

# ====================== MAIN ENTRY POINT ======================
def main() -> None:
    """Main function to start the bot"""
    try:
        bot = AnonymousBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == "__main__":
    main()
