from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import concurrent.futures

# Import Services
from services.gemini_agent import scan_url as ai_scan
from services.threat_intel import check_virustotal
from services.forensics import get_domain_age
from services.db_manager import save_scan, is_whitelisted, add_whitelist, get_history

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: str
    scripts: Optional[str] = None
    screenshot: Optional[str] = None

class WhitelistRequest(BaseModel):
    url: str

@router.get("/history")
async def history_endpoint():
    return get_history()

@router.post("/whitelist")
async def whitelist_endpoint(req: WhitelistRequest):
    success = add_whitelist(req.url)
    return {"status": "success" if success else "error"}

@router.post("/analyze")
async def analyze_endpoint(request: AnalyzeRequest):
    try:
        # 1. Check Whitelist
        if is_whitelisted(request.url):
            return {
                "risk_score": 0, "verdict": "Safe", "reason": "Whitelisted Site",
                "intel_data": {"malicious": 0}, "domain_age": 9999
            }

        # 2. Parallel Scan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_ai = executor.submit(ai_scan, request.url, request.scripts, request.screenshot)
            future_intel = executor.submit(check_virustotal, request.url)
            future_age = executor.submit(get_domain_age, request.url)
            
            ai_result = future_ai.result()
            intel_data = future_intel.result()
            age_data = future_age.result()

        final_score = ai_result.get("risk_score", 0)
        final_verdict = ai_result.get("verdict", "Safe")
        final_reason = ai_result.get("reason", "Analysis Complete")
        days_old = age_data.get("age_days", -1)

        # 3. Apply Rules
        if days_old > 0 and days_old < 30:
            final_score = max(final_score, 75)
            final_reason += f" (New Domain: {days_old} days old)"

        if intel_data.get("malicious", 0) > 0:
            final_score = 100
            final_verdict = "Phishing"
            final_reason = f"Flagged by {intel_data['malicious']} security vendors."

        # 4. Save & Return
        save_scan(request.url, final_score, final_verdict)

        return {
            "risk_score": final_score,
            "verdict": final_verdict,
            "reason": final_reason,
            "intel_data": intel_data,
            "domain_age": days_old
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"risk_score": 0, "verdict": "Error", "reason": str(e)}