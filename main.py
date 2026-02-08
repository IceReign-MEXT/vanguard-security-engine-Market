#!/usr/bin/env python3
"""
VANGUARD V3 - BOT + DATABASE CONNECTOR
"""

import os
import threading
import time
import asyncpg
import asyncio
from flask import Flask
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
flask_app = Flask(__name__)

@flask_app.route("/")
def health(): return "VANGUARD BOT ONLINE", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# --- DATABASE SETUP ---
async def log_scan(target, issues, price):
    if not DATABASE_URL: return
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        # Create Table if needed
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
        # Log the Scan
        status = "🔴 CRITICAL" if issues > 0 else "🟢 SECURE"
        await conn.execute(
            "INSERT INTO vanguard_logs (target, issues, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5)",
            target, issues, price, status, int(time.time())
        )
        await conn.close()
        print(f"✅ Logged {target} to Dashboard.")
    except Exception as e:
        print(f"⚠️ DB Error: {e}")

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡 **VANGUARD ONLINE.**\nSend me a URL or Wallet to audit.")

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    msg = await update.message.reply_text("🛰 **Scanning Target...**")

    try:
        # 1. Run Audit
        pdf_path, admin_brief = audit_engine.analyze_target(text)

        # Calculate fake price for DB log based on brief content (simple extraction)
        price = 300 # Default
        issues = 1  # Default
        if "Issues: 0" in admin_brief:
            issues = 0
            price = 0

        # 2. Save to Database (So Dashboard shows it)
        await log_scan(text, issues, price)

        if pdf_path:
            await update.message.reply_document(open(pdf_path, 'rb'), caption="✅ **REPORT GENERATED.**")

            # Post to Channel
            if CHANNEL_ID:
                alert = f"🚨 **THREAT DETECTED**\n\n🎯 Target: `{text}`\n⚠️ Issues: {issues}\n🛠 Status: PENDING FIX\n\n*Vanguard Engine*"
                await context.bot.send_message(chat_id=CHANNEL_ID, text=alert, parse_mode="Markdown")
                await context.bot.send_document(chat_id=CHANNEL_ID, document=open(pdf_path, 'rb'))

            if MY_ID:
                await context.bot.send_message(chat_id=MY_ID, text=admin_brief)

            await msg.delete()
        else:
            await msg.edit_text("❌ Scan Failed. Invalid Target.")

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

# --- RUNNER ---
def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    print("🚀 VANGUARD BOT LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
