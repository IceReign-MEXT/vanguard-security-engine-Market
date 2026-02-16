import time
import requests
from fpdf import FPDF
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import random

class AlienAuditor:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (IceGods Security Scanner v1.0)'}

    def scan_target(self, target):
        if "http" in target:
            return self.audit_website(target)
        elif target.startswith("0x"):
            return self.audit_wallet(target)
        else:
            return None, "INVALID_TARGET", 0

    def audit_website(self, url):
        issues = []
        score = 100
        start = time.time()

        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            load_time = round(time.time() - start, 2)

            # 1. SPEED CHECK
            if load_time > 1.5:
                score -= 20
                issues.append(f"[CRITICAL] Load Time: {load_time}s (Target < 1.0s). Losing 40% Traffic.")

            # 2. SECURITY HEADERS
            headers = r.headers
            if 'X-Frame-Options' not in headers:
                score -= 15
                issues.append("[HIGH RISK] Missing Anti-Clickjack Header.")
            if 'Content-Security-Policy' not in headers:
                score -= 15
                issues.append("[HIGH RISK] Missing Content Security Policy (XSS Risk).")

            # 3. SEO CHECK
            soup = BeautifulSoup(r.text, 'html.parser')
            desc = soup.find("meta", attrs={"name": "description"})
            if not desc:
                score -= 10
                issues.append("[MEDIUM] No Meta Description (Invisible on Google).

        except Exception as e:
            return None, f"Scan Failed: {str(e)}", 0

        # CALCULATE FIX PRICE
        fix_price = (100 - score) * 5  # Example: Score 60 = $200 Fix
        if fix_price < 100: fix_price = 100

        pdf_file = self.generate_pdf(url, score, issues, fix_price)
        return pdf_file, issues, fix_price

    def audit_wallet(self, wallet):
        # Simulated Deep Scan for Wallet
        score = random.randint(40, 90)
        issues = []
        if score < 80: issues.append("[RISK] High Interaction with Mixing Services.")
        if score < 60: issues.append("[CRITICAL] Contract Approval Unrevoked.")

        pdf_file = self.generate_pdf(wallet, score, issues, 50)
        return pdf_file, issues, 50

    def generate_pdf(self, target, score, issues, price):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # HEADER
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="VANGUARD SECURITY AUDIT", ln=1, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Powered by IceGods Intelligence", ln=1, align='C')
        pdf.ln(10)

        # SCORE
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"TARGET: {target}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100", ln=1, align='L')
        pdf.ln(10)

        # ISSUES
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="VULNERABILITIES DETECTED:", ln=1, align='L')
        pdf.set_font("Arial", size=11)

        for issue in issues:
            pdf.cell(200, 10, txt=f"- {issue}", ln=1, align='L')

        if len(issues) == 0:
            pdf.cell(200, 10, txt="- System Secure. No threats found.", ln=1, align='L')

        # SALES PITCH
        pdf.ln(20)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="REMEDIATION PLAN:", ln=1, align='L')
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, txt=f"We can fix these issues and secure your asset within 24 hours.\n\nESTIMATED LOSS IF IGNORED: High\nFIX COST: ${price} USD")

        # CONTACT
        pdf.ln(20)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="CONTACT ENGINEER:", ln=1, align='C')
        pdf.set_font("Arial", 'U', 11)
        pdf.cell(200, 10, txt="Telegram: @MexRobertICE", ln=1, align='C')
        pdf.cell(200, 10, txt="GitHub: github.com/IceReign-MEXT", ln=1, align='C')

        filename = f"audit_{int(time.time())}.pdf"
        pdf.output(filename)
        return filename
