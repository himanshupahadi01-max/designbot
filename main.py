import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Namaste!\n\nApna design requirement yahan bhejo, main admin ko forward kar dunga."
    )


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # admin ko forward
    msg = (
        f"🆕 New Message\n\n"
        f"👤 From: {user.first_name} (id: {user.id})\n"
        f"📩 Text:\n{text}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

    # user ko reply
    await update.message.reply_text(
        "✅ Tumhara message admin tak pahunch gaya.\n"
        "Wo jaldi tumse contact karenge 🙂"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    app.run_polling()


if __name__ == "__main__":
    main()
