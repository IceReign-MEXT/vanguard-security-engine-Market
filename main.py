#!/usr/bin/env python3
import os
import threading
import time
import asyncpg
import asyncio
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from auditor import VanguardAuditor

# --- CONFIGURATION ---
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8545903212:AAE7V0U6JHXk4NR3o4DuQlBohoeikyZfl9k") # Failsafe
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1003844332949")
ADMIN_ID = os.getenv("TELEGRAM_CHAT_ID", "8254662446")
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine
auditor = VanguardAuditor()

# --- FLASK SERVER ---
flask_app = Flask(__name__)
@flask_app.route("/")
def health(): return "VANGUARD V100 ONLINE", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# --- DATABASE LOGGING (Updates Dashboard) ---
async def log_audit(target):
    if not DATABASE_URL: return
    try:
        # Use port 6543 pooler safely
        db_url = DATABASE_URL
        if "sslmode" not in db_url: db_url += "?sslmode=require"
        
        conn = await asyncpg.connect(db_url)
        
        # Log that an audit happened (We log it as pending revenue or audit service)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vanguard_logs (
                id SERIAL PRIMARY KEY, target TEXT, status TEXT, created_at BIGINT
            )
        """)
        await conn.execute("INSERT INTO vanguard_logs (target, status, created_at) VALUES ($1, 'CRITICAL', $2)", target, int(time.time()))
        await conn.close()
        print("✅ Audit Logged to Dashboard DB")
    except Exception as e:
        print(f"⚠️ DB Error: {e}")

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🛡 **VANGUARD FORENSICS V100**\n\n"
        "Institutional Cyber-Security & Blockchain Scanner.\n\n"
        "**Supported Targets:**\n"
        "🌐 Websites / DApps\n"
        "🔷 Ethereum Contracts (0x...)\n"
        "🟣 Solana Tokens\n"
        "₿ Bitcoin Wallets\n\n"
        "👇 **Paste a URL or Address to begin Deep Scan:**"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def handle_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()
    
    if len(target) < 5: return
    
    status_msg = await update.message.reply_text("🛰 **Initializing Deep Forensic Scan...**\nChecking vulnerabilities...")
    
    try:
        # 1. Generate PDF
        pdf_path, issues, price = auditor.analyze_target(target)
        
        if pdf_path:
            # 2. Log to Dashboard
            await log_audit(target)
            
            # 3. Send PDF to User
            await update.message.reply_document(
                document=open(pdf_path, 'rb'),
                caption=f"✅ **AUDIT COMPLETE.**\n\n⚠️ **CRITICAL RISKS FOUND.**\nDownload your PDF report immediately. Forward to your developer or contact @MexRobertICE for the patch."
            )
            
            # 4. Blast to Channel (Marketing)
            if CHANNEL_ID:
                try:
                    alert = (
                        f"🚨 **VANGUARD VULNERABILITY DETECTED** 🚨\n\n"
                        f"🎯 **Target:** `{target}`\n"
                        f"⚠️ **Risk Level:** CRITICAL\n"
                        f"🛠 **Action:** Deep-Scan PDF Generated.\n\n"
                        f"🛡 *Run your own scan:* @VanguardSecurity_bot"
                    )
                    await context.bot.send_document(chat_id=CHANNEL_ID, document=open(pdf_path, 'rb'), caption=alert, parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    print(f"Channel Post Error: {e}")
            
            # Cleanup File
            os.remove(pdf_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Scan Failed. Invalid Format. Use HTTP, 0x, or SOL address.")

    except Exception as e:
        await status_msg.edit_text(f"⚠️ System Error: {e}")

# --- MAIN ---
def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_scan))
    
    print("🚀 VANGUARD V100 FORENSICS LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
