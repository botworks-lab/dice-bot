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

# user_id: {msg_id, start_msg_id}
waiting_users = {}


# ========================
# /start
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot_msg = await update.message.reply_text(
        "🎲 Бот для бросков кубиков\n\nНажми кнопку 👇",
        reply_markup=reply_markup
    )

    # сохраняем сообщение /start и сообщение бота
    waiting_users[update.message.from_user.id] = {
        "start_msg_id": update.message.message_id,
        "bot_msg_id": bot_msg.message_id
    }


# ========================
# кнопка
# ========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id in waiting_users and "waiting" in waiting_users[user_id]:
        return

    msg = await query.message.reply_text(
        "✍️ Отправь список (каждый пункт с новой строки)"
    )

    if user_id not in waiting_users:
        waiting_users[user_id] = {}

    waiting_users[user_id]["waiting"] = True
    waiting_users[user_id]["hint_msg_id"] = msg.message_id


# ========================
# генерация
# ========================
def process_items(items):
    return "\n".join(
        f"{item} — 🎲 {random.randint(1, 6)}" for item in items
    )


# ========================
# обработка списка
# ========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in waiting_users or "waiting" not in waiting_users[user_id]:
        return

    text = update.message.text or ""
    lines = text.split("\n")
    items = [i.strip() for i in lines if i.strip()]

    if not items:
        return

    data = waiting_users.pop(user_id)

    # 1. отправляем результат
    await update.message.reply_text(process_items(items))

    # 2. удаляем всё лишнее
    try:
        await update.message.delete()  # список
    except:
        pass

    # подсказка
    try:
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=data.get("hint_msg_id")
        )
    except:
        pass

    # сообщение с кнопкой
    try:
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=data.get("bot_msg_id")
        )
    except:
        pass

    # /start
    try:
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=data.get("start_msg_id")
        )
    except:
        pass


# ========================
# запуск
# ========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()