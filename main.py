#!/usr/bin/env python3
"""
VANGUARD V3 - PURE BOT (No Web Server Conflict)
"""
import os
import time
import asyncpg
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from auditor import VanguardAuditor

# --- CONFIGURATION ---
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
MY_ID = os.getenv("TELEGRAM_CHAT_ID")
RPC_URL = os.getenv("RPC_URL", "https://eth.llamarpc.com")
DATABASE_URL = os.getenv("DATABASE_URL")

# --- INITIALIZE ---
audit_engine = VanguardAuditor(RPC_URL)

# --- DATABASE LOGGING ---
async def log_scan(target, issues, price):
    if not DATABASE_URL: return
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vanguard_logs (
                id SERIAL PRIMARY KEY,
                target TEXT,
                issues INT,
                fix_price INT,
                status TEXT,
                created_at BIGINT
            )
        """)
        status = "🔴 CRITICAL" if issues > 0 else "🟢 SECURE"
        await conn.execute("INSERT INTO vanguard_logs (target, issues, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5)", target, issues, price, status, int(time.time()))
        await conn.close()
    except Exception as e: print(f"DB Error: {e}")

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡 **VANGUARD ONLINE.**\nSend me a Website URL or Wallet Address.")

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    msg = await update.message.reply_text("🛰 **Scanning...**")
    try:
        pdf_path, admin_brief = audit_engine.analyze_target(text)
        price = 300
        issues = 1 if "Issues" in admin_brief else 0
        await log_scan(text, issues, price)

        if pdf_path:
            await update.message.reply_document(document=open(pdf_path, 'rb'), caption="✅ **REPORT GENERATED.**")
            if CHANNEL_ID:
                try: await context.bot.send_message(chat_id=CHANNEL_ID, text=f"🚨 **TARGET AUDITED:** {text}\n⚠️ Risks Found.", parse_mode="Markdown")
                except: pass
            if MY_ID:
                try: await context.bot.send_message(chat_id=MY_ID, text=admin_brief)
                except: pass
            await msg.delete()
        else:
            await msg.edit_text("❌ Scan Failed.")
    except Exception as e: await msg.edit_text(f"⚠️ Error: {e}")

# --- RUNNER ---
def main():
    print("🚀 VANGUARD BOT STARTED...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.run_polling()

if __name__ == "__main__":
    main()


