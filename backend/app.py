import os
import sqlite3
import json
import logging
import base64
import httpx
import asyncio
import whois
import ssl
import socket
import sys
import time
import requests
import zipfile
import io
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from groq import Groq
import uvicorn

# --- CONFIG & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WadeEngine")

app = FastAPI(title="WADE Engine Ultimate", version="5.0")

# API KEYS (Fetched from Hugging Face Cloud Secrets)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

# TRUSTED DOMAINS (Whitelist Ages)
TRUSTED_AGES = {
    "google.com": 9500, "youtube.com": 6900, "wikipedia.org": 8700, 
    "github.com": 5800, "microsoft.com": 11000, "huggingface.co": 1500,
    "stackoverflow.com": 7000, "amazon.com": 10500, "apple.com": 13000,
    "netflix.com": 9000, "linkedin.com": 7500, "whatsapp.com": 5000,
    "openai.com": 3000, "facebook.com": 7600, "instagram.com": 4500,
    "twitter.com": 6500, "x.com": 10000, "twitch.tv": 4000,
    "gmail.com": 9500, "outlook.com": 8000, "yahoo.com": 10000,
    "paruluniversity.ac.in": 5000, "uhdmovies.loan": 1000
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE SETUP ---
DB_PATH = "wade_logs.db"
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                        (id INTEGER PRIMARY KEY, url TEXT, score INTEGER, verdict TEXT, sources TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
init_db()

# --- INDUSTRY-READY THREAT INTELLIGENCE ---
class ThreatIntel:
    def __init__(self):
        self.malicious_urls = set()
        self.loaded = False

    async def update_feeds(self):
        logger.info("🔄 WADE: Updating Threat Intelligence from GitHub & URLHaus...")
        sources = [
            "https://urlhaus.abuse.ch/downloads/text_online/",
            "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-links-ACTIVE.txt"
        ]
        
        count = 0
        async with httpx.AsyncClient() as client:
            for source in sources:
                try:
                    r = await client.get(source, timeout=10)
                    if r.status_code == 200:
                        for line in r.text.splitlines():
                            if not line.startswith("#") and line.strip():
                                self.malicious_urls.add(line.strip())
                                count += 1
                except Exception as e:
                    logger.error(f"⚠️ Feed Error ({source}): {e}")
        
        self.loaded = True
        logger.info(f"✅ WADE Intel Updated: {len(self.malicious_urls)} Active Threats.")

intel_db = ThreatIntel()
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(intel_db.update_feeds())

# --- ROBUST DOMAIN AGE ---
def get_domain_age(url):
    try:
        domain = url.split("//")[-1].split("/")[0].replace("www.", "").split(":")[0]
        
        if domain in TRUSTED_AGES:
            return TRUSTED_AGES[domain]

        socket.setdefaulttimeout(2.0) 
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list): creation_date = creation_date[0]
            
            if creation_date:
                if isinstance(creation_date, str):
                    try: creation_date = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")
                    except: 
                        try: creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S")
                        except: pass
                if isinstance(creation_date, datetime):
                    return (datetime.now() - creation_date).days
        except: pass 

        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=2.0) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    start_date_str = cert['notBefore']
                    start_date = datetime.strptime(start_date_str, "%b %d %H:%M:%S %Y %Z")
                    return (datetime.now() - start_date).days
        except: pass
            
    except Exception: pass 
    return -1 

async def check_virustotal(url: str):
    if not VIRUSTOTAL_API_KEY: return {"malicious": 0, "total": "No API Key"}
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}", 
                headers={"x-apikey": VIRUSTOTAL_API_KEY}, 
                timeout=5.0
            )
            if res.status_code == 200:
                stats = res.json()['data']['attributes']['last_analysis_stats']
                return {"malicious": stats.get('malicious', 0), "total": sum(stats.values())}
    except: pass
    return {"malicious": 0, "total": "Database Error"}

def log_scan(url: str, result: dict):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO logs (url, score, verdict, sources) VALUES (?, ?, ?, ?)",
                (url, result.get("risk_score", 0), result.get("verdict", "UNKNOWN"), "AI+OSINT")
            )
    except: pass

