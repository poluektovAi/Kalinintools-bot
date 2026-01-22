print("BOT FILE LOADED")

import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_CHAT_ID = 7693224290:AAG76xDm5rEdaRZ87SzHOWzvFA_UTBc5a8I  # <-- СЮДА ВСТАВЬ СВОЙ ID

# Ссылки на Google Таблицы
STOCKS_URL = "https://docs.google.com/spreadsheets/d/1F5a_kQVLDAI8aTGX8Bh8aFE8G6jThAXf/edit?usp=sharing&ouid=100603441846947403910&rtpof=true&sd=true"      # Остатки
SALE_URL = "https://docs.google.com/..."        # Распродажа

user_states = {}

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Остатки", callback_data="stocks")],
        [InlineKeyboardButton("🔥 Акции", callback_data="promo")],
        [InlineKeyboardButton("💸 Распродажа", callback_data="sale")],
        [InlineKeyboardButton("📝 Сделать заказ", callback_data="order")]
    ]

    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- КНОПКИ ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id

    if query.data == "stocks":
        await query.message.reply_text(
            f"📦 Остатки:\n{STOCKS_URL}"
        )

    elif query.data == "sale":
        await query.message.reply_text(
            f"💸 Распродажа:\n{SALE_URL}"
        )

    elif query.data == "promo":
        await query.message.reply_text("🔥 Актуальные акции:")

        for img in ["promo1.jpg", "promo2.jpg", "promo3.jpg"]:
            if os.path.exists(img):
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=open(img, "rb")
                )

    elif query.data == "order":
        user_states[chat_id] = "waiting_order"
        await query.message.reply_text(
            "Отправьте заказ ОДНИМ сообщением:\n"
            "— текст\n"
            "— фото\n"
            "— файл\n"
            "Можно всё вместе."
        )

# ---------- ЗАКАЗ ----------
async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if user_states.get(chat_id) != "waiting_order":
        return

    message = update.message

    text = message.text or message.caption or "Без текста"

    # отправляем админу текст
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📝 НОВЫЙ ЗАКАЗ\n\n{text}"
    )

    # фото
    if message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=message.photo[-1].file_id
        )

    # файл
    if message.document:
        await context.bot.send_document(
            chat_id=ADMIN_CHAT_ID,
            document=message.document.file_id
        )

    user_states.pop(chat_id)

    await message.reply_text(
        "✅ Заказ принят в обработку.\nМы скоро свяжемся с вами."
    )

# ---------- ЗАПУСК ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.Document.ALL,
        handle_order
    ))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
print("END OF FILE")
