import os
import re

# Safely find the file, no matter where we run from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIG_PATH = os.path.join(BASE_DIR, "data", "malicious_signatures.txt")

class WadeEngine:
    def __init__(self):
        self.signatures = set()
        self.load_signatures()

    def load_signatures(self):
        print(f"[*] Loading signatures from: {SIG_PATH}")
        try:
            if not os.path.exists(SIG_PATH):
                print(f"[!] WARNING: Signature file not found at {SIG_PATH}. Using empty DB.")
                return

            # Open with 'ignore' to prevent crashes from bad characters
            with open(SIG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    sig = line.strip().lower()
                    if sig and len(sig) > 3:
                        self.signatures.add(sig)
            
            print(f"[+] Successfully loaded {len(self.signatures)} signatures.")
        except Exception as e:
            print(f"[!] ERROR loading signatures: {e}")

    def check_url_safety(self, url):
        url_lower = url.lower()
        
        # 1. Check Signatures
        for sig in self.signatures:
            if sig in url_lower:
                return {
                    "status": "DANGEROUS",
                    "risk_score": 100,
                    "reason": f"Signature Match: '{sig}' detected in URL."
                }
        
        # 2. Heuristic Checks (Extensions)
        suspicious_exts = ['.exe', '.bat', '.sh', '.vbs', '.scr', '.com', '.apk']
        for ext in suspicious_exts:
            if url_lower.endswith(ext):
                return {
                    "status": "DANGEROUS",
                    "risk_score": 90,
                    "reason": f"High-Risk File Extension ({ext})"
                }

        return {"status": "SAFE", "risk_score": 0, "reason": "No local threats found."}

# Create a global instance
engine = WadeEngine()

# Helper function for app.py
def check_url_safety(url):
    return engine.check_url_safety(url)