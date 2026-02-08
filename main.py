#!/usr/bin/env python3
"""
VANGUARD V3 - AUDIT BOT (Background Worker)
Features: Scans Websites/Wallets, Generates PDFs, Logs to Database
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

# --- INITIALIZE AUDITOR ---
# This uses the auditor.py file we created earlier
audit_engine = VanguardAuditor(RPC_URL)

# --- DATABASE LOGGING ---
async def log_scan(target, issues, price):
    """
    Saves the scan result to Supabase so the Dashboard can show it.
    """
    if not DATABASE_URL: return
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        # Create Table if it doesn't exist
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

        # Determine Status
        status = "🔴 CRITICAL" if issues > 0 else "🟢 SECURE"

        # Insert Data
        await conn.execute(
            "INSERT INTO vanguard_logs (target, issues, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5)",
            target, issues, price, status, int(time.time())
        )
        await conn.close()
        print(f"✅ Logged {target} to Dashboard.")
    except Exception as e:
        print(f"⚠️ DB Log Error: {e}")

# --- TELEGRAM HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡 **VANGUARD SECURITY ENGINE**\n\n"
        "Send me a **Website URL** (e.g., example.com) or **Ethereum Wallet**.\n"
        "I will generate a Professional Audit PDF."
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.effective_user

    msg = await update.message.reply_text("🛰 **Scanning Target... Generating PDF...**")

    try:
        # 1. Run the Audit (Using auditor.py)
        # This returns the filename of the PDF and the text for the admin
        pdf_path, admin_brief = audit_engine.analyze_target(text)

        # Calculate pricing for the Database Log
        # (We extract the price from the text brief or default to 300)
        price = 300
        issues = 1
        if "Issues: 0" in admin_brief:
            issues = 0
            price = 0

        # 2. Log to Dashboard
        await log_scan(text, issues, price)

        if pdf_path:
            # 3. Send PDF to User
            await update.message.reply_document(
                document=open(pdf_path, 'rb'),
                caption="✅ **AUDIT COMPLETE.**\nHere is your security report. Forward this to your developer."
            )

            # 4. Post to Channel (Marketing)
            if CHANNEL_ID:
                try:
                    alert = f"🚨 **VULNERABILITY DETECTED**\n\n🎯 Target: `{text}`\n⚠️ Risk Level: HIGH\n🛠 Status: PENDING FIX\n\n*Vanguard Engine*"
                    await context.bot.send_message(chat_id=CHANNEL_ID, text=alert, parse_mode="Markdown")
                    await context.bot.send_document(chat_id=CHANNEL_ID, document=open(pdf_path, 'rb'))
                except: pass

            # 5. Send Pricing Quote to YOU (Private)
            if MY_ID:
                try: await context.bot.send_message(chat_id=MY_ID, text=admin_brief)
                except: pass

            await msg.delete()
        else:
            await msg.edit_text("❌ Scan Failed. Please send a valid URL (https://) or ETH Wallet (0x...).")

    except Exception as e:
        await msg.edit_text(f"⚠️ System Error: {e}")

# --- MAIN RUNNER ---
def main():
    print("🚀 VANGUARD BOT STARTED...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    app.run_polling()

if __name__ == "__main__":
    main()
