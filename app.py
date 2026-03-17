import os
import psycopg2
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

RAW_DB = os.getenv("DATABASE_URL", "")
DB_URL = RAW_DB.replace(":5432/", ":6543/") if ":5432/" in RAW_DB else RAW_DB

def get_db_data():
    if not DB_URL: return 0, 0, 0,[]
    try:
        conn = psycopg2.connect(DB_URL + "?sslmode=require" if "sslmode" not in DB_URL else DB_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM vanguard_audits;")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM vanguard_audits WHERE score < 70;")
        threats = cur.fetchone()[0]
        
        cur.execute("SELECT SUM(fix_price) FROM vanguard_audits;")
        rev = cur.fetchone()[0] or 0
        
        cur.execute("SELECT target, type, score, fix_price, status FROM vanguard_audits ORDER BY created_at DESC LIMIT 15;")
        logs = cur.fetchall()
        
        cur.close()
        conn.close()
        return total, threats, rev, logs 
    except Exception as e:
        print(f"DB Error: {e}")
        return 0, 0, 0,[]

@app.route('/')
def dashboard():
    total, threats, rev, logs = get_db_data()
    return render_template('index.html', total_scans=total, threats=threats, revenue=rev, logs=logs)
