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

BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен из Render
ADMIN_CHAT_ID = 660874323  # <-- ТВОЙ Telegram user_id (ТОЛЬКО ЦИФРЫ)

# ================= FLASK (ДЛЯ RENDER) =================

app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot is running"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask).start()

# ================= КНОПКИ =================

def main_menu():
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
        "Добрый день! Выберите действие:",
        reply_markup=main_menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "stocks":
        await query.message.reply_text(
            "Остатки:\nhttps://docs.google.com/spreadsheets/d/1F5a_kQVLDAI8aTGX8Bh8aFE8G6jThAXf/edit?usp=sharing&ouid=100603441846947403910&rtpof=true&sd=true"
        )

    elif query.data == "sales":
        await query.message.reply_text("Акции:")
        # пример — замени на свои file_id или URL
        await query.message.reply_photo(
            photo="https://via.placeholder.com/600x400?text=SALE"
        )

    elif query.data == "clearance":
        await query.message.reply_text(
            "Распродажа:\nhttps://docs.google.com/spreadsheets/d/YYYY"
        )

    elif query.data == "order":
        context.user_data["ordering"] = True
        await query.message.reply_text(
            "Отправь заказ:\n"
            "— текст\n"
            "— фото\n"
            "— файл\n"
            "Можно всё вместе одним сообщением."
        )

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):

