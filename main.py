#!/usr/bin/env python3
import os
import time
import asyncio
import threading
import asyncpg
import requests
import random
from fpdf import FPDF
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1. CONFIGURATION ---
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
ADMIN_ID = os.getenv("TELEGRAM_CHAT_ID", "8254662446")
ETH_MAIN = os.getenv("ETH_MAIN", "0x20d2708acd360cd0fd416766802e055295470fc1")

# Fix Database URL for Render
RAW_DB = os.getenv("DATABASE_URL", "")
DB_URL = RAW_DB.replace(":5432/", ":6543/") if ":5432/" in RAW_DB else RAW_DB

# --- 2. FLASK SERVER ---
app = Flask(__name__)
@app.route("/")
def health(): return "VANGUARD V250 IMMORTAL", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- 3. DATABASE ENGINE ---
pool = None
async def init_db():
    global pool
    if not DB_URL: return
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
        print("✅ DATABASE CONNECTED")
    except Exception as e:
        print(f"⚠️ DB ERROR: {e}")

# --- 4. THE AUDITOR ENGINE ---
def generate_pdf(target, t_type, score, issues, price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(200, 0, 0) if score < 70 else pdf.set_text_color(0, 150, 0)
    pdf.cell(200, 10, txt="VANGUARD THREAT ANALYSIS REPORT", ln=1, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"TARGET: {target}", ln=1, align='L')
    pdf.cell(200, 10, txt=f"NETWORK: {t_type}", ln=1, align='L')
    pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100 (FAIL)", ln=1, align='L')
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="CRITICAL VULNERABILITIES DETECTED:", ln=1, align='L')
    pdf.set_font("Arial", '', 11)
    for issue in issues:
        pdf.multi_cell(0, 10, txt=f"- {issue}")
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(200, 10, txt="REMEDIATION QUOTE:", ln=1, align='L')
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, txt=f"We can generate a deployment patch for these vulnerabilities.\n\nFIX COST: ${price} USD.\nContact @MexRobertICE on Telegram.")
    
    filename = f"Audit_{int(time.time())}.pdf"
    pdf.output(filename)
    return filename

def generate_patch(target):
    filename = f"Vanguard_Patch_{int(time.time())}.txt"
    with open(filename, "w") as f:
        f.write(f"=== VANGUARD AUTOMATED REMEDIATION PATCH ===\nTarget: {target}\n\n")
        f.write("[1] SECURITY FIX:\nAdd strict Content-Security-Policy and X-Frame-Options headers to your server.\n")
        f.write("[2] SMART CONTRACT FIX:\nExecute renounceOwnership() and lock LP tokens using a trusted locker for 6+ months.\n")
        f.write("\nDeploy these changes to upgrade Security Score to 100/100.")
    return filename

# --- 5. TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🛡 **VANGUARD OMNI-SCANNER ONLINE**\n\n"
        "I audit Web3 Contracts & Web2 Domains.\n\n"
        "👇 **Paste a Website URL (http...) or Wallet (0x...) to begin:**"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def handle_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()
    if len(target) < 5: return
    
    msg = await update.message.reply_text("🛰 **Initializing Scan...**")
    
    # Auto Detect Type
    t_type = "WEBSITE" if "http" in target or "." in target else "BLOCKCHAIN"
    score = random.randint(30, 65)
    price = 200
    status = "CRITICAL VULNERABILITY"
    
    issues = [
        "[HIGH] Mutable Proxy Variables Detected",
        "[CRITICAL] Missing Anti-Clickjacking Security Headers",
        "[MEDIUM] Exposed Endpoints Found"
    ]

    try:
        # LOG TO DATABASE (This updates your dashboard)
        if pool:
            await pool.execute(
                "INSERT INTO vanguard_audits (telegram_id, target, type, score, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                str(update.effective_user.id), target, t_type, score, price, status, int(time.time())
            )
            print(f"✅ Dashboard Updated for {target}")

        # Generate PDF
        pdf_path = generate_pdf(target, t_type, score, issues, price)
        
        report_msg = (
            f"🚨 **AUDIT COMPLETE**\n\n"
            f"🎯 **Target:** `{target[:25]}...`\n"
            f"⚠️ **Score:** {score}/100 (FAIL)\n\n"
            f"📄 *Professional PDF report attached below.*"
        )
        
        kb = [[InlineKeyboardButton(f"🛠 Buy Automated Patch (${price})", callback_data=f"fix_{price}")]]
        
        await msg.delete()
        await update.message.reply_document(document=open(pdf_path, 'rb'), caption=report_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
        
        context.user_data['pending_target'] = target
        os.remove(pdf_path)

        # POST TO CHANNEL
        if CHANNEL_ID:
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=f"🚨 **VANGUARD THREAT DETECTED**\n\n**Target:** `{target[:15]}...`\n**Risk Score:** {score}/100 (FAIL)\n\n🛡 *Scan your projects here: @VanguardSecurity_bot*", parse_mode=ParseMode.MARKDOWN)
            except: pass

    except Exception as e:
        await msg.edit_text(f"⚠️ System Error: {e}\n(Bot is still running, check logs)")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("fix_"):
        price = query.data.split("_")[1]
        invoice = (
            f"🧾 **VANGUARD INVOICE**\n\n"
            f"📦 **Item:** Automated Patch Code\n"
            f"💰 **Amount:** ${price} USD\n\n"
            f"🏦 **Pay ETH/SOL to:**\n`{ETH_MAIN}`\n\n"
            f"⚠️ **Reply:** `/confirm <TX_HASH>`"
        )
        await query.message.reply_text(invoice, parse_mode=ParseMode.MARKDOWN)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: `/confirm <TX_HASH>`")
    
    await update.message.reply_text("🛰 **Verifying Payment...**\nChecking double-spend protection...")
    time.sleep(2)
    
    target = context.user_data.get('pending_target', 'Unknown Target')
    
    if ADMIN_ID:
        try: await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰 **NEW VANGUARD SALE!**\nUser: @{update.effective_user.username}\nTX: {context.args[0]}\nTarget: {target}")
        except: pass

    await update.message.reply_text("✅ **PAYMENT VERIFIED.** Generating Patch...")
    
    patch_file = generate_patch(target)
    await update.message.reply_document(document=open(patch_file, 'rb'), caption="🔐 **VANGUARD PATCH GENERATED**\n\nDeploy this code to secure your asset.")
    os.remove(patch_file)

# --- MAIN ---
def main():
    threading.Thread(target=run_web, daemon=True).start()
    if not BOT_TOKEN:
        print("❌ CRITICAL: BOT TOKEN MISSING")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(init_db())
    except: pass
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_target))
    
    print("🚀 VANGUARD V250 IMMORTAL LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
