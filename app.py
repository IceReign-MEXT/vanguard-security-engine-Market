from flask import Flask, jsonify, request
import os
import requests
from dotenv import load_dotenv

# Load environment variables for local testing
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
# These are pulled from Render Environment Variables for security
PANEL_API_KEY = os.getenv('PANEL_API_KEY')
PANEL_URL = "https://morethanpanel.com/api/v2"
ADMIN_ID = os.getenv('ADMIN_ID', '7033049440') # Your ID

class MarketEngine:
    @staticmethod
    def get_balance():
        """Connects to MoreThanPanel to check current SMM funds."""
        if not PANEL_API_KEY:
            return {"error": "API Key missing in environment"}

        payload = {
            'key': PANEL_API_KEY,
            'action': 'balance'
        }
        try:
            response = requests.post(PANEL_URL, data=payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def check_order_status(order_id):
        """Checks the status of a specific SMM order."""
        payload = {
            'key': PANEL_API_KEY,
            'action': 'status',
            'order': order_id
        }
        try:
            response = requests.post(PANEL_URL, data=payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# --- ROUTES ---

@app.route('/')
def home():
    """Main landing endpoint for the Vanguard Engine."""
    return jsonify({
        "status": "Online",
        "engine": "Vanguard Market Engine",
        "version": "2.0.5",
        "branding": "IceGods Systems",
        "message": "Alien Core Operational"
    })

@app.route('/api/status')
def status():
    """Endpoint to check SMM balance and system health."""
    balance_info = MarketEngine.get_balance()
    return jsonify({
        "system_health": "Good",
        "market_connection": "Active",
        "data": balance_info
    })

@app.route('/api/order/<int:order_id>')
def order_info(order_id):
    """Endpoint to track specific order progress."""
    status_info = MarketEngine.check_order_status(order_id)
    return jsonify(status_info)

# --- ERROR HANDLING ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == "__main__":
    # Render sets the PORT environment variable automatically
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
