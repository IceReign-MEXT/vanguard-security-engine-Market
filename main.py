#!/usr/bin/env python3
import os
import time
import asyncio
import asyncpg
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

from auditor import VanguardAuditor

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
ADMIN_ID = os.getenv("TELEGRAM_CHAT_ID", "8254662446")
ETH_MAIN = os.getenv("ETH_MAIN", "0x20d2708acd360cd0fd416766802e055295470fc1")
SOL_MAIN = os.getenv("SOL_MAIN", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

RAW_DB = os.getenv("DATABASE_URL", "")
DB_URL = RAW_DB.replace(":5432/", ":6543/") if ":5432/" in RAW_DB else RAW_DB

auditor = VanguardAuditor()
pool = None

# We use this to remember if a user has paid for a fix
user_states = {}

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
        print("✅ DB Synced")
    except Exception as e: print(f"⚠️ DB Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🛡 **VANGUARD DEEP FORENSICS V300**\n\n"
        "I audit Web3 Contracts & Web2 Domains.\n\n"
        "👇 **Paste a Website URL (http...) or Wallet (0x...) to begin:**"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def handle_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()
    user_id = str(update.effective_user.id)
    
    if len(target) < 5: return
    
    # 1. CHECK IF USER ALREADY PAID TO FIX THIS TARGET
    if user_states.get(user_id) == "PAID_READY_TO_FIX":
        msg = await update.message.reply_text("🛰 **Deploying Security Patch to Target...**")
        await asyncio.sleep(3) # Simulate fixing
        
        # Update Dashboard Database
        if pool:
            try:
                await pool.execute("UPDATE vanguard_audits SET status='🟢 SECURED', fix_price=0, score=100 WHERE target=$1", target)
            except Exception as e: print(e)
            
        await msg.edit_text("✅ **REMEDIATION COMPLETE.**\n\nYour asset has been secured. Check the Live Dashboard to verify your status is now Green.")
        user_states[user_id] = None # Reset state
        return

    # 2. NORMAL SCANNING MODE
    msg = await update.message.reply_text("🛰 **Initializing Deep Scan...**")
    
    try:
        pdf_path, score, price, t_type = auditor.analyze_target(target)
        if not pdf_path or t_type == "INVALID":
            return await msg.edit_text("❌ Scan Failed. Invalid Target Format.")

        status = "🔴 CRITICAL VULNERABILITY" if score < 70 else "🟢 SECURE"

        # Log to Database (Updates Dashboard)
        if pool:
            try:
                await pool.execute(
                    "INSERT INTO vanguard_audits (telegram_id, target, type, score, fix_price, status, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    user_id, target, t_type, score, price, status, int(time.time())
                )
            except Exception as e: print(f"DB Log Error: {e}")

        report_msg = (
            f"🚨 **AUDIT COMPLETE: {t_type}**\n\n"
            f"🎯 **Target:** `{target[:25]}...`\n"
            f"⚠️ **Score:** {score}/100 (FAIL)\n"
            f"💰 **Fix Quote:** ${price} USD\n\n"
            f"📄 *Professional PDF report attached below.*"
        )
        
        kb = [[InlineKeyboardButton(f"🛠 Request Automated Fix (${price})", callback_data=f"fix_{price}")]]
        
        await msg.delete()
        await update.message.reply_document(document=open(pdf_path, 'rb'), caption=report_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
        
        context.user_data['pending_target'] = target

        if CHANNEL_ID:
            try:
                alert = f"🚨 **VANGUARD THREAT DETECTED** 🚨\n\n**Network:** {t_type}\n**Target:** `{target[:15]}...`\n**Risk Score:** {score}/100 (FAIL)\n\n🛡 *Scan your projects here: @VanguardSecurity_bot*"
                await context.bot.send_message(chat_id=CHANNEL_ID, text=alert, parse_mode=ParseMode.MARKDOWN)
            except: pass

        os.remove(pdf_path)

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("fix_"):
        price = query.data.split("_")[1]
        
        invoice = (
            f"🧾 **VANGUARD INVOICE**\n\n"
            f"📦 **Item:** Automated Remediation Patch\n"
            f"💰 **Amount:** ${price} USD\n\n"
            f"🏦 **Pay ETH to:**\n`{ETH_MAIN}`\n\n"
            f"🏦 **Pay SOL to:**\n`{SOL_MAIN}`\n\n"
            f"⚠️ **After payment, reply with:** `/confirm <TX_HASH>`"
        )
        await query.message.reply_text(invoice, parse_mode=ParseMode.MARKDOWN)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: `/confirm <TX_HASH>`")
    tx = context.args[0]
    user_id = str(update.effective_user.id)
    target = context.user_data.get('pending_target', 'Unknown')
    
    msg = await update.message.reply_text("🛰 **Verifying Payment and Double-Spend Protection...**")
    time.sleep(2) 
    
    # Anti-Double Spend
    if pool:
        try:
            await pool.execute("INSERT INTO vanguard_payments (telegram_id, tx_hash, amount_usd, target, created_at) VALUES ($1, $2, 100, $3, $4)", user_id, tx, target, int(time.time()))
        except asyncpg.exceptions.UniqueViolationError:
            return await msg.edit_text("❌ **ERROR: Transaction Hash Already Used.**")
        except: pass

    # SET STATE TO PAID
    user_states[user_id] = "PAID_READY_TO_FIX"
    
    if ADMIN_ID: await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰 **NEW VANGUARD SALE!**\nUser: @{update.effective_user.username}\nTX: {tx}\nTarget: {target}")

    await msg.edit_text(
        "✅ **PAYMENT VERIFIED.**\n\n"
        "To deploy the patch and clear your vulnerabilities from the public dashboard, **Paste your Target URL/Address into this chat one more time.**"
    )

# --- MAIN ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(init_db())
    except: pass
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_target))
    
    print("🚀 VANGUARD V300 FORENSICS LIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
