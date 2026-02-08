#!/usr/bin/env python3
import os
import time
import asyncio
import asyncpg
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from auditor import VanguardAuditor

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
MY_ID = os.getenv("TELEGRAM_CHAT_ID")
RPC_URL = os.getenv("RPC_URL", "https://eth.llamarpc.com")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = VanguardAuditor(RPC_URL)

async def log_db(target, issues, price):
    if not DATABASE_URL: return
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vanguard_logs (
                id SERIAL PRIMARY KEY, target TEXT, issues INT, fix_price INT, status TEXT, created_at BIGINT
            )
        """)
        status = "🔴 CRITICAL" if issues > 0 else "🟢 SECURE"
        await conn.execute("INSERT INTO vanguard_logs (target, issues, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5)", target, issues, price, status, int(time.time()))
        await conn.close()
    except Exception as e: print(f"DB Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡 **VANGUARD ONLINE**\nSend a Link or Wallet Address.")

async def handle_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    msg = await update.message.reply_text("🛰 **Scanning...**")

    try:
        pdf_path, brief = engine.analyze_target(text)

        # Parse Brief for DB
        issues = 0
        price = 0
        if "Issues:" in brief:
            issues = int(brief.split("Issues: ")[1].split("\n")[0])
        if "$" in brief:
            price = int(float(brief.split("$")[1].split("\n")[0]))

        await log_db(text, issues, price)

        if pdf_path:
            await update.message.reply_document(open(pdf_path, 'rb'), caption="✅ **REPORT READY.**")

            # Channel Alert
            if CHANNEL_ID and issues > 0:
                try: await context.bot.send_message(CHANNEL_ID, f"🚨 **VULNERABILITY FOUND**\nTarget: `{text}`\nRisk: HIGH\n*Vanguard Security*")
                except: pass

            # Admin Quote
            if MY_ID:
                try: await context.bot.send_message(MY_ID, brief)
                except: pass

            os.remove(pdf_path) # Clean up
            await msg.delete()
        else:
            await msg.edit_text("❌ Scan Failed.")

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_scan))
    print("🚀 VANGUARD BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
