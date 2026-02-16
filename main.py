#!/usr/bin/env python3
"""
VANGUARD V50 - SECURITY WARLORD
Features: PDF Generation, Auto-Quoting, Dashboard Sync
"""

import os
import time
import asyncio
import asyncpg
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from auditor import AlienAuditor

# --- CONFIG ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("VIP_CHANNEL_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

auditor = AlienAuditor()

# --- FLASK ---
flask_app = Flask(__name__)
@flask_app.route("/")
def health(): return "VANGUARD ACTIVE 🛡️", 200
def run_web(): flask_app.run(host="0.0.0.0", port=8080)

# --- DB LOGGING ---
async def log_audit(target, price, status):
    if not DATABASE_URL: return
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        # Reuse 'cp_payments' for audits, but mark service as 'AUDIT'
        await conn.execute("""
            INSERT INTO cp_payments (telegram_id, amount_usd, service_type, tx_hash, created_at) 
            VALUES ('SYSTEM', $1, 'AUDIT_SCAN', $2, $3)
        """, price, target, int(time.time()))
        await conn.close()
    except: pass

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡 **VANGUARD V50 ONLINE**\n\n"
        "I am the Deep-Scan Security Engine.\n\n"
        "👇 **HOW TO USE:**\n"
        "Paste a **Website URL** or **Wallet Address**.\n"
        "I will generate a PDF Report for you to send to the client."
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()
    user = update.effective_user

    msg = await update.message.reply_text(f"🛰 **Scanning {target}...**\n(Analyzing Packets...)")

    try:
        # Run Alien Brain
        pdf_file, issues, price = auditor.scan_target(target)

        if pdf_file:
            # 1. Send PDF to User (You)
            await update.message.reply_document(
                document=open(pdf_file, 'rb'),
                caption=f"✅ **AUDIT COMPLETE**\n\n📉 Score: {100-(len(issues)*10)}/100\n💰 Quote: ${price}\n\n*Forward this PDF to the owner to close the deal.*"
            )

            # 2. Post to Channel (Social Proof)
            if CHANNEL_ID:
                alert = (
                    f"🚨 **VANGUARD DETECTED VULNERABILITY**\n\n"
                    f"🎯 **Target:** `{target}`\n"
                    f"⚠️ **Risk:** CRITICAL\n"
                    f"🛠 **Action:** Fix Proposal Sent.\n\n"
                    f"🛡 *Secured by IceGods*"
                )
                try: await context.bot.send_message(CHANNEL_ID, alert, parse_mode="Markdown")
                except: pass

            # 3. Log to Dashboard
            await log_audit(target, price, "CRITICAL")

            # Cleanup
            os.remove(pdf_file)
            await msg.delete()
        else:
            await msg.edit_text("❌ Scan Failed. Invalid Link/Wallet.")

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

# --- MAIN ---
def main():
    Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan))

    print("🚀 VANGUARD V50 LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
