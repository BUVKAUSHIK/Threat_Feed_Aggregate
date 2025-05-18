from flask import Flask, render_template
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    # --- URLHaus Feed ---
    urlhaus_url = "https://urlhaus-api.abuse.ch/v1/urls/recent/"
    urlhaus_iocs = []
    try:
        # Required parameters for URLHaus API
        params = {
            "recent": "true"  # Get recent URLs
        }
        
        print("[URLHaus] Sending request to:", urlhaus_url)
        print("[URLHaus] With params:", params)
        
        response = requests.get(urlhaus_url, params=params)
        print("[URLHaus] Status code:", response.status_code)
        
        if response.status_code == 200:
            data = response.json()
            print("[URLHaus] Response keys:", data.keys())
            print("[URLHaus] Sample entry:", data.get("urls", [])[0] if data.get("urls") else "No URLs in response")
            urlhaus_iocs = data.get("urls", [])[:20]
            print("[URLHaus] Full JSON:", data)
        else:
            print("[URLHaus] Failed to fetch. Check endpoint.")
    except Exception as e:
        print("[URLHaus] Exception:", e)

    # --- AbuseIPDB Feed ---
    ABUSE_API_KEY = os.getenv('ABUSE_API_KEY')
    abuse_url = "https://api.abuseipdb.com/api/v2/blacklist"
    abuse_iocs = []

    if not ABUSE_API_KEY:
        print("[AbuseIPDB] ERROR: API key is missing. Please check .env or environment variables.")
    else:
        abuse_headers = {
            "Accept": "application/json",
            "Key": ABUSE_API_KEY
        }
        try:
            response = requests.get(abuse_url, headers=abuse_headers)
            print("[AbuseIPDB] Status code:", response.status_code)
            if response.status_code == 200:
                data = response.json()
                print("[AbuseIPDB] Response keys:", data.keys())
                print("[AbuseIPDB] Sample entry:", data.get("data", [])[0] if data.get("data") else "No IPs in response")
                abuse_iocs = data.get("data", [])[:20]
            elif response.status_code == 429:
                print("[AbuseIPDB] Rate limit exceeded. Please wait before making more requests.")
                # Optionally, show a message in your template
                abuse_iocs = []
            else:
                print("[AbuseIPDB] Failed to fetch. Status:", response.status_code)
        except Exception as e:
            print("[AbuseIPDB] Exception:", e)

    return render_template("index.html", urls=urlhaus_iocs, ips=abuse_iocs)

if __name__ == '__main__':
    app.run(debug=True)
