import os
import time
import asyncio
import asyncpg
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from auditor import VanguardAuditor

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
ADMIN_ID = os.getenv("TELEGRAM_CHAT_ID")
RAW_DB = os.getenv("DATABASE_URL", "")
DB_URL = RAW_DB.replace(":5432/", ":6543/") if ":5432/" in RAW_DB else RAW_DB

auditor = VanguardAuditor()
pool = None

async def init_db():
    global pool
    try:
        db_string = DB_URL + "?sslmode=require" if "sslmode" not in DB_URL else DB_URL
        pool = await asyncpg.create_pool(db_string, statement_cache_size=0)
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vanguard_audits (
                    id SERIAL PRIMARY KEY,
                    telegram_id TEXT,
                    target TEXT,
                    type TEXT,
                    score INT,
                    fix_price INT,
                    status TEXT,
                    created_at BIGINT
                )
            """)
        print("✅ DB Synced")
    except Exception as e: print(f"⚠️ DB Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🛡 **VANGUARD MULTI-CHAIN AUDITOR V100**\n\n"
        "Send me any of the following to scan:\n"
        "🌐 **Website URL** (http://...)\n"
        "💠 **Ethereum Address** (0x...)\n"
        "🟣 **Solana Address** (Base58)\n"
        "🟠 **Bitcoin Address** (bc1...)\n\n"
        "I will calculate the risk and generate a PDF Report."
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def handle_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()
    if len(target) < 5: return
    
    msg = await update.message.reply_text("🛰 **Initializing Omni-Scan...**")
    
    try:
        # Run Auditor
        pdf_path, score, price, t_type = auditor.analyze_target(target)
        
        if not pdf_path or t_type == "INVALID":
            await msg.edit_text("❌ Scan Failed. Invalid Target Format.")
            return

        status = "CRITICAL VULNERABILITY" if score < 70 else "SECURE"

        # Log to Database (Updates Dashboard Immediately!)
        if pool:
            try:
                await pool.execute(
                    "INSERT INTO vanguard_audits (telegram_id, target, type, score, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    str(update.effective_user.id), target, t_type, score, price, status, int(time.time())
                )
            except Exception as e: print(e)

        report_msg = (
            f"🚨 **AUDIT COMPLETE: {t_type}**\n\n"
            f"🎯 **Target:** `{target[:15]}...`\n"
            f"⚠️ **Score:** {score}/100\n"
            f"💰 **Fix Quote:** ${price}\n\n"
            f"📄 *I have generated your professional PDF report.*"
        )
        
        await msg.delete()
        await update.message.reply_document(document=open(pdf_path, 'rb'), caption=report_msg, parse_mode=ParseMode.MARKDOWN)

        # POST TO CHANNEL (Marketing the Fear)
        if CHANNEL_ID:
            try:
                alert = (
                    f"🚨 **VANGUARD THREAT DETECTED** 🚨\n\n"
                    f"**Network:** {t_type}\n"
                    f"**Target:** `{target[:15]}...`\n"
                    f"**Risk Score:** {score}/100 (FAIL)\n\n"
                    f"🛡 *Scan your projects to ensure safety: @VanguardSecurity_bot*"
                )
                await context.bot.send_document(chat_id=CHANNEL_ID, document=open(pdf_path, 'rb'), caption=alert, parse_mode=ParseMode.MARKDOWN)
            except Exception as e: 
                # Tell admin if channel post fails
                if ADMIN_ID: await context.bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ Could not post to channel. Make sure Bot is Admin in {CHANNEL_ID}.")

        os.remove(pdf_path) # Cleanup

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(init_db())
    except: pass
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_target))
    
    print("🚀 VANGUARD V100 LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
