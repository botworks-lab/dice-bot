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
    # аргументы после команды
    args = context.args

    # если написали /roll меч щит
    if args:
        items = args
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

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("d", roll))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, roll))

app.run_polling()