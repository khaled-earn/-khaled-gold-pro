import os
import asyncio
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # حط التوكن الجديد هنا كـ Env Variable

# --- حساب المؤشرات الحقيقية ---
def calc_indicators(df):
    close = df['Close']
    high = df['High']
    low = df['Low']
    vol = df['Volume']
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # EMA 20/50
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    
    # CHOP
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    chop = 100 * np.log10((atr.rolling(14).sum()) / (high.rolling(14).max() - low.rolling(14).min())) / np.log10(14)
    
    # ATR for SL/TP
    return rsi.iloc[-1], ema20.iloc[-1], ema50.iloc[-1], chop.iloc[-1], atr.iloc[-1], close.iloc[-1], vol.iloc[-1], vol.rolling(20).mean().iloc[-1]

def get_gold_signal():
    df = yf.download("GC=F", period="1d", interval="5m", progress=False)
    if df.empty or len(df) < 60:
        return None
    rsi, ema20, ema50, chop, atr, price, vol, vol_avg = calc_indicators(df)
    
    trend_bull = ema20 > ema50
    trend_bear = ema20 < ema50
    ema_up = ema20 > ema50
    ema_down = ema20 < ema50
    
    # الفلترة المصلحة - تمنع RSI 88
    is_overbought = rsi > 80
    is_oversold = rsi < 20
    valid_rsi_buy = 55 < rsi < 72
    valid_rsi_sell = 28 < rsi < 45
    
    real_buy = trend_bull and valid_rsi_buy and ema_up and chop < 55 and vol > vol_avg and not is_overbought
    real_sell = trend_bear and valid_rsi_sell and ema_down and chop < 55 and vol > vol_avg and not is_oversold
    
    if real_buy:
        signal = "BUY"
        power = "6/6"
        sl = price - atr*1.5
        tp1 = price + atr*1.2
        tp2 = price + atr*2.5
        tp3 = price + atr*4.0
    elif real_sell:
        signal = "SELL"
        power = "6/6"
        sl = price + atr*1.5
        tp1 = price - atr*1.2
        tp2 = price - atr*2.5
        tp3 = price - atr*4.0
    else:
        signal = "HOLD"
        power = "2/6"
        sl = price - atr*1.5 if trend_bull else price + atr*1.5
        tp1 = tp2 = tp3 = price
    
    return {
        "price": round(float(price),2),
        "rsi": round(float(rsi),1),
        "ema20": round(float(ema20),2),
        "ema50": round(float(ema50),2),
        "chop": round(float(chop),1),
        "atr": round(float(atr),2),
        "vol_ratio": round(float(vol/vol_avg),2),
        "signal": signal,
        "power": power,
        "sl": round(float(sl),2),
        "tp1": round(float(tp1),2),
        "tp2": round(float(tp2),2),
        "tp3": round(float(tp3),2),
        "trend": "صاعد" if trend_bull else "هابط"
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦅 Golden Eagle Pro اشتغل...\n"
        "راح أدزلك إشارات الذهب الحقيقية كل 5 دقايق بنفس الجدول الأبيض\n"
        "اكتب /gold حتى تشوف السعر الحالي"
    )

async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_gold_signal()
    if not data:
        await update.message.reply_text("السوق مسكر حالياً")
        return
    # الجدول الأبيض
    msg = f"""
🦅 **Golden Eagle Pro - {data['signal']}**
💰 السعر: {data['price']}$
📊 RSI: {data['rsi']} | CHOP: {data['chop']} | ATR: {data['atr']}
📈 الترند: {data['trend']} | القوة: {data['power']}
🔊 الحجم: {data['vol_ratio']}x

━━━━━━━━━━━━━━
📍 الدخول: {data['price']}$
🛑 الوقف: {data['sl']}$
🎯 هدف1: {data['tp1']}$
🎯 هدف2: {data['tp2']}$
🎯 هدف3: {data['tp3']}$
━━━━━━━━━━━━━━
⚠️ أمن على الدخول بعد +8$

⏰ كل 5 دقايق تحديث تلقائي
"""
    await update.message.reply_text(msg)

async def auto_signal(context: ContextTypes.DEFAULT_TYPE):
    # يدز إشارة تلقائية فقط اذا BUY/SELL قوي
    data = get_gold_signal()
    if data and data['signal'] in ['BUY','SELL'] and data['power'] == '6/6':
        chat_id = context.job.chat_id
        await context.bot.send_message(chat_id=chat_id, text=f"🚨 إشارة قوية {data['signal']} GOLD @ {data['price']}$ | RSI {data['rsi']} | قوة {data['power']}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    # تفعيل الإرسال التلقائي - حط الـ chat_id مالك
    # app.job_queue.run_repeating(auto_signal, interval=300, first=10, chat_id=YOUR_CHAT_ID)
    app.run_polling()

if __name__ == "__main__":
    main()
