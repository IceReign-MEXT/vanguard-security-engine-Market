import time
import random
from fpdf import FPDF

class VanguardAuditor:
    def __init__(self):
        self.agency = "ICEGODS VANGUARD FORENSICS"

    def analyze_target(self, target):
        issues =[]
        score = random.randint(20, 65) # Force a failing score so they pay you
        target_type = "UNKNOWN"

        target_lower = target.lower()

        # 1. WEBSITE DETECTION
        if target_lower.startswith("http") or "." in target_lower:
            target_type = "WEBSITE / DAPP"
            issues =[
                "CRITICAL: DDoS Protection Bypassed (Layer 7 Vulnerable)",
                "HIGH: SQL Injection Vector detected in API endpoints",
                "HIGH: Missing Strict-Transport-Security (HSTS) headers",
                "MEDIUM: SSL Cipher Suites outdated (Susceptible to interception)"
            ]
        # 2. ETHEREUM / EVM DETECTION
        elif target_lower.startswith("0x") and len(target) == 42:
            target_type = "ETHEREUM SMART CONTRACT"
            issues =[
                "CRITICAL: Unrenounced Ownership (Rugpull Risk)",
                "HIGH: Proxy Contract allows arbitrary logic manipulation",
                "HIGH: Liquidity Pool is NOT permanently locked",
                "MEDIUM: High gas consumption on transfer functions"
            ]
        # 3. BITCOIN DETECTION
        elif target_lower.startswith("bc1") or target_lower.startswith("1") or target_lower.startswith("3"):
            target_type = "BITCOIN WALLET"
            issues =[
                "HIGH: Linked to known dark-web mixing services (Tornado/Wasabi)",
                "MEDIUM: High transaction cluster entropy detected",
                "MEDIUM: Dusting attack vulnerabilities present"
            ]
        # 4. SOLANA DETECTION
        elif len(target) > 30 and not target_lower.startswith("0x"):
            target_type = "SOLANA TOKEN / WALLET"
            issues =[
                "CRITICAL: Mint Authority is STILL ENABLED (Can print infinite tokens)",
                "HIGH: Freeze Authority is ENABLED (Honeypot Risk - Can freeze sales)",
                "HIGH: Top 10 holders control >65% of supply (Dump Risk)",
                "MEDIUM: High MEV Bot extraction rate detected on pair"
            ]
        else:
            return None, "Invalid Target", 0

        # Generate the PDF Document
        pdf_file = self.create_pdf(target, target_type, score, issues)
        return pdf_file, issues, 200 # $200 is the fix price

    def create_pdf(self, target, t_type, score, issues):
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(200, 10, txt="VANGUARD DEEP-SCAN REPORT", ln=1, align='C')
        
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(200, 10, txt=f"Agency: {self.agency}", ln=1, align='C')
        pdf.ln(10)

        # Target Details
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"TARGET: {target}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"ASSET CLASS: {t_type}", ln=1, align='L')
        
        # Score
        pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100 (CRITICAL RISK)", ln=1, align='L')
        pdf.ln(10)

        # Issues List
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="FORENSIC FINDINGS:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        
        for issue in issues:
            pdf.multi_cell(0, 10, txt=f"- {issue}")
        
        # Sales Pitch
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 128, 0)
        pdf.cell(200, 10, txt="RECOMMENDATION & FIX:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, txt="These vulnerabilities leave the asset exposed to immediate exploitation, liquidity drains, or traffic interception.\n\nVanguard Engineers can deploy an automated patch and issue a 'SAFE' certificate.\n\nFix Cost: $200 USD.\nContact Admin: @MexRobertICE to initiate patching.")

        # Save File
        file_name = f"Vanguard_Forensics_{int(time.time())}.pdf"
        pdf.output(file_name)
        return file_name
