# WADE: Web AI Defense Engine 🛡️

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Status](https://img.shields.io/badge/status-Stable-success)

**WADE** is a next-generation browser defense system that uses **Generative AI (Gemini 1.5)** and **Computer Vision** to detect zero-day phishing attacks, malicious scripts (XSS), and social engineering threats in real-time.

Unlike traditional antivirus tools that rely on static blacklists, WADE analyzes the *intent* and *context* of a webpage, allowing it to block never-before-seen threats.

---

## 🏗️ Architecture

WADE follows a **Service-Oriented Architecture (SOA)** with three core components:

1.  **The Eyes (Frontend):** A Chrome Extension that captures DOM structure, executed scripts, and screenshots.
2.  **The Brain (Backend):** A FastAPI server integrating Google Gemini 1.5 Pro for multimodal analysis (Vision + Code).
3.  **The Memory (Database):** MongoDB Atlas for logging threat intelligence and user feedback.

---

## 🚀 Key Features

### ✅ 1. Multimodal Phishing Detection
Combines **Optical Character Recognition (OCR)** and **Visual Analysis** to detect fake login forms that mimic banking/social sites, even if the URL is "fresh."

### ✅ 2. Active Script Analysis (XSS Defense)
Scrapes raw JavaScript from the DOM and uses an **LLM-based Code Auditor** to identify malicious patterns like cookie stealing (`document.cookie`), keylogging, and obfuscated payloads (`eval()`).

### ✅ 3. Real-Time Intervention
Hijacks the browser tab with a full-screen warning overlay when high-risk confidence (>75%) is detected, preventing user interaction with the malicious content.

---

## 🛠️ Tech Stack

* **AI & ML:** Google Gemini 1.5 Flash (Vision & Text), Scikit-Learn (Heuristics)
* **Backend:** Python, FastAPI, Uvicorn, Motor (Async MongoDB)
* **Frontend:** JavaScript (ES6), Chrome Extension API (Manifest V3)
* **Database:** MongoDB Atlas (Cloud)
* **Infrastructure:** Render (Cloud Hosting)

---

## 🔮 Future Roadmap (Enterprise Scale)

* **Redis Caching Layer:** Implementing an LRU cache to reduce API latency for frequently visited domains.
* **Local LLM Support:** Integration with **Ollama (Llama 3)** for on-premise, privacy-preserving analysis (Data Sovereignty).
* **SIEM Integration:** Webhook support for pushing threat logs to Splunk/ElasticSearch.

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/Ghost19-ui/WADE-AI-Defense.git](https://github.com/Ghost19-ui/WADE-AI-Defense.git)
cd WADE-AI-Defense


👨‍💻 Author
Tushar Kumar Saini Cybersecurity Content Strategist & B.Tech CSE Student Parul University

Built for the Future of Web Security.
