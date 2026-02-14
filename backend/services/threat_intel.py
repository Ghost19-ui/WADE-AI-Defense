import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()
VT_KEY = os.getenv("VIRUSTOTAL_API_KEY")

def check_virustotal(url):
    if not VT_KEY: return {"malicious": 0, "total": 0}
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        headers = {"x-apikey": VT_KEY}
        resp = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        
        if resp.status_code == 200:
            stats = resp.json()['data']['attributes']['last_analysis_stats']
            return {"malicious": stats['malicious'], "total": sum(stats.values())}
    except Exception as e:
        print(f"❌ Intel Error: {e}")
    return {"malicious": 0, "total": 0}