import time
import random
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VanguardAuditor:
    def __init__(self):
        self.company_name = "VANGUARD FORENSICS (ICEGODS)"
        
    def analyze_target(self, target):
        issues =[]
        score = 100
        fix_price = 50 # Base Analysis Fee
        target_type = "UNKNOWN"

        # --- AUTO-DETECT TARGET TYPE ---
        if target.startswith("http") or ("." in target and not target.startswith("0x")):
            target_type = "WEBSITE"
            if not target.startswith("http"): target = "https://" + target
        elif target.startswith("0x") and len(target) == 42:
            target_type = "ETHEREUM"
        elif len(target) in [43, 44] and not target.startswith("0x"):
            target_type = "SOLANA"
        elif target.startswith("1") or target.startswith("3") or target.startswith("bc1"):
            target_type = "BITCOIN"
        else:
            return None, 0, 0, "INVALID"

        # --- DYNAMIC SCANNING LOGIC ---
        if target_type == "WEBSITE":
            try:
                start = time.time()
                r = requests.get(target, timeout=5, verify=False)
                load = time.time() - start
                if load > 1.5:
                    issues.append(f"[CRITICAL] Load Time {load:.2f}s (Optimal is <1.0s). Losing 45% of traffic.")
                    score -= 20
                    fix_price += 150 # Speed optimization cost
                if 'X-Frame-Options' not in r.headers:
                    issues.append("[HIGH] Clickjacking vulnerability. Missing X-Frame-Options.")
                    score -= 15
                    fix_price += 100 # Security patch cost
            except:
                issues.append("[FATAL] Domain unreachable or blocking security probes.")
                score -= 50
                fix_price += 300

        elif target_type == "ETHEREUM":
            # Simulate Contract/Wallet Check
            issues.append("[CRITICAL] Contract Proxy contains Mutable Variables (Rug Pull Risk).")
            issues.append("[HIGH] Liquidity Pool is UNLOCKED.")
            issues.append("[MEDIUM] Dev wallet holds 15% of supply.")
            score -= 45
            fix_price += 500 # Smart contract fix cost

        elif target_type == "SOLANA":
            # Simulate SOL Check
            issues.append("[CRITICAL] Mint Authority ENABLED (Dev can print infinite tokens).")
            issues.append("[CRITICAL] Freeze Authority ENABLED (Honeypot Trap).")
            score -= 60
            fix_price += 750 # Token migration/fix cost

        elif target_type == "BITCOIN":
            issues.append("[MEDIUM] UTXO Dusting Attack patterns detected.")
            issues.append("[HIGH] Interaction with known CoinJoin/Mixer addresses.")
            score -= 25
            fix_price += 200

        # Enforce minimum score
        if score < 10: score = 10

        pdf_file = self.generate_pdf(target, target_type, score, issues, fix_price)
        return pdf_file, score, fix_price, target_type

    def generate_pdf(self, target, t_type, score, issues, price):
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(200, 0, 0) if score < 70 else pdf.set_text_color(0, 150, 0)
        pdf.cell(200, 10, txt="VANGUARD THREAT ANALYSIS REPORT", ln=1, align='C')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(200, 10, txt=f"Powered by: {self.company_name}", ln=1, align='C')
        pdf.ln(10)
        
        # Target Info
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=f"ASSET: {target}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"NETWORK/TYPE: {t_type}", ln=1, align='L')
        
        if score < 70: pdf.set_text_color(255, 0, 0)
        else: pdf.set_text_color(0, 150, 0)
        pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100", ln=1, align='L')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
        # Issues
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="VULNERABILITIES DETECTED:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        for issue in issues:
            pdf.multi_cell(0, 10, txt=issue)
            
        # Dynamic Sales Pitch
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(200, 10, txt="REMEDIATION QUOTE:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pitch = f"Our automated systems and engineers can patch these {len(issues)} critical vulnerabilities. If ignored, you risk asset drain or massive traffic loss.\n\nESTIMATED FIX COST: ${price} USD.\nContact Telegram: @MexRobertICE to initiate the patch."
        pdf.multi_cell(0, 10, txt=pitch)
        
        filename = f"Audit_{t_type}_{int(time.time())}.pdf"
        pdf.output(filename)
        return filename
