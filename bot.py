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

# user_id: {dice, msg_id, form_msg_id}
waiting_users = {}


# ========================
# /roll — открывает "форму"
# ========================
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # сохраняем ID
    waiting_users[update.message.from_user.id] = {
        "start_msg_id": msg.message_id,
        "user_cmd_id": update.message.message_id
    }


# ========================
# выбор кубика
# ========================
async def select_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    dice = int(query.data.split("_")[1])

    # сообщение формы
    form_msg = await query.message.reply_text(
        f"✍️ Введи список (кубик d{dice})\n(каждый пункт с новой строки)"
    )

    # можно закрепить (если бот админ)
    try:
        await context.bot.pin_chat_message(
            chat_id=query.message.chat_id,
            message_id=form_msg.message_id,
            disable_notification=True
        )
    except:
        pass

    waiting_users[user_id].update({
        "dice": dice,
        "form_msg_id": form_msg.message_id
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
# обработка формы
# ========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in waiting_users:
        return

    data = waiting_users.pop(user_id)

    text = update.message.text or ""
    items = [i.strip() for i in text.split("\n") if i.strip()]

    if not items:
        return

    dice = data.get("dice", 6)

    # отправка результата
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=process_items(items, dice)
    )

    # удаление сообщений
    for msg_id in [
        update.message.message_id,
        data.get("start_msg_id"),
        data.get("user_cmd_id"),
        data.get("form_msg_id")
    ]:
        try:
            if msg_id:
                await context.bot.delete_message(
                    chat_id=update.message.chat_id,
                    message_id=msg_id
                )
        except:
            pass


# ========================
# запуск
# ========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("roll", roll))
app.add_handler(CallbackQueryHandler(select_dice, pattern="dice_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()