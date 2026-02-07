import os
import requests
from bs4 import BeautifulSoup
from web3 import Web3
from dotenv import load_dotenv

# Load your secret Vault
load_dotenv()

class VanguardWeapon:
    def __init__(self, target):
        self.target = target
        self.eth_price = self.get_eth_price()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID")

    def get_eth_price(self):
        """Fetches live price using your CoinGecko Key"""
        cg_key = os.getenv("COINGECKO_API_KEY")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&x_cg_demo_api_key={cg_key}"
        try:
            r = requests.get(url).json()
            return float(r['ethereum']['usd'])
        except:
            return 2500.0 # Fallback

    def send_alert(self, report):
        """Sends the Casualty Report to your Telegram Channel"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.channel_id, "text": report, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload)
            print("[+] Telegram Alert Dispatched!")
        except Exception as e:
            print(f"[-] Alert Failed: {e}")

    def scan_web(self):
        print(f"[*] Scanning Web URL: {self.target}")
        try:
            r = requests.get(self.target, timeout=10)
            issues = []
            if not self.target.startswith("https"):
                issues.append("- INSECURE CONNECTION (No HTTPS)")
            if 'X-Frame-Options' not in r.headers:
                issues.append("- CLICKJACKING RISK (Missing Headers)")

            if issues:
                msg = f"🛡️ *WEB VULNERABILITY DETECTED*\n\n*Target:* {self.target}\n*Issues Found:*\n" + "\n".join(issues)
                self.send_alert(msg)
        except Exception as e:
            print(f"[-] Web Scan Error: {e}")

    def scan_contract(self):
        print(f"[*] Scanning Contract: {self.target}")
        # Failover System: Alchemy -> Infura
        providers = [os.getenv("RPC_URL"), os.getenv("INFURA_URL")]
        w3 = None
        for p in providers:
            temp_w3 = Web3(Web3.HTTPProvider(p))
            if temp_w3.is_connected():
                w3 = temp_w3
                break

        if w3:
            balance_wei = w3.eth.get_balance(self.target)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            casualty_usd = float(balance_eth) * self.eth_price

            if balance_eth > 0:
                report = (
                    f"🚨 *CRITICAL CASUALTY DETECTED*\n\n"
                    f"*Contract:* `{self.target}`\n"
                    f"*Balance:* {balance_eth:.4f} ETH\n"
                    f"*USD AT RISK:* `${casualty_usd:,.2f}`\n\n"
                    f"⚡ *Status:* Ready for Remediation."
                )
                self.send_alert(report)
                return balance_eth
        return 0

if __name__ == "__main__":
    print("--- VANGUARD SECURITY LABS SYSTEM ---")
    target_input = input("Enter Target (URL or 0x Address): ").strip()
    weapon = VanguardWeapon(target_input)

    if target_input.startswith("0x"):
        weapon.scan_contract()
    else:
        if not target_input.startswith("http"):
            target_input = "http://" + target_input
            weapon.target = target_input
        weapon.scan_web()

