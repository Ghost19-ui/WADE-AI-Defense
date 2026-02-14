import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Using Llama 3.2 Vision or Gemini Flash
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def scan_url(url, scripts, screenshot_base64=None):
    if not GROQ_API_KEY:
        return {"risk_score": 0, "verdict": "Safe", "reason": "AI Key Missing"}

    # --- OPTION 3: CONTEXT-AWARE PROMPT ---
    system_prompt = """
    You are WADE, a Cyber Defense AI. Analyze the website context.
    
    LOOK FOR THESE RED FLAGS:
    1. BRAND MISMATCH: Does the screenshot show a logo (e.g., PayPal, Microsoft) but the URL is NOT the official domain?
    2. URGENCY TEXT: Does the text scream "Account Suspended", "Act Now", "24 Hours Left"?
    3. DATA THEFT: Are there forms asking for passwords/credit cards on a non-secure HTTP site?
    
    Return JSON: {"risk_score": 0-100, "verdict": "Safe"|"Phishing"|"Suspicious", "reason": "Short explanation"}
    """

    user_content = [
        {"type": "text", "text": f"Analyze this URL: {url}. Scripts found: {str(scripts)[:500]}"}
    ]

    # Add Screenshot if available (Computer Vision)
    if screenshot_base64:
        if "base64," in screenshot_base64:
            screenshot_base64 = screenshot_base64.split("base64,")[1]
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{screenshot_base64}"}
        })

    payload = {
        "model": "llama-3.2-11b-vision-preview", # Or gemini-1.5-flash
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        data = response.json()
        return json.loads(data['choices'][0]['message']['content'])
    except Exception as e:
        print(f"AI Error: {e}")
        return {"risk_score": 0, "verdict": "Unknown", "reason": "AI Analysis Failed"}