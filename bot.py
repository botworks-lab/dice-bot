import random
import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

# пользователи, которые ждут ввод списка
waiting_users = set()


# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎲 Бот для бросков кубиков\n\nНажми кнопку 👇",
        reply_markup=reply_markup
    )


# обработка кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    waiting_users.add(user_id)

    await query.message.reply_text(
        "Отправь список (каждый пункт с новой строки)"
    )


# генерация результата
def process_items(items):
    result = []
    for item in items:
        dice = random.randint(1, 6)
        result.append(f"{item} — 🎲 {dice}")
    return "\n".join(result)


# команда /roll
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    # убираем /roll и /roll@bot
    text = text.replace("/roll", "")
    if context.bot.username:
        text = text.replace(f"@{context.bot.username}", "")

    text = text.strip()

    if text:
        items = text.replace(",", " ").split()
    else:
        parts = update.message.text.split("\n")[1:]
        items = [i.strip() for i in parts if i.strip()]

    if not items:
        await update.message.reply_text("Напиши список после /roll")
        return

    await update.message.reply_text(process_items(items))


# обработка через кнопку (режим ожидания)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # если пользователь НЕ в режиме ожидания — игнор
    if user_id not in waiting_users:
        return

    waiting_users.remove(user_id)

    text = update.message.text or ""
    lines = text.split("\n")
    items = [i.strip() for i in lines if i.strip()]

    if not items:
        return

    await update.message.reply_text(process_items(items))

    # попытка удалить сообщение пользователя (если бот админ)
    try:
        await update.message.delete()
    except:
        pass


# запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("roll", roll))

app.add_handler(CallbackQueryHandler(button_handler))

# только текст БЕЗ команд
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()