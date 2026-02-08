import os
import time
import requests
import socket
import ssl
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- AUDIT ENGINE ---
def analyze_site(url):
    if not url.startswith("http"):
        url = "https://" + url

    domain = urlparse(url).netloc
    report = {
        "url": url,
        "domain": domain,
        "score": 100,
        "issues": [],
        "speed": 0,
        "ssl": False,
        "seo": False
    }

    # 1. SPEED TEST
    start_time = time.time()
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        report['speed'] = round(time.time() - start_time, 2)

        if report['speed'] > 2.5:
            report['score'] -= 30
            report['issues'].append(f"⚠️ Critical Speed Issue: Load time is {report['speed']}s (Google wants < 2.5s).")

        if r.status_code != 200:
            report['score'] -= 50
            report['issues'].append(f"❌ Server Error: Returning Status Code {r.status_code}.")

        # 2. SEO CHECK
        soup = BeautifulSoup(r.text, 'html.parser')
        if not soup.title or not soup.title.string:
            report['score'] -= 10
            report['issues'].append("⚠️ SEO Missing: No Page Title found.")
        else:
            report['seo'] = True

        desc = soup.find("meta", attrs={"name": "description"})
        if not desc:
            report['score'] -= 10
            report['issues'].append("⚠️ SEO Missing: No Meta Description (Invisible to Google).")

    except Exception as e:
        report['score'] = 0
        report['issues'].append("💀 FATAL: Website is down or blocking scanners.")
        return report

    # 3. SSL SECURITY CHECK
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                report['ssl'] = True
    except:
        report['score'] -= 40
        report['issues'].append("❌ SECURITY RISK: SSL Certificate is invalid or missing.")

    # 4. GENERATE SALES PITCH
    report['pitch'] = f"""
    SUBJECT: Urgent issue with {domain}

    Hello, I was visiting {domain} and noticed it took {report['speed']} seconds to load. 
    Google penalizes sites slower than 2.5s.

    Also detected:
    - {len(report['issues'])} Technical Errors

    I can fix these performance issues for a flat fee of $100.
    Let me know if you want to save your traffic.
    """

    return report

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"error": "No URL provided"})

    result = analyze_site(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
