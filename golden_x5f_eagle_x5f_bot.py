import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Khaled Gold Pro شغال - أرسل /gold لمعرفة سعر الذهب")

async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        data = response.json()
        price = data.get('price', 0)
        await update.message.reply_text(f"💰 سعر الذهب الحالي: ${price:.2f}")
    except Exception as e:
        await update.message.reply_text("💰 سعر الذهب: 2650$ (السيرفر مشغول حاليا - تجريبي)")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    app.run_polling()
