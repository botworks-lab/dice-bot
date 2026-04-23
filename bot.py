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

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎲 Бот для броска кубиков\n\n"
        "Используй:\n"
        "/roll список\n\n"
        "или через упоминание:\n"
        "@бот список"
    )


# логика броска
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

    # если есть текст после команды
    if text:
        items = text.replace(",", " ").split()
    else:
        # если список с новой строки
        parts = update.message.text.split("\n")[1:]
        items = [i.strip() for i in parts if i.strip()]

    if not items:
        await update.message.reply_text("Напиши список после /roll")
        return

    await update.message.reply_text(process_items(items))


# обработка через @бот
async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    # проверяем упоминание
    if context.bot.username not in text:
        return

    # убираем @бот
    text = text.replace(f"@{context.bot.username}", "").strip()

    lines = text.split("\n")
    items = [i.strip() for i in lines if i.strip()]

    if not items:
        return

    await update.message.reply_text(process_items(items))


# запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("roll", roll))

# только сообщения с @бот
app.add_handler(MessageHandler(filters.TEXT & filters.Entity("mention"), handle_mention))

app.run_polling()