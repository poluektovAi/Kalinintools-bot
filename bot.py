import os
import smtplib
from email.message import EmailMessage
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

from flask import Flask
import threading

app = Flask(__name__)

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()


BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL_LOGIN = os.getenv("EMAIL_LOGIN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1F5a_kQVLDAI8aTGX8Bh8aFE8G6jThAXf/edit?usp=sharing&ouid=100603441846947403910&rtpof=true&sd=true"

PROMO_IMAGES = [
    "promo1.jpg"
]

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Акции", callback_data="promo")],
        [InlineKeyboardButton("📦 Остатки", callback_data="stock")],
        [InlineKeyboardButton("✉️ Отправить заявку", callback_data="order")]
    ]
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "promo":
        for img in PROMO_IMAGES:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=open(img, "rb")
            )

    elif query.data == "stock":
        await query.message.reply_text(
            f"Остатки по ссылке:\n{GOOGLE_SHEET_URL}"
        )

    elif query.data == "order":
        user_states[query.message.chat_id] = "waiting_text"
        await query.message.reply_text(
            "Напишите текст заявки и прикрепите фото или файл:"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if user_states.get(chat_id) != "waiting_text":
        return

    text = update.message.text or update.message.caption or "Без текста"
    files = []

    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        files.append((file, "photo.jpg"))

    if update.message.document:
        file = await update.message.document.get_file()
        files.append((file, update.message.document.file_name))

    # ВРЕМЕННО: лог вместо почты
    print("ЗАЯВКА ПОЛУЧЕНА")
    print(text)
    print(f"Файлов: {len(files)}")

    user_states.pop(chat_id)

    await update.message.reply_text("✅ Заявка отправлена!")


def send_email(text, files):
    msg = EmailMessage()
    msg["Subject"] = "Новая заявка из Telegram"
    msg["From"] = EMAIL_LOGIN
    msg["To"] = EMAIL_TO
    msg.set_content(text)

    for file, name in files:
        content = file.download_as_bytearray()
        msg.add_attachment(
            content,
            maintype="application",
            subtype="octet-stream",
            filename=name
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()
