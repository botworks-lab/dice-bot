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

# user_id: {"time": ..., "msg_id": ...}
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

    # защита от спама
    if user_id in waiting_users and time.time() - waiting_users[user_id]["time"] < 3:
        return

    msg = await query.message.reply_text(
        "✍️ Отправь список (каждый пункт с новой строки)"
    )

    waiting_users[user_id] = {
        "time": time.time(),
        "msg_id": msg.message_id
    }


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
# обработка списка
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

    data = waiting_users.pop(user_id)

    # удалить сообщение пользователя
    try:
        await update.message.delete()
    except:
        pass

    # удалить подсказку
    try:
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=data["msg_id"]
        )
    except:
        pass

    # отправить результат
    await update.message.reply_text(process_items(items))


# ========================
# запуск
# ========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()