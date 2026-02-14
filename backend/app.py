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

app = FastAPI(title="Wade Engine Ultimate", version="6.0.0")

# API KEYS
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

# TRUSTED DOMAINS (Whitelist)
TRUSTED_AGES = {
    "google.com": 9500, "youtube.com": 6900, "wikipedia.org": 8700, 
    "github.com": 5800, "microsoft.com": 11000, "huggingface.co": 1500,
    "stackoverflow.com": 7000, "amazon.com": 10500, "apple.com": 13000,
    "netflix.com": 9000, "linkedin.com": 7500, "whatsapp.com": 5000,
    "openai.com": 3000, "facebook.com": 7600, "instagram.com": 4500,
    "twitter.com": 6500, "x.com": 10000, "twitch.tv": 4000,
    "gmail.com": 9500, "outlook.com": 8000, "yahoo.com": 10000
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

# --- ROBUST DOMAIN AGE (With Timeout Fix) ---
def get_domain_age(url):
    try:
        domain = url.split("//")[-1].split("/")[0].replace("www.", "").split(":")[0]
        
        # 1. Check Whitelist (Fastest)
        if domain in TRUSTED_AGES:
            return TRUSTED_AGES[domain]

        # 2. Try WHOIS with Timeout
        # FIX: Added specific timeout to prevent hanging
        socket.setdefaulttimeout(2.0) 
        
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            
            if isinstance(creation_date, list): 
                creation_date = creation_date[0]
            
            if creation_date:
                if isinstance(creation_date, str):
                    # Try parsing common string formats
                    try: creation_date = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")
                    except: 
                        try: creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S")
                        except: pass
                
                if isinstance(creation_date, datetime):
                    return (datetime.now() - creation_date).days
        except:
            pass 

        # 3. Fallback: SSL Certificate Date
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=2.0) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    start_date_str = cert['notBefore']
                    start_date = datetime.strptime(start_date_str, "%b %d %H:%M:%S %Y %Z")
                    return (datetime.now() - start_date).days
        except:
            pass
            
    except Exception:
        pass 
        
    return -1 # Truly Unknown

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

class HybridScanner:
    def __init__(self):
        self.groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        if GEMINI_API_KEY: genai.configure(api_key=GEMINI_API_KEY)

    async def scan(self, url, vt_data, domain_age):
        vt_score = vt_data.get('malicious', 0) if isinstance(vt_data.get('malicious'), int) else 0
        
        # PROMPT ENGINEERING: Added "Strict JSON" instruction to fix parsing errors
        context = f"Domain Age: {domain_age} days (If -1, unknown). VirusTotal Flags: {vt_score}."
        
        system_prompt = (
            f"You are WADE Security AI. Analyze URL: '{url}'. Context: {context}.\n"
            "Evaluate phishing risk. If VirusTotal > 0 or Age < 30 days, high risk.\n"
            "Return ONLY JSON: {'risk_score': int (0-100), 'verdict': 'SAFE'|'MALICIOUS', "
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

        # Fallback if AI fails
        return {"risk_score": 0, "verdict": "SAFE", "threat_type": "None", "harm": "None", "effect": "None"}

scanner = HybridScanner()

class ScanRequest(BaseModel):
    url: str

@app.post("/analyze")
async def analyze_url(request: ScanRequest, background_tasks: BackgroundTasks):
    url = request.url
    domain = url.split("//")[-1].split("/")[0].replace("www.", "")

    # 1. WHITELIST CHECK
    if domain in TRUSTED_AGES:
        return {
            "risk_score": 0, "verdict": "SAFE", "threat_type": "Official Trusted Domain",
            "harm": "None", "effect": "None",
            "domain_age": TRUSTED_AGES[domain],
            "vt_data": {"malicious": 0, "total": 95}
        }

    # 2. THREAT INTEL CHECK (Blacklists)
    if url in intel_db.malicious_urls:
        return {
            "risk_score": 100, "verdict": "MALICIOUS", "threat_type": "Confirmed Phishing (GitHub Feed)",
            "harm": "In Global Blacklist", "effect": "Credential Theft",
            "domain_age": -1, "vt_data": {"malicious": "High", "total": "OSINT"}
        }

    # 3. DEEP CLOUD SCAN
    age = get_domain_age(url)
    vt_data = await check_virustotal(url)
    
    # 4. AI SCAN
    result = await scanner.scan(url, vt_data, age)
    
    # 5. OVERRIDE RULES (The "Brutal" Logic)
    # If VirusTotal says it's bad, it IS bad, regardless of what AI says.
    if isinstance(vt_data.get('malicious'), int) and vt_data.get('malicious') > 2:
        result['risk_score'] = max(result['risk_score'], 90)
        result['verdict'] = "MALICIOUS"
        result['threat_type'] = "Security Vendor Flagged"

    # If domain is extremely new (< 7 days), flag it as suspicious
    if age != -1 and age < 7 and result['risk_score'] < 50:
        result['risk_score'] = 60
        result['threat_type'] = "Newly Registered Domain"

    final_result = {**result, "domain_age": age, "vt_data": vt_data}
    background_tasks.add_task(log_scan, url, final_result)
    return final_result

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<html><body><h1>WADE ONLINE v6.0</h1></body></html>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)