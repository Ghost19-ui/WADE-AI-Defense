import os

# --- INDUSTRY STANDARD ATTACK SIGNATURES (Pre-Compiled) ---
# These are the top patterns used by OWASP, PayloadAllTheThings, and HackTricks.
SIGNATURES = [
    # --- 1. XSS (Cross Site Scripting) ---
    "<script>", "javascript:", "vbscript:", "onload=", "onerror=", "onmouseover=", 
    "alert(", "prompt(", "confirm(", "eval(", "document.cookie", "document.domain",
    "window.location", "<img src=x", "<svg/onload", "javascript:alert", 
    "xss://", "autofocus", "onfocus=", "expression(",

    # --- 2. SQL Injection (SQLi) ---
    "union select", "union all select", "or 1=1", "' or '1'='1", "--", ";--", 
    "admin' --", "information_schema", "select * from", "drop table", "insert into",
    "xp_cmdshell", "waitfor delay", "pg_sleep", "dbms_pipe", "benchmark(",

    # --- 3. Command Injection (RCE) ---
    "cmd.exe", "/bin/sh", "/bin/bash", "/etc/passwd", "/etc/shadow", 
    "cat /etc/", "ping -c", "nc -e", "netcat", "wget ", "curl ", 
    "whoami", "id;", ";ls", "| ls", "&& ls", "powershell", 
    "Invoke-WebRequest", "bitsadmin", "certutil",

    # --- 4. Path Traversal & LFI ---
    "../", "..\\", "/..", "....//", "/proc/self/environ", "c:\\windows\\", 
    "boot.ini", "win.ini", "system32",

    # --- 5. Dangerous Files & Extensions ---
    ".exe", ".bat", ".sh", ".vbs", ".scr", ".com", ".pif", ".jar",
    "eicar.com", "eicar-standard-antivirus-test-file", 
    "malware", "shell.php", "backdoor", "trojan"
]

# Path to your existing data file
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir.endswith("backend"):
    OUTPUT_FILE = os.path.join(current_dir, "data", "malicious_signatures.txt")
else:
    OUTPUT_FILE = os.path.join("backend", "data", "malicious_signatures.txt")

def generate_database():
    print(f"🚀 GENERATING HIGH-VALUE SECURITY DATABASE...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    unique_sigs = sorted(list(set(SIGNATURES)))
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for sig in unique_sigs:
            f.write(sig + "\n")

    print(f"💾 SAVED TO: {OUTPUT_FILE}")
    print(f"✅ SUCCESS! Database populated with {len(unique_sigs)} elite attack signatures.")
    print("👉 ACTION: Upload the 'backend/data' folder to Hugging Face now.")

if __name__ == "__main__":
    generate_database()