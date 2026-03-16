import time
import random
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VanguardAuditor:
    def __init__(self):
        self.company_name = "VANGUARD CYBER-SECURITY"
        
    def analyze_target(self, target):
        if not target.startswith("http"):
            target = "https://" + target
            
        issues =[]
        score = 100
        start = time.time()
        
        try:
            r = requests.get(target, timeout=10, verify=False)
            load_time = round(time.time() - start, 2)
            
            # 1. Speed Check
            if load_time > 1.5:
                score -= 20
                issues.append(f"[CRITICAL] Load Time: {load_time}s (Standard < 1s). Losing traffic.")
            
            # 2. Header Check
            headers = r.headers
            if 'X-Frame-Options' not in headers:
                score -= 15
                issues.append("[HIGH RISK] Missing X-Frame-Options (Clickjacking Vulnerability).")
            if 'Content-Security-Policy' not in headers:
                score -= 15
                issues.append("[HIGH RISK] Missing Content-Security-Policy (XSS Risk).")
                
            # 3. SEO Check
            soup = BeautifulSoup(r.text, 'html.parser')
            if not soup.find("meta", attrs={"name": "description"}):
                score -= 10
                issues.append("[MEDIUM] No Meta Description. Poor Search Engine Visibility.")
                
        except Exception as e:
            return None, 0, 0
            
        if len(issues) == 0:
            issues.append("System appears secure. Standard protections active.")
            
        # Calculate Fix Price
        fix_price = (100 - score) * 5
        if fix_price < 100: fix_price = 150
        
        pdf_file = self.generate_pdf(target, score, issues, fix_price)
        return pdf_file, score, fix_price

    def generate_pdf(self, target, score, issues, price):
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(200, 10, txt="CONFIDENTIAL SECURITY AUDIT", ln=1, align='C')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(200, 10, txt=f"Authorized by: {self.company_name}", ln=1, align='C')
        pdf.ln(10)
        
        # Target Info
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=f"TARGET: {target}", ln=1, align='L')
        
        if score < 60: pdf.set_text_color(255, 0, 0)
        else: pdf.set_text_color(0, 150, 0)
        pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100", ln=1, align='L')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
        # Issues
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="DETECTED VULNERABILITIES:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        
        for issue in issues:
            pdf.multi_cell(0, 10, txt=issue)
            
        # Sales Pitch
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(200, 10, txt="REMEDIATION PLAN:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pitch = f"Vanguard Engineers can patch these vulnerabilities within 24 hours.\n\nEstimated Fix Cost: ${price} USD.\nContact @MexRobertICE on Telegram to secure this asset."
        pdf.multi_cell(0, 10, txt=pitch)
        
        filename = f"Vanguard_Audit_{int(time.time())}.pdf"
        pdf.output(filename)
        return filename
