# 🛡️ VANGUARD SECURITY ENGINE

**Automated Cyber-Security & Blockchain Forensics Terminal.**

Vanguard is an institutional-grade auditing system designed to detect vulnerabilities in Web2 infrastructure (Websites) and Web3 assets (Wallets). It functions as an automated consultant, generating professional PDF reports and instant price quotes for remediation.

---

## ⚡ SYSTEM CAPABILITIES

### 🌐 Web2 Security Audit
*   **Latency Analysis:** Detects server lag and speed bottlenecks (>2.0s threshold).
*   **Header Inspection:** Scans for missing security headers (X-Frame-Options, SSL).
*   **SEO Forensics:** Checks meta-data health and visibility.
*   **Output:** Generates a client-ready PDF Audit Certificate.

### ⛓️ Web3 Wallet Forensics
*   **Deep Scan:** Connects to Ethereum Mainnet via RPC.
*   **Activity Logging:** Analyzes transaction count and ETH balance.
*   **Bot Detection:** Flags high-frequency wallets vs dormant addresses.

### 🧠 Ecosystem Integration
*   **Dashboard Sync:** Pushes scan results to the **IceGods Command Center**.
*   **Channel Broadcast:** Auto-posts "Vulnerability Alerts" to public channels.
*   **Admin Quoting:** Calculates repair costs and sends private quotes to the Admin.

---

## 🛠 TECH STACK

*   **Core:** Python 3.11
*   **Framework:** Flask (Keep-Alive) + python-telegram-bot
*   **Blockchain:** Web3.py + Alchemy/Infura RPC
*   **Database:** Supabase (PostgreSQL)
*   **Reporting:** FPDF (PDF Generation)
*   **Scraping:** BeautifulSoup4 (HTML Analysis)

---

## 🚀 DEPLOYMENT GUIDE

1.  **Clone Repository**
2.  **Set Environment Variables** (See `.env.example`)
3.  **Deploy to Render** (Python 3 Runtime)
4.  **Start Command:** `python main.py & gunicorn app:app --bind 0.0.0.0:$PORT`

---

## 🔒 SECURITY PROTOCOLS

This software is designed for **Ethical Auditing** and **Lead Generation**.
All reports are generated locally and logged securely to the IceGods Database.

---

### 📡 CONNECT
*   **Telegram Channel:** [ICEGODSICEDEVILS](https://t.me/ICEGODSICEDEVILS)
*   **Live Dashboard:** [IceGods Terminal](https://icegods-dashboard-56aj.onrender.com)
*   **Developer:** IceReign Systems

*(C) 2026 IceReign Systems. All Rights Reserved.*
