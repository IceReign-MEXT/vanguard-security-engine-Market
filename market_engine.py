import requests
import os

class MarketEngine:
    def __init__(self):
        self.api_key = os.getenv('PANEL_API_KEY')
        self.url = "https://morethanpanel.com/api/v2"

    def get_balance(self):
        """Checks the current SMM balance to ensure we can fulfill orders"""
        payload = {'key': self.api_key, 'action': 'balance'}
        try:
            r = requests.post(self.url, data=payload)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def place_order(self, service_id, link, quantity):
        """Automatically triggers a purchase on MoreThanPanel"""
        payload = {
            'key': self.api_key,
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        }
        r = requests.post(self.url, data=payload)
        return r.json()