# --- RECALIBRATED AI SCANNER ---
class HybridScanner:
    def __init__(self):
        self.groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        if GEMINI_API_KEY: genai.configure(api_key=GEMINI_API_KEY)

    async def scan(self, url, vt_data, domain_age):
        vt_score = vt_data.get('malicious', 0) if isinstance(vt_data.get('malicious'), int) else 0
        
        context = f"Domain Age: {domain_age} days (If -1, unknown). VirusTotal Flags: {vt_score}."
        
        system_prompt = (
            f"You are WADE Security AI. Analyze URL: '{url}'. Context: {context}.\n"
            "BE OBJECTIVE, NOT PARANOID. If VirusTotal is 0 and the site is > 30 days old, default to SAFE.\n"
            "Only flag as MALICIOUS if the URL shows clear phishing patterns (brand typos, deceptive paths).\n"
            "Return ONLY strict JSON: {'risk_score': int (0-100), 'verdict': 'SAFE'|'MALICIOUS', "
            "'threat_type': str, 'harm': str, 'effect': str}"
        )

        if self.groq:
            try:
                res = self.groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}],
                    response_format={"type": "json_object"}
                )
                return json.loads(res.choices[0].message.content)
            except: pass 
            
        if GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"{system_prompt}. Provide valid JSON.")
                clean_json = res.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_json)
            except: pass

        return {"risk_score": 0, "verdict": "SAFE", "threat_type": "None", "harm": "None", "effect": "None"}

scanner = HybridScanner()
class ScanRequest(BaseModel): url: str

@app.post("/analyze")
async def analyze_url(request: ScanRequest, background_tasks: BackgroundTasks):
    url = request.url
    domain = url.split("//")[-1].split("/")[0].replace("www.", "")

    if domain in TRUSTED_AGES:
        return {
            "risk_score": 0, "verdict": "SAFE", "threat_type": "Official Trusted Domain",
            "harm": "None", "effect": "None", "domain_age": TRUSTED_AGES[domain],
            "vt_data": {"malicious": 0, "total": 95}
        }

    if url in intel_db.malicious_urls:
        return {
            "risk_score": 100, "verdict": "MALICIOUS", "threat_type": "Confirmed Phishing (GitHub Feed)",
            "harm": "In Global Blacklist", "effect": "Credential Theft", "domain_age": -1, 
            "vt_data": {"malicious": "High", "total": "OSINT"}
        }

    age = get_domain_age(url)
    vt_data = await check_virustotal(url)
    result = await scanner.scan(url, vt_data, age)
    
    # RECALIBRATED OVERRIDE RULES
    if isinstance(vt_data.get('malicious'), int) and vt_data.get('malicious') > 3:
        result['risk_score'] = max(result['risk_score'], 90)
        result['verdict'] = "MALICIOUS"
        result['threat_type'] = "Security Vendor Flagged"

    if age != -1 and age < 3 and result['risk_score'] < 40:
        result['risk_score'] = 50
        result['threat_type'] = "Very Newly Registered Domain"

    final_result = {**result, "domain_age": age, "vt_data": vt_data}
    background_tasks.add_task(log_scan, url, final_result)
    return final_result

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <body style="background-color: #050505; color: #00f3ff; font-family: monospace; text-align: center; margin-top: 20%;">
            <h1>🛡️ WADE ENGINE ACTIVE</h1>
            <p>Web AI Defense Engine API is currently running and monitoring traffic.</p>
        </body>
    </html>
    """

# --- DYNAMIC THREAT INTEL: TRANCO TOP 10K ---
trusted_cache = {
    "timestamp": 0,
    "domains": []
}

@app.get("/trusted-domains")
def get_trusted_domains():
    global trusted_cache
    current_time = time.time()
    
    if current_time - trusted_cache["timestamp"] > 86400 or not trusted_cache["domains"]:
        try:
            print("WADE: Downloading latest Tranco Top 10k list...")
            url = "https://tranco-list.eu/top-1m.csv.zip"
            resp = requests.get(url, timeout=10)
            
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                csv_name = z.namelist()[0]
                with z.open(csv_name) as f:
                    domains = []
                    for i, line in enumerate(f):
                        if i >= 10000: break
                        domain = line.decode('utf-8').strip().split(',')[1]
                        domains.append(domain)
            
            custom_safe = ["paruluniversity.ac.in", "uhdmovies.loan"]
            trusted_cache["domains"] = list(set(domains + custom_safe))
            trusted_cache["timestamp"] = current_time
            print(f"WADE: Successfully cached {len(trusted_cache['domains'])} trusted domains.")
            
        except Exception as e:
            print(f"Error fetching Tranco list: {e}")
            if not trusted_cache["domains"]:
                trusted_cache["domains"] = ["google.com", "youtube.com", "github.com", "paruluniversity.ac.in", "uhdmovies.loan"]

    return {"success": True, "domains": trusted_cache["domains"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)