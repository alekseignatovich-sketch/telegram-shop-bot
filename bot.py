import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# === Конфигурация ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Переменная окружения BOT_TOKEN не задана!")

# Пример каталога (можно заменить на JSON/БД)
PRODUCTS = {
    "1": {"name": "Разукрашка 'Звёздная ночь'", "price": "5$", "file_id": os.getenv("FILE_ID_1", "")},
    "2": {"name": "Шаблон Telegram-магазина", "price": "10$", "file_id": os.getenv("FILE_ID_2", "")},
    "3": {"name": "Готовый бот-каталог (под ключ)", "price": "50$", "file_id": os.getenv("FILE_ID_3", ""), "ready": True},
}

def snowflake_button(text: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(f"❄️ {text}", callback_data=text)

def product_menu():
    buttons = []
    for pid, prod in PRODUCTS.items():
        if not prod.get("ready", False):
            continue
        name = prod["name"]
        price = prod["price"]
        buttons.append([InlineKeyboardButton(f"📦 {name} — {price}", callback_data=f"buy_{pid}")])
    buttons.append([snowflake_button("Назад в меню")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎄 *Добро пожаловать в магазин цифровых товаров!* 🎄\n\n"
        "Выберите товар ниже ⬇️\n"
        "Все покупки — мгновенная доставка! 💾"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=product_menu())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "Назад в меню":
        await start(update, context)
    elif data.startswith("buy_"):
        pid = data[4:]
        prod = PRODUCTS.get(pid)
        if not prod:
            await query.edit_message_text("❌ Товар не найден.")
            return
        caption = f"✅ *{prod['name']}*\n💰 Цена: {prod['price']}\n\n📥 Нажмите, чтобы получить файл:"
        await query.edit_message_text(
            caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💾 Скачать товар", callback_data=f"send_{pid}")],
                [snowflake_button("Назад к товарам")]
            ])
        )
    elif data.startswith("send_"):
        pid = data[5:]
        prod = PRODUCTS.get(pid)
        file_id = prod.get("file_id") if prod else None
        if file_id:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file_id,
                caption=f"🎁 Ваш товар: *{prod['name']}*!",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("⚠️ Файл не настроен. Обратитесь к администратору.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("🚀 Бот запущен и ожидает сообщения...")
    app.run_polling()
