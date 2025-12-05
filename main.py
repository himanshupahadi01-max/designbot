import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

ASK_TYPE, ASK_DETAILS, ASK_CONTACT = range(3)

PRICE_MAP = {
    "Thumbnail": "₹49",
    "DP / Profile Pic": "₹39",
    "Poster / Banner": "₹79",
    "Logo": "₹99",
}

UPI_ID = "9958034727-2@ybl"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Namaste 👋\n\n"
        "Is bot se aap *design order* de sakte ho:\n"
        f"- Thumbnail 🎬 ({PRICE_MAP['Thumbnail']})\n"
        f"- DP / Profile Pic 🧑‍💻 ({PRICE_MAP['DP / Profile Pic']})\n"
        f"- Poster / Banner 🎨 ({PRICE_MAP['Poster / Banner']})\n"
        f"- Logo ✨ ({PRICE_MAP['Logo']})\n\n"
        "Order dene ke liye: /order likho ✅\n\n"
        "_Normal delivery time: 1–3 hours_ ⏳"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    msg = (
        "Kya banwana hai? Choose karo (number likho):\n\n"
        f"1️⃣ Thumbnail ({PRICE_MAP['Thumbnail']})\n"
        f"2️⃣ DP / Profile Pic ({PRICE_MAP['DP / Profile Pic']})\n"
        f"3️⃣ Poster / Banner ({PRICE_MAP['Poster / Banner']})\n"
        f"4️⃣ Logo ({PRICE_MAP['Logo']})\n\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    return ASK_TYPE

def detect_type(user_text: str) -> str:
    t = user_text.lower().strip()
    if t in ["1", "thumbnail", "yt thumbnail"]: return "Thumbnail"
    if t in ["2", "dp", "profile"]: return "DP / Profile Pic"
    if t in ["3", "poster", "banner"]: return "Poster / Banner"
    if t in ["4", "logo"]: return "Logo"
    return user_text.strip()

async def ask_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    design_type = detect_type(user_text)
    context.user_data["type"] = design_type
    price = PRICE_MAP.get(design_type, "Custom")
    await update.message.reply_text(
        f"Thik hai, aapko *{design_type}* chahiye 🎨\n"
        f"Price: *{price}*\n\n"
        "Ab details bhejo:"
    )
    return ASK_DETAILS

async def ask_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["details"] = update.message.text.strip()
    await update.message.reply_text("Ab apna contact bhejo:")
    return ASK_CONTACT

async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text.strip()
    user = update.message.from_user
    order_text = f"""🆕 *New Design Order*  

👤 From: {user.first_name}
📦 Type: {context.user_data['type']}
💰 Price: {PRICE_MAP.get(context.user_data['type'], 'Custom')}
📝 Details: {context.user_data['details']}
📲 Contact: {context.user_data['contact']}
💳 Suggested UPI: `{UPI_ID}`
"""
    await update.message.reply_text(
        f"Thank you! 🎉\nPayment karo: `{UPI_ID}`\nScreenshot bhejo.",
        parse_mode="Markdown"
    )
    await context.application.bot.send_message(
        chat_id=ADMIN_CHAT_ID, text=order_text, parse_mode="Markdown"
    )
    return ConversationHandler.END

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("order", order_start)],
        states={
            ASK_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_type)],
            ASK_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_details)],
            ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact)],
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    print("Bot Running..")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
