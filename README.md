# WADE: Web AI Defense Engine 🛡️

**WADE (Web AI Defense Engine)** is a next-generation browser Intrusion Prevention System (IPS). It acts as an active edge-sensor in your browser, utilizing **Large Language Models (Groq Llama-3 & Google Gemini)** and **OSINT Threat Intelligence** to detect zero-day phishing attacks, malicious scripts, and newly registered hostile domains in real-time.

Unlike traditional antivirus tools that rely solely on outdated static blacklists, WADE analyzes the *intent*, *context*, and *origin* of web traffic, allowing it to block never-before-seen threats before the page even renders.

---

## 🏗️ Architecture (Phase 2)

WADE follows a highly efficient, cloud-integrated **Microservice Architecture**:

1. **The Edge Sensor (Chrome Extension):** Built on Manifest V3. It intercepts web navigation, neutralizes malicious inline scripts (XSS), and manages zero-latency trusted caching.
2. **The Intelligence Core (FastAPI Backend):** Hosted on **Hugging Face Spaces**. It orchestrates asynchronous OSINT lookups (VirusTotal, WHOIS) and prompts the LLM models to generate a definitive risk score.
3. **The Memory (SQLite & Local Storage):** Uses a lightweight cloud SQLite database (`wade_logs.db`) for scan history, alongside Chrome's `storage.local` for the user's custom "3-Strike" trust memory.

---

## 🚀 Key Features

### ✅ 1. Hybrid AI Threat Detection

Utilizes **Groq (Llama 3.3 70B)** for ultra-low latency heuristic analysis, with an automatic fallback to **Google Gemini 1.5 Flash**. It objectively evaluates domain age, security vendor flags, and URL patterns to generate a precise Risk Score (0-100%).

### ✅ 2. Zero-Latency Fast Path

Integrates an in-memory cache of the **Tranco Top 10,000 Global Domains** and custom user whitelists. Traffic to known safe sites routes instantly without triggering API overhead or network delays.

### ✅ 3. Interactive Heads-Up Display (HUD)

Features a proactive link scanner. Hovering over any hyperlink (e.g., in a webmail client) triggers a floating cyberpunk-styled tooltip that reveals the AI's risk assessment and domain age *before* the user clicks.

### ✅ 4. Real-Time Intervention & Red Isolation

When high-risk confidence (>75%) is detected, WADE physically severs the browser connection and forces a strict Content Security Policy (CSP) compliant "Access Denied" isolation screen, preventing drive-by downloads.

### ✅ 5. 3D Analytics Command Center

A fully integrated, local-storage-powered dashboard featuring interactive donut charts, threat logs, and manual whitelist/blacklist controls rendered with CSS3 glass-morphism.

---

## 🛠️ Tech Stack

* **AI Models:** Groq API (Llama 3.3 70B), Google Gemini 1.5 Flash
* **Backend:** Python, FastAPI, Uvicorn, SQLite3, `concurrent.futures`
* **Frontend:** Vanilla JavaScript (ES6+), HTML5, Advanced CSS3 (3D Transforms)
* **Browser API:** Google Chrome Manifest V3 (Service Workers, MutationObservers)
* **Threat Intel:** VirusTotal v3 API, URLHaus, Phishing.Database, Python `whois`
* **Infrastructure:** Hugging Face Spaces (Dockerized Deployment)

---

## 📦 Installation & Setup

### 1. Cloud Backend Setup (Hugging Face / Local)

If you wish to host your own instance of the backend API:

```bash
git clone https://github.com/Ghost19-ui/WADE-AI-Defense.git
cd WADE-AI-Defense

# Install dependencies
pip install -r requirements.txt

# Set your API keys as environment variables
export GROQ_API_KEY="your_groq_key"
export GEMINI_API_KEY="your_gemini_key"
export VIRUSTOTAL_API_KEY="your_vt_key"

# Run the FastAPI server
python app.py

```

### 2. Chrome Extension Setup

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **"Developer mode"** in the top right corner.
3. Click **"Load unpacked"**.
4. Select the `extension` folder located inside the cloned `WADE-AI-Defense` directory.
5. Pin the WADE shield icon to your toolbar and browse safely.

*(Note: To point the extension to a local backend instead of the live Hugging Face deployment, update the `API_URL` variable in `extension/background.js` and `extension/hover_script.js` to `http://127.0.0.1:7860`)*.

---

## 👨‍💻 Author

**Tushar Kumar Saini** *Cybersecurity Content Strategist, Red Team Operator, & B.Tech CSE Student at Parul University.* Built for the Future of Web Security.