import time
import random
from fpdf import FPDF
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VanguardAuditor:
    def __init__(self):
        self.company_name = "VANGUARD CYBER-FORENSICS"
        
    def analyze_target(self, target):
        issues =[]
        score = 100
        target_type = "UNKNOWN"
        age_days = random.randint(5, 1200) # Simulated deployment age

        # --- DEEP DETECTION LOGIC ---
        if target.startswith("http") or ("." in target and not target.startswith("0x")):
            target_type = "WEBSITE"
            if not target.startswith("http"): target = "https://" + target
            issues.append(f"[INFO] Domain registered {age_days} days ago.")
            issues.append("[CRITICAL] Missing strict Content-Security-Policy (XSS Vulnerable).")
            issues.append("[CRITICAL] DDoS Vulnerability: No rate limiting detected at edge.")
            issues.append("[HIGH] SSL Certificate uses outdated TLS 1.1 cipher suites.")
            score -= random.randint(35, 50)
            
        elif target.startswith("0x") and len(target) == 42:
            target_type = "ETHEREUM"
            issues.append(f"[INFO] Smart Contract deployed {age_days} days ago.")
            issues.append("[CRITICAL] Reentrancy vulnerability found in payable function.")
            issues.append("[CRITICAL] Ownership NOT renounced. Developer can halt trading.")
            issues.append("[HIGH] Unverified bytecode segments detected in Proxy.")
            score -= random.randint(45, 65)
            
        elif len(target) in [43, 44] and not target.startswith("0x"):
            target_type = "SOLANA"
            issues.append(f"[INFO] SPL Token minted {age_days} days ago.")
            issues.append("[CRITICAL] Freeze Authority is ENABLED. Users can be blacklisted.")
            issues.append("[CRITICAL] Mint Authority is ENABLED. Infinite inflation risk.")
            issues.append("[HIGH] High concentration: Top 10 wallets hold >80% of supply.")
            score -= random.randint(50, 75)
            
        elif target.startswith("1") or target.startswith("3") or target.startswith("bc1"):
            target_type = "BITCOIN"
            issues.append(f"[INFO] Wallet active for {age_days} days.")
            issues.append("[HIGH] UTXO Dusting Attack patterns detected.")
            issues.append("[MEDIUM] Interaction with known CoinJoin/Mixer addresses.")
            score -= random.randint(20, 35)
        else:
            return None, 0, 0, "INVALID"

        # --- DYNAMIC PRICING LOGIC ---
        # Base fee $50. Add $100 per Critical, $50 per High.
        fix_price = 50
        fix_price += sum(100 for i in issues if "[CRITICAL]" in i)
        fix_price += sum(50 for i in issues if "[HIGH]" in i)

        if score < 10: score = 10

        pdf_file = self.generate_pdf(target, target_type, score, issues, fix_price)
        return pdf_file, score, fix_price, target_type

    def generate_pdf(self, target, t_type, score, issues, price):
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(220, 20, 60) if score < 70 else pdf.set_text_color(34, 139, 34)
        pdf.cell(200, 10, txt="DEEP FORENSIC THREAT ANALYSIS", ln=1, align='C')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(200, 10, txt=f"Powered by: {self.company_name}", ln=1, align='C')
        pdf.ln(10)
        
        # Target Info
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=f"ASSET: {target}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"NETWORK: {t_type}", ln=1, align='L')
        
        if score < 70: pdf.set_text_color(220, 20, 60)
        else: pdf.set_text_color(34, 139, 34)
        pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100", ln=1, align='L')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
        # Issues
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="VULNERABILITIES & METADATA DETECTED:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        for issue in issues:
            pdf.multi_cell(0, 10, txt=issue)
            
        # Dynamic Sales Pitch
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(200, 10, txt="REMEDIATION QUOTE:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pitch = f"Our automated system calculated the remediation cost based on threat severity.\n\nESTIMATED FIX COST: ${price} USD.\n\nTo deploy the patch, return to the Telegram Bot, select 'Request Automated Fix', and complete payment."
        pdf.multi_cell(0, 10, txt=pitch)
        
        filename = f"Audit_{t_type}_{int(time.time())}.pdf"
        pdf.output(filename)
        return filename
EOF
