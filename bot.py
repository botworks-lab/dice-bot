import random
import os
import logging
import time

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

# хранение состояния (user_id: timestamp)
waiting_users = {}


# ========================
# /start
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎲 Бот для бросков кубиков\n\nНажми кнопку 👇",
        reply_markup=reply_markup
    )


# ========================
# кнопка
# ========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # защита от повторного нажатия (3 сек)
    if user_id in waiting_users and time.time() - waiting_users[user_id] < 3:
        return

    waiting_users[user_id] = time.time()

    await query.message.reply_text(
        "✍️ Отправь список (каждый пункт с новой строки)"
    )


# ========================
# генерация
# ========================
def process_items(items):
    result = []
    for item in items:
        dice = random.randint(1, 6)
        result.append(f"{item} — 🎲 {dice}")
    return "\n".join(result)


# ========================
# /roll
# ========================
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

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
        return

    await update.message.reply_text(process_items(items))


# ========================
# обработка списка после кнопки
# ========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in waiting_users:
        return

    text = update.message.text or ""
    lines = text.split("\n")
    items = [i.strip() for i in lines if i.strip()]

    if not items:
        return

    # УДАЛЯЕМ из режима сразу
    waiting_users.pop(user_id, None)

    await update.message.reply_text(process_items(items))

    # удаляем сообщение пользователя
    try:
        await update.message.delete()
    except:
        pass


# ========================
# запуск
# ========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("roll", roll))

app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()