#!/usr/bin/env python3
"""
Telegram Pakistani SIM Database Bot
With channel verification, SIM / CNIC lookup, banner + help command
"""

import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

# ================= CONFIG =================
BOT_TOKEN = "7954860168:AAGZNkmHH7M84sG42bde0mAvNHorKJCdetM"
CHANNEL_USERNAME = "@danaashiqofficial"
CHANNEL_LINK = "https://t.me/danaashiqofficial"
SIM_API_URL = "https://legendxdata.site/Api/simdata.php?phone="

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ================= FORMAT FUNCTION =================
def format_sim_data(data):
    """Format SIM data response beautifully (multiple records supported)"""
    if not data or "error" in data:
        return """
❌ *NO SIM DATA FOUND* ❌

🚫 *SORRY, NO Free INFORMATION AVAILABLE FOR THIS NUMBER (Whatsapp 03208061149 For Paid Sim Details)*

💡 *TRY:*
• CHECK THE NUMBER FORMAT 
• TRY WITHOUT COUNTRY CODE: 3001234567

🔄 *SEND ANOTHER NUMBER OR CNIC TO SEARCH AGAIN*
       Or Visit 
       WEBSITE : http://officialservices.click
         """

    # ✅ Multiple records (CNIC search)
    if isinstance(data, list):
        if not data:
            return "❌ *NO SIM DATA FOUND* ❌"

        results = []
        for idx, record in enumerate(data, 1):
            results.append(f"""
━━━━━━━━━━━━━━━━━━━━━━
📌 *Record #{idx}*

📱 *NUMBER:* {record.get('Mobile #', 'N/A')}
👤 *NAME:* {record.get('Name', 'Not Available')}
🆔 *CNIC:* {record.get('CNIC', 'N/A')}
📍 *ADDRESS:* {record.get('Address', 'Not Available')}
📡 *OPERATOR:* {record.get('Operator', 'N/A')}
            """)
        return "\n".join(results) + "\n\n🔥 *POWERED BY Dana Ashiq* 🔥"

    # ✅ Single record
    formatted_text = f"""
🎯 *SIM DATABASE RESULT* 🎯

📱 *NUMBER:* {data.get('number', data.get('Mobile #', 'N/A'))}
👤 *NAME:* {data.get('name', data.get('Name', 'Not Available'))}
🆔 *CNIC:* {data.get('cnic', data.get('CNIC', 'N/A'))}
📍 *ADDRESS:* {data.get('address', data.get('Address', 'Not Available'))}
📡 *OPERATOR:* {data.get('operator', data.get('Operator', 'N/A'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 *POWERED BY Dana Ashiq* 🔥
    """
    return formatted_text


# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banner = """
╔════════════════════╗
   🔥 SIM DATABASE BOT 🔥
╚════════════════════╝
"""

    keyboard = [
        [InlineKeyboardButton("✅ JOIN CHANNEL", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🔄 Verify", callback_data="verify")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"{banner}\n"
        f"👋 *WELCOME TO SIM DATABASE BOT*\n\n"
        f"👉 To use this bot you must join our channel {CHANNEL_USERNAME}\n\n"
        f"After joining click Verify ✅\n\n"
        f"⚡ Send */help* to learn how to use me.",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *HELP GUIDE*

You can search for:
1️⃣ *Phone Number* → 03001234567
2️⃣ *CNIC* → 3520212345671

⚡ *Examples:*
• `03001234567`
• `3520212345671`

🔒 *Rules:*
- Number must start with 03
- CNIC must be 13 digits
- Don't use country code (+92)

📢 Join for updates:
👉 {channel}
    """.format(channel=CHANNEL_LINK)

    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "verify":
        user_id = query.from_user.id
        try:
            member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if member.status in ["member", "administrator", "creator"]:
                await query.edit_message_text(
                    "✅ Verification successful!\n\n"
                    "Now send me a *Phone Number (03001234567)* or *CNIC (3520212345671)* to get SIM details.",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await query.edit_message_text(
                    "❌ You must join the channel first!\n\n"
                    f"👉 {CHANNEL_LINK}"
                )
        except Exception as e:
            await query.edit_message_text(
                "⚠️ Error verifying membership. Please join the channel first!"
            )
            logger.error(e)


async def sim_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # ✅ Validation (Phone OR CNIC)
    if not (text.isdigit() and ((text.startswith("03") and len(text) == 11) or len(text) == 13)):
        await update.message.reply_text(
            "❌ Invalid input!\n\n"
            "✔ Example Phone: 03001234567\n"
            "✔ Example CNIC: 3520212345671"
        )
        return

    await update.message.reply_text("⏳ Please wait... Fetching SIM Data...")

    try:
        response = requests.get(SIM_API_URL + text, timeout=15)
        data = response.json()
        formatted = format_sim_data(data)
        await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("⚠️ Error fetching data. Please try again later.")


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sim_lookup))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()