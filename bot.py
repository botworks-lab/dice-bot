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

# user_id: данные пользователя
waiting_users = {}


# ========================
# /start — сразу выбор кубика
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("d6", callback_data="dice_6"),
            InlineKeyboardButton("d20", callback_data="dice_20"),
            InlineKeyboardButton("d100", callback_data="dice_100"),
        ]
    ]

    msg = await update.message.reply_text(
        "🎲 Выбери кубик",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    waiting_users[update.message.from_user.id] = {
        "start_msg_id": msg.message_id,
        "user_start_id": update.message.message_id
    }


# ========================
# выбор кубика
# ========================
async def select_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    dice = int(query.data.split("_")[1])

    if user_id not in waiting_users:
        waiting_users[user_id] = {}

    msg = await query.message.reply_text(
        f"✍️ Отправь список (кубик d{dice})"
    )

    waiting_users[user_id].update({
        "dice": dice,
        "msg_id": msg.message_id
    })


# ========================
# генерация
# ========================
def process_items(items, dice):
    result = []
    for item in items:
        roll = random.randint(1, dice)
        result.append(f"{item} — 🎲 {roll}")
    return "\n".join(result)


# ========================
# обработка списка
# ========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in waiting_users:
        return

    data = waiting_users.pop(user_id)

    text = update.message.text or ""
    lines = text.split("\n")
    items = [i.strip() for i in lines if i.strip()]

    if not items:
        return

    dice = data.get("dice", 6)

    # отправка без reply
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=process_items(items, dice)
    )

    # удаление сообщений
    try:
        await update.message.delete()
    except:
        pass

    for key in ["msg_id", "start_msg_id", "user_start_id"]:
        try:
            if data.get(key):
                await context.bot.delete_message(
                    chat_id=update.message.chat_id,
                    message_id=data.get(key)
                )
        except:
            pass


# ========================
# запуск
# ========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(select_dice, pattern="dice_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()