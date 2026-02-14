import requests
import os

# --- CONFIGURATION ---
# We use a User-Agent to prevent GitHub from blocking the request (404/403 errors)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

SOURCES = {
    # 1. Massive XSS List (PayloadBox)
    "XSS_Basic": "https://raw.githubusercontent.com/payloadbox/xss-payload-list/master/Intruder/xss-payload-list.txt",
    
    # 2. SQL Injection List (PayloadBox)
    "SQLi_Short": "https://raw.githubusercontent.com/payloadbox/sql-injection-payload-list/master/Intruder/detect/sqli.txt",
    
    # 3. Open Redirects (PayloadBox)
    "Open_Redirect": "https://raw.githubusercontent.com/payloadbox/open-redirect-payload-list/master/Intruder/open-redirect-payload-list.txt",
    
    # 4. LFI - Local File Inclusion (PayloadBox)
    "LFI_Basic": "https://raw.githubusercontent.com/payloadbox/rfi-lfi-payload-list/master/Intruder/LFI-RFI-Payload-list.txt"
}

# Determine correct output path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir.endswith("backend"):
    OUTPUT_FILE = os.path.join(current_dir, "data", "malicious_signatures.txt")
else:
    OUTPUT_FILE = os.path.join("backend", "data", "malicious_signatures.txt")

def update_database():
    print("🚀 CONTACTING SECURITY REPOSITORIES (Spoofing Browser)...")
    new_signatures = set()

    for name, url in SOURCES.items():
        try:
            print(f"   ⬇️  Downloading {name}...")
            # We add HEADERS here to trick GitHub
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                lines = response.text.splitlines()
                count = 0
                for line in lines:
                    clean = line.strip().lower()
                    if clean and len(clean) > 4: 
                        new_signatures.add(clean)
                        count += 1
                print(f"       ✅ Success! Got {count} signatures.")
            else:
                print(f"   ⚠️  Failed {name} (Status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Add Critical Defaults
    defaults = [
        "<script>", "javascript:", "eval(", "union select", "/etc/passwd", "alert(1)",
        "eicar.com", "eicar-standard-antivirus-test-file", "content-disposition:", 
        "cmd.exe", "/bin/sh", "wget ", "curl ", "powershell"
    ]
    for d in defaults:
        new_signatures.add(d)

    # Save
    print(f"💾 SAVING TO {OUTPUT_FILE}...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for sig in sorted(new_signatures):
            f.write(sig + "\n")

    print(f"\n✅ DATABASE UPDATED: {len(new_signatures)} signatures ready.")
    print("👉 NOW: Upload the 'backend/data' folder to Hugging Face.")

if __name__ == "__main__":
    update_database()