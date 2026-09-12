from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
  app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
import asyncio
import requests
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

try:
    asyncio.set_event_loop(
        asyncio.new_event_loop()
    )
except:
    pass

async def start(update, context):
    await update.message.reply_text(
        "🔥 Khaled Gold Pro شغال"
    )

async def gold(update, context):
    try:
        r = requests.get(
            "https://api.gold-api.com/price/XAU",
            timeout=10
        ).json()
        price = r.get('price', 0)
        await update.message.reply_text(
            f"الذهب: ${price}"
        )
    except:
        await update.message.reply_text(
            "الذهب: 2650$ تجريبي"
        )

def main():
    app = Application.builder().token(
        BOT_TOKEN
    ).build()
    app.add_handler(
        CommandHandler("start", start)
    )
    app.add_handler(
        CommandHandler("gold", gold)
    )
    app.run_polling()

if __name__ == "__main__":
    main()
