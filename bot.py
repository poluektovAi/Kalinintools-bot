import os
import threading
from flask import Flask

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= НАСТРОЙКИ =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 660874323

# ================= FLASK ДЛЯ RENDER =================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask).start()

# ================= МЕНЮ =================

def build_menu():
    keyboard = [
        [InlineKeyboardButton("📦 Остатки", callback_data="stocks")],
        [InlineKeyboardButton("🔥 Акции", callback_data="sales")],
        [InlineKeyboardButton("💸 Распродажа", callback_data="clearance")],
        [InlineKeyboardButton("📝 Сделать заказ", callback_data="order")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выбери действие:",
        reply_markup=build_menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "stocks":
        await query.message.reply_text(
            "Остатки:\nhttps://docs.google.com/spreadsheets/d/1F5a_kQVLDAI8aTGX8Bh8aFE8G6jThAXf/edit?usp=sharing&ouid=100603441846947403910&rtpof=true&sd=true"
        )

    elif query.data == "sales":
        await query.message.reply_photo(
            photo="https://via.placeholder.com/600x400?text=SALE"
        )

    elif query.data == "clearance":
        await query.message.reply_text(
            "Распродажа:\nhttps://docs.google.com/spreadsheets/d/1cWHguibILTdIAd5ZOUGf1NlBde4y_jNl/edit?usp=sharing&ouid=100603441846947403910&rtpof=true&sd=true"
        )

    elif query.data == "order":
        context.user_data["ordering"] = True
        await query.message.reply_text(
            "Отправь заказ одним сообщением:\n"
            "— текст\n"
            "— фото\n"
            "— файл\n"
            "Можно всё вместе."
        )

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("ordering"):
        return

    await context.bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    await update.message.reply_text("✅ Заказ принят и отправлен в обработку.")
    context.user_data["ordering"] = False

# ================= ЗАПУСК =================

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO | filters.Document.ALL,
            handle_order
        )
    )

    print("BOT STARTED")
    application.run_polling()

if __name__ == "__main__":
    main()
