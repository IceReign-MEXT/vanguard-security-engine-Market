#!/usr/bin/env python3
"""
VANGUARD SECURITY ENGINE V2
Features: Website/Wallet Audit, PDF Generation, Price Quoting
"""

import os
import threading
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
RPC_URL = os.getenv("RPC_URL")

# Initialize Auditor
audit_engine = VanguardAuditor(RPC_URL)

# --- FLASK SERVER ---
flask_app = Flask(__name__)
@flask_app.route("/")
def health(): return "VANGUARD ACTIVE", 200
def run_web(): flask_app.run(host="0.0.0.0", port=8080)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡 **VANGUARD SECURITY ENGINE**\n\n"
        "Send me a **Website URL** or **Ethereum Wallet**.\n"
        "I will generate a Professional Security PDF."
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.effective_user

    msg = await update.message.reply_text("🛰 **Scanning Target... Generating PDF...**")

    # RUN AUDIT
    try:
        pdf_path, admin_brief = audit_engine.analyze_target(text)

        if pdf_path:
            # 1. SEND PDF TO USER
            await update.message.reply_document(
                document=open(pdf_path, 'rb'),
                caption="✅ **AUDIT COMPLETE.**\nHere is your security report."
            )

            # 2. SEND PDF TO CHANNEL (Marketing)
            if CHANNEL_ID:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"🚨 **NEW VULNERABILITY DETECTED**\n\nTarget: {text}\nStatus: ⚠️ RISKS FOUND\n\n*Vanguard Engine has generated a fix report.*"
                )
                await context.bot.send_document(
                    chat_id=CHANNEL_ID,
                    document=open(pdf_path, 'rb')
                )

            # 3. SEND PRICING GUIDE TO YOU (Private)
            if MY_ID:
                await context.bot.send_message(chat_id=MY_ID, text=admin_brief)

            await msg.delete()
        else:
            await msg.edit_text("❌ Invalid Target. Send a URL (https://...) or Wallet (0x...).")

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

# --- MAIN ---
def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    print("🚀 VANGUARD LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
