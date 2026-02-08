import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DB_URL = os.getenv("DATABASE_URL")

@app.route("/")
def dashboard():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Get Stats
        cur.execute("SELECT COUNT(*) FROM vanguard_logs;")
        total_scans = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM vanguard_logs WHERE status LIKE '%CRITICAL%';")
        threats = cur.fetchone()[0]

        # Get Recent Scans
        cur.execute("SELECT target, issues, fix_price, status FROM vanguard_logs ORDER BY created_at DESC LIMIT 10;")
        scans = cur.fetchall()

        cur.close()
        conn.close()

        return render_template("index.html", scans=scans, total=total_scans, threats=threats)
    except:
        return "Dashboard Loading... (Database Connecting)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
