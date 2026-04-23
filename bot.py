import random
import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# логирование (очень полезно)
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")


# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 🎲\n\n"
        "Используй команду:\n"
        "/roll список\n\n"
        "Пример:\n"
        "/roll меч щит лук\n\n"
        "или\n"
        "/roll\nмеч\nщит\nлук"
    )


# команда /roll
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("MESSAGE:", update.message.text)  # для дебага

    # если есть аргументы (/roll меч щит)
    if context.args:
        items = context.args
    else:
        # если список с новой строки
        text = update.message.text
        parts = text.split("\n")[1:]
        items = [i.strip() for i in parts if i.strip()]

    if not items:
        await update.message.reply_text("Напиши список после /roll")
        return

    result = []

    for item in items:
        dice = random.randint(1, 6)
        result.append(f"{item} — 🎲 {dice}")

    await update.message.reply_text("\n".join(result))


# fallback (если просто текст, например @бот)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # если просто текст без команды — можно игнорить
    if text.startswith("/"):
        return

    # разбиваем по строкам
    lines = text.split("\n")
    items = [i.strip() for i in lines if i.strip()]

    if not items:
        return

    result = []

    for item in items:
        dice = random.randint(1, 6)
        result.append(f"{item} — 🎲 {dice}")

    await update.message.reply_text("\n".join(result))


# запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("roll", roll))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()