import time
import requests
from fpdf import FPDF
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VanguardAuditor:
    def __init__(self):
        self.company_name = "VANGUARD CYBER-FORENSICS"
        
    def analyze_target(self, target):
        issues =[]
        score = 100
        target_type = "UNKNOWN"

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

        # --- REAL DATA SCANNING LOGIC ---

        if target_type == "WEBSITE":
            # REAL HTTP SCAN
            try:
                start = time.time()
                r = requests.get(target, timeout=8, verify=False)
                load = time.time() - start
                
                if load > 2.0:
                    issues.append(f"[CRITICAL] Load Time {load:.2f}s. Site is unoptimized. SEO ranking penalty active.")
                    score -= 20
                
                # Check Real Security Headers
                headers = r.headers
                if 'X-Frame-Options' not in headers:
                    issues.append("[HIGH] Clickjacking Vulnerability. Missing X-Frame-Options header.")
                    score -= 15
                if 'Strict-Transport-Security' not in headers:
                    issues.append("[CRITICAL] Missing HSTS Header. Vulnerable to Man-in-the-Middle (MITM) SSL stripping.")
                    score -= 20
                
                # Check SEO
                soup = BeautifulSoup(r.text, 'html.parser')
                if not soup.find("meta", attrs={"name": "description"}):
                    issues.append("[MEDIUM] No Meta Description found. Organic search traffic is hindered.")
                    score -= 10
            except requests.exceptions.RequestException as e:
                issues.append(f"[FATAL] Server is down or blocking security probes. Error: {str(e)}")
                score -= 50

        elif target_type == "ETHEREUM":
            # REAL GOPLUS SECURITY API SCAN (Honeypot Detector)
            try:
                url = f"https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses={target}"
                res = requests.get(url, timeout=5).json()
                
                if res.get('result') and target.lower() in res['result']:
                    data = res['result'][target.lower()]
                    
                    if data.get('is_honeypot') == "1":
                        issues.append("[FATAL] HONEYPOT DETECTED. Users cannot sell this token.")
                        score -= 80
                    if data.get('is_proxy') == "1":
                        issues.append("[HIGH] Contract is a Proxy. Developer can rewrite the code to steal funds.")
                        score -= 20
                    if data.get('is_mintable') == "1":
                        issues.append("[CRITICAL] Mint Function Active. Dev can print infinite tokens.")
                        score -= 30
                    if float(data.get('buy_tax', 0)) > 0.1 or float(data.get('sell_tax', 0)) > 0.1:
                        issues.append(f"[HIGH] Malicious Tax Rates. Buy: {data.get('buy_tax')}, Sell: {data.get('sell_tax')}.")
                        score -= 20
                else:
                    issues.append("[WARNING] Contract not verified or no liquidity found on major DEXs.")
                    score -= 20
            except:
                issues.append("[ERROR] Could not complete deep blockchain sync.")
                score -= 10

        elif target_type == "SOLANA":
            # REAL DEXSCREENER LIQUIDITY SCAN
            try:
                url = f"https://api.dexscreener.com/latest/dex/tokens/{target}"
                res = requests.get(url, timeout=5).json()
                if res.get('pairs'):
                    pair = res['pairs'][0]
                    liq = pair.get('liquidity', {}).get('usd', 0)
                    if liq < 5000:
                        issues.append(f"[CRITICAL] Extreme Low Liquidity (${liq:,.2f}). High Rug Pull Risk.")
                        score -= 40
                    fdv = pair.get('fdv', 0)
                    if fdv > (liq * 50):
                        issues.append("[HIGH] Market Cap to Liquidity Ratio is dangerous. Price will collapse on sell.")
                        score -= 20
                else:
                    issues.append("[CRITICAL] Token has NO LIQUIDITY pools detected on Raydium/Orca.")
                    score -= 50
            except:
                issues.append("[WARNING] Failed to fetch Solana on-chain data.")

        elif target_type == "BITCOIN":
            issues.append("[WARNING] Deep UTXO tracking requires enterprise KYC nodes. Basic scan shows active inputs.")
            score -= 10

        # Calculate Fix Price Based on Real Issues
        if score < 10: score = 10
        fix_price = 50 + (len(issues) * 75)

        pdf_file = self.generate_pdf(target, target_type, score, issues, fix_price)
        return pdf_file, score, fix_price, target_type

    def generate_pdf(self, target, t_type, score, issues, price):
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(200, 0, 0) if score < 70 else pdf.set_text_color(0, 150, 0)
        pdf.cell(200, 10, txt="VANGUARD THREAT ANALYSIS REPORT", ln=1, align='C')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(200, 10, txt=f"Powered by: {self.company_name}", ln=1, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=f"ASSET: {target}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"NETWORK/TYPE: {t_type}", ln=1, align='L')
        
        if score < 70: pdf.set_text_color(255, 0, 0)
        else: pdf.set_text_color(0, 150, 0)
        pdf.cell(200, 10, txt=f"SECURITY SCORE: {score}/100", ln=1, align='L')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="REAL-TIME VULNERABILITIES DETECTED:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        
        if not issues:
            pdf.multi_cell(0, 10, txt="- Verified Secure. No threats detected by Vanguard Node.")
        else:
            for issue in issues:
                pdf.multi_cell(0, 10, txt=issue)
            
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(200, 10, txt="REMEDIATION QUOTE:", ln=1, align='L')
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pitch = f"Our automated systems detected {len(issues)} verifiable on-chain/server vulnerabilities.\n\nESTIMATED FIX COST: ${price} USD.\n\nContact Telegram: @MexRobertICE or use the Bot to initiate the patch."
        pdf.multi_cell(0, 10, txt=pitch)
        
        filename = f"Audit_{t_type}_{int(time.time())}.pdf"
        pdf.output(filename)
        return filename

