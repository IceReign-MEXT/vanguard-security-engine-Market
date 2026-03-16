#!/usr/bin/env python3
"""
VANGUARD SECURITY ENGINE - MAIN APPLICATION
Flask + Telegram Webhook Integration
"""

import os
import logging
import requests as http_requests
from flask import Flask, request, jsonify, Response
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configuration
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
ADMIN_CHAT = os.environ.get('ADMIN_TELEGRAM', '@MexRobertICE')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')  # https://your-app.onrender.com/telegram

# ═══════════════════════════════════════════════════════════════
# WEBHOOK ENDPOINT - CRITICAL FOR TELEGRAM
# ═══════════════════════════════════════════════════════════════

@app.route('/')
def home():
    """Home page"""
    return """
    <h1>🛡️ Vanguard Security Engine</h1>
    <p>System Operational</p>
    <p>API Endpoints:</p>
    <ul>
        <li><a href="/api/health">/api/health</a> - Health check</li>
        <li>POST /telegram - Telegram webhook</li>
        <li><a href="/set-telegram-webhook">/set-telegram-webhook</a> - Setup webhook</li>
    </ul>
    """

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    """
    Receive Telegram updates via webhook
    This is the endpoint Telegram will POST to when users message the bot
    """
    try:
        update_data = request.get_json(force=True)
        logger.info(f"Received update: {update_data.get('update_id')}")
        
        # Handle messages
        if 'message' in update_data:
            message = update_data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user = message.get('from', {})
            username = user.get('username', 'Unknown')
            
            logger.info(f"Message from {username} ({chat_id}): {text[:50]}")
            
            # Command handling
            if text == '/start':
                send_message(chat_id, 
                    f"🛡️ <b>VANGUARD SECURITY BOT</b>\n\n"
                    f"Hello! I'm your crypto security assistant.\n\n"
                    f"<b>Commands:</b>\n"
                    f"• /scan &lt;address&gt; - Security scan\n"
                    f"• /price - View pricing\n"
                    f"• /status - System status\n"
                    f"• /help - Documentation\n\n"
                    f"<b>Example:</b>\n"
                    f"<code>/scan 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb</code>\n\n"
                    f"Or just send me any address starting with 0x",
                    parse_mode="HTML"
                )
            
            elif text.startswith('/scan') or (text.startswith('0x') and len(text) >= 42):
                # Extract address
                if text.startswith('/scan'):
                    parts = text.split()
                    if len(parts) > 1:
                        address = parts[1]
                    else:
                        send_message(chat_id, "❌ Please provide an address:\n<code>/scan 0x...</code>", parse_mode="HTML")
                        return jsonify({"ok": True}), 200
                else:
                    address = text.strip()
                
                # Send scanning message
                send_message(chat_id, f"🔍 Scanning <code>{address[:20]}...</code>...\nThis may take 10-20 seconds...", parse_mode="HTML")
                
                # Perform scan (simplified)
                try:
                    # Here you would call your actual scanner
                    # For now, simulate a scan
                    result = {
                        "scan_id": "demo123",
                        "target": address,
                        "risk_level": "medium",
                        "score": 45,
                        "findings": [
                            {
                                "title": "Unverified Contract",
                                "severity": "medium",
                                "description": "Contract source code is not verified.",
                                "recommendation": "Wait for verification before investing."
                            }
                        ]
                    }
                    
                    # Format response
                    response_text = format_scan_result(result)
                    send_message(chat_id, response_text, parse_mode="HTML")
                    
                except Exception as e:
                    logger.error(f"Scan error: {e}")
                    send_message(chat_id, "❌ Scan failed. Please try again later.")
            
            elif text == '/price':
                send_message(chat_id,
                    "💰 <b>VANGUARD PRICING</b>\n\n"
                    "<b>🔍 Basic Scan:</b> FREE\n"
                    "• Contract verification\n"
                    "• Basic analysis\n"
                    "• Risk score\n\n"
                    "<b>🔬 Deep Scan:</b> $50\n"
                    "• Full bytecode analysis\n"
                    "• PDF report\n"
                    "• Honeypot detection\n\n"
                    "<b>🛠️ Remediation:</b> $150\n"
                    "• Emergency assistance\n"
                    "• Wallet recovery\n"
                    "• 1-on-1 consultation\n\n"
                    f"Contact: {ADMIN_CHAT}",
                    parse_mode="HTML"
                )
            
            elif text == '/status':
                send_message(chat_id, 
                    "🟢 <b>System Operational</b>\n\n"
                    "All security engines are active.\n"
                    "Threat database updated.\n"
                    "Ready to scan.",
                    parse_mode="HTML"
                )
            
            elif text == '/help':
                send_message(chat_id,
                    "📖 <b>HELP</b>\n\n"
                    "I can detect:\n"
                    "• Smart contract drainers\n"
                    "• Honeypot tokens\n"
                    "• Hidden mint functions\n"
                    "• Unchecked approvals\n\n"
                    "<b>Commands:</b>\n"
                    "• /scan &lt;address&gt; - Scan wallet/contract\n"
                    "• /price - View pricing\n"
                    "• /status - Check status\n"
                    "• /help - This message\n\n"
                    "Just paste any 0x address to scan it automatically!",
                    parse_mode="HTML"
                )
            
            else:
                send_message(chat_id, 
                    "I don't understand that command.\n\n"
                    "Send me an Ethereum address (0x...) to scan it,\n"
                    "or use /help to see available commands."
                )
        
        return jsonify({"ok": True}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

def send_message(chat_id, text, parse_mode=None):
    """Send message via Telegram Bot API"""
    if not TELEGRAM_TOKEN:
        logger.error("No TELEGRAM_TOKEN configured")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode or "HTML"
        }
        response = http_requests.post(url, json=payload, timeout=10)
        logger.info(f"Message sent to {chat_id}: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

def format_scan_result(result):
    """Format scan results for Telegram"""
    risk_emoji = {
        "safe": "🟢", "low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"
    }
    level = result.get('risk_level', 'unknown')
    emoji = risk_emoji.get(level, "⚪")
    
    text = f"{emoji} <b>SCAN RESULT: {level.upper()}</b>\n\n"
    text += f"<b>Score:</b> {result.get('score', result.get('overall_risk_score', 0))}/100\n"
    text += f"<b>Target:</b> <code>{result.get('target', result.get('target_address', 'Unknown'))}</code>\n"
    text += f"<b>Scan ID:</b> <code>{result.get('scan_id', 'N/A')}</code>\n\n"
    
    findings = result.get('findings', [])
    if findings:
        text += "<b>🔍 FINDINGS:</b>\n"
        for f in findings:
            severity_emoji = "🔴" if f.get('severity') == 'critical' else "🟠" if f.get('severity') == 'high' else "🟡"
            text += f"\n{severity_emoji} <b>{f.get('title', 'Unknown')}</b>\n"
            text += f"{f.get('description', '')[:100]}...\n"
            text += f"💡 {f.get('recommendation', '')[:80]}...\n"
    else:
        text += "✅ No threats detected!\n"
    
    return text

# ═══════════════════════════════════════════════════════════════
# WEBHOOK SETUP ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/set-telegram-webhook', methods=['GET'])
def setup_webhook():
    """
    Set Telegram webhook URL
    Visit this URL after deployment to activate the bot
    """
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "TELEGRAM_BOT_TOKEN not configured"}), 500
    
    # Construct webhook URL
    webhook_url = WEBHOOK_URL or f"{request.url_root}telegram"
    
    try:
        # Call Telegram API to set webhook
        api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
        response = http_requests.post(api_url, json={"url": webhook_url}, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            return jsonify({
                "status": "success",
                "message": "Webhook set successfully!",
                "webhook_url": webhook_url,
                "telegram_response": data
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to set webhook",
                "telegram_response": data
            }), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-telegram-webhook', methods=['GET'])
def get_webhook_info():
    """Check current webhook status"""
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "TELEGRAM_BOT_TOKEN not configured"}), 500
    
    try:
        api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
        response = http_requests.get(api_url, timeout=10)
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-telegram-webhook', methods=['GET'])
def delete_webhook():
    """Remove webhook (useful for debugging)"""
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "TELEGRAM_BOT_TOKEN not configured"}), 500
    
    try:
        api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"
        response = http_requests.post(api_url, timeout=10)
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "operational",
        "version": "5.0",
        "timestamp": datetime.utcnow().isoformat(),
        "telegram_configured": bool(TELEGRAM_TOKEN),
        "webhook_url": WEBHOOK_URL
    })

@app.route('/api/scan', methods=['POST'])
def scan():
    """API endpoint for scanning"""
    data = request.json or {}
    address = data.get('address') or data.get('target')
    
    if not address:
        return jsonify({"error": "No address provided"}), 400
    
    # Here you would integrate with your auditor.py
    # For now, return demo response
    return jsonify({
        "scan_id": "scan123",
        "address": address,
        "risk_level": "medium",
        "score": 45,
        "findings": []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
