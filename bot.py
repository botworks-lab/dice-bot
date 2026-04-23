import random
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь список строками — я кину кубик 🎲\n"
        "Можно указать /d20 или /d6"
    )

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # имя бота
    bot_username = context.bot.username

    # если это группа — проверяем упоминание или команду
    if update.message.chat.type != "private":
        if not (text.startswith("/roll") or f"@{bot_username}" in text):
            return

    # убираем команду и имя бота из текста
    text = text.replace("/roll", "")
    text = text.replace(f"@{bot_username}", "").strip()

    lines = text.split("\n")

    dice_max = 6
    result = []

    for line in lines:
        item = line.strip()
        if item:
            dice = random.randint(1, dice_max)
            result.append(f"{item} — 🎲 {dice}")

    if result:
        await update.message.reply_text("\n".join(result))

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("d", roll))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, roll))

app.run_polling()