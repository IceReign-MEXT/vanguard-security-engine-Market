import os
import time
import asyncio
import asyncpg
import psycopg2
import threading
from dotenv import load_dotenv
from flask import Flask, render_template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from auditor import VanguardAuditor

# --- CONFIGURATION ---
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
ADMIN_ID = os.getenv("TELEGRAM_CHAT_ID")
RAW_DB = os.getenv("DATABASE_URL", "")
# Force correct port and SSL for Supabase connection
DB_URL = RAW_DB.replace(":5432/", ":6543/") if ":5432/" in RAW_DB else RAW_DB
if "sslmode" not in DB_URL: DB_URL += "?sslmode=require"

auditor = VanguardAuditor()

# --- FLASK DASHBOARD (WEB) ---
app = Flask(__name__)

def get_dashboard_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        # 1. Total Scans
        cur.execute("SELECT COUNT(*) FROM vanguard_audits;")
        total = cur.fetchone()[0]
        # 2. Threats (Score < 80)
        cur.execute("SELECT COUNT(*) FROM vanguard_audits WHERE score < 80;")
        threats = cur.fetchone()[0]
        # 3. Live Logs
        cur.execute("SELECT target, score, fix_price, status FROM vanguard_audits ORDER BY created_at DESC LIMIT 10;")
        logs = cur.fetchall()
        cur.close()
        conn.close()
        return total, threats, logs
    except Exception as e:
        print(f"Web DB Error: {e}")
        return 0, 0,[]

@app.route('/')
def dashboard():
    total, threats, logs = get_dashboard_data()
    return render_template('index.html', total_scans=total, threats=threats, logs=logs)

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- DATABASE SETUP (BOT) ---
pool = None
async def init_db():
    global pool
    try:
        pool = await asyncpg.create_pool(DB_URL, statement_cache_size=0)
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vanguard_audits (
                    id SERIAL PRIMARY KEY,
                    telegram_id TEXT,
                    target TEXT,
                    score INT,
                    fix_price INT,
                    status TEXT,
                    created_at BIGINT
                )
            """)
        print("✅ DB Synced")
    except Exception as e: print(f"⚠️ DB Error: {e}")

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🛡 **VANGUARD SECURITY ENGINE**\n\n"
        "Institutional-grade Web Forensics.\n\n"
        "👇 **Paste a Website URL (e.g., website.com) to begin your free audit:**"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def scan_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()
    if len(target) < 4 or "." not in target: return
    
    msg = await update.message.reply_text("🛰 **Analyzing server headers & load speeds...**")
    
    try:
        # Run Auditor
        pdf_path, score, price = auditor.analyze_target(target)
        
        if not pdf_path:
            await msg.edit_text("❌ Scan Failed. Site unreachable.")
            return

        status = "CRITICAL VULNERABILITY" if score < 70 else "SECURE"

        # Log to Database (Updates Dashboard Immediately!)
        if pool:
            try:
                await pool.execute(
                    "INSERT INTO vanguard_audits (telegram_id, target, score, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5, $6)",
                    str(update.effective_user.id), target, score, price, status, int(time.time())
                )
            except Exception as e: print(e)

        # Reply to User
        report_msg = (
            f"🚨 **AUDIT COMPLETE**\n\n"
            f"🎯 **Target:** `{target}`\n"
            f"⚠️ **Score:** {score}/100\n\n"
            f"📄 *I have generated your professional PDF report.*"
        )
        
        kb = [[InlineKeyboardButton("🛠 Request Fix Quote", callback_data=f"fix_{price}")]]
        
        await msg.delete()
        await update.message.reply_document(
            document=open(pdf_path, 'rb'),
            caption=report_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(kb)
        )

        # Alert Channel
        if CHANNEL_ID:
            try:
                alert = f"🚨 **THREAT DETECTED**\n\nTarget: `{target}`\nScore: {score}/100\n\n*Vanguard Security Scan.*"
                await context.bot.send_message(CHANNEL_ID, alert, parse_mode=ParseMode.MARKDOWN)
            except: pass
            
        os.remove(pdf_path) # Cleanup

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("fix_"):
        price = query.data.split("_")[1]
        await query.message.reply_text(
            f"👨‍💻 **ENGINEER DISPATCHED**\n\n"
            f"Our team can patch these vulnerabilities for **${price} USD**.\n"
            f"Please contact Head Engineer @MexRobertICE to proceed."
        )

# --- MAIN ---
def main():
    # 1. Start Dashboard Server
    threading.Thread(target=run_web, daemon=True).start()
    
    # 2. Start Telegram Bot
    app = Application.builder().token(BOT_TOKEN).build()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(init_db())
    except: pass
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_target))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 VANGUARD V5.0 LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
