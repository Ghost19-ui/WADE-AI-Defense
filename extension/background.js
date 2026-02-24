// background.js - WADE Intelligence Center (Final V3)
const API_URL = "https://reaper1907-wade-engine.hf.space"; 

// 1. GLOBAL ALLOWLIST
const TRUSTED_DOMAINS = [
"google.com", "google.co.in", "youtube.com", "gmail.com", "drive.google.com", "gstatic.com",
    
    // Developer & Cloud Platforms
    "github.com", "stackoverflow.com", "huggingface.co", "gitlab.com", "aws.amazon.com",
    
    // Microsoft Ecosystem
    "microsoft.com", "office.com", "bing.com", "live.com", "sharepoint.com",
    
    // Productivity & Design Tools
    "canva.com", "canva.in", "notion.so", "figma.com", "slack.com", "trello.com",
    
    // Professional & Social Networking
    "linkedin.com", "reddit.com", "twitter.com", "x.com",
    
    // Major Frameworks & Documentation
    "angularjs.org", "angular.io", "react.dev", "vuejs.org", "developer.mozilla.org",
    
    // Institutional / Custom User Trusts
    "paruluniversity.ac.in",
];

function isGlobalTrusted(url) {
    try {
        const hostname = new URL(url).hostname;
        return TRUSTED_DOMAINS.some(d => hostname === d || hostname.endsWith("." + d));
    } catch (e) { return false; }
}

// 2. LOGGING HELPER (Fixes Empty History)
function saveToHistory(url, score, reason) {
    chrome.storage.local.get({ scanHistory: [] }, (result) => {
        let history = result.scanHistory;
        // Prevent duplicate entries for the same URL in a row
        if (history.length > 0 && history[history.length - 1].url === url) return;

        history.push({
            url: url,
            score: score,
            reason: reason,
            date: new Date().toLocaleTimeString()
        });

        if (history.length > 20) history.shift(); // Keep last 20
        chrome.storage.local.set({ scanHistory: history });
    });
}

// 3. ROUTING LOGIC
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        handleUrl(tabId, tab.url);
    }
});

function handleUrl(tabId, url) {
    // A. Check Global Trust
    if (isGlobalTrusted(url)) {
        markSafe(tabId, "Global Trusted", url);
        return;
    }

    // B. Check User Learned Trust
    try {
        const hostname = new URL(url).hostname;
        chrome.storage.local.get({ userTrust: {} }, (result) => {
            const trustData = result.userTrust;
            const bypassCount = trustData[hostname] || 0;

            if (bypassCount >= 3) {
                console.log(`🛡️ WADE: Skipping ${hostname} (User Trusted)`);
                markSafe(tabId, "User Trusted", url);
                return;
            }
            performScan(tabId, url);
        });
    } catch (e) { performScan(tabId, url); }
}

function markSafe(tabId, reason, url) {
    chrome.action.setBadgeText({text: "SAFE"});
    chrome.action.setBadgeBackgroundColor({color: "#00FF00"});
    
    // SAVE TO HISTORY (This fixes your bug)
    saveToHistory(url, 0, reason);

    chrome.tabs.sendMessage(tabId, { 
        action: "SCAN_RESULT", 
        data: { risk_score: 0, threat_type: reason, harm: "None" } 
    }).catch(() => {});
}

// 4. AI SCANNING
function performScan(tabId, url) {
    chrome.action.setBadgeText({text: "..."});
    chrome.action.setBadgeBackgroundColor({color: "#888"});

    fetch(`${API_URL}/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    })
    .then(res => res.json())
    .then(data => {
        updateBadge(data.risk_score);
        saveToHistory(url, data.risk_score, data.threat_type || " AI Analysis");

        chrome.tabs.sendMessage(tabId, { action: "SCAN_RESULT", data: data }).catch(() => {});

        if (data.risk_score > 75) {
            chrome.tabs.sendMessage(tabId, { action: "BLOCK_PAGE", data: data }).catch(() => {});
            setTimeout(() => chrome.tabs.sendMessage(tabId, { action: "BLOCK_PAGE", data: data }).catch(() => {}), 1500);
        }
    })
    .catch(() => chrome.action.setBadgeText({text: "ERR"}));
}

function updateBadge(score) {
    chrome.action.setBadgeText({text: score.toString()});
    let color = score > 75 ? "#FF0000" : (score > 30 ? "#FFA500" : "#00FF00");
    chrome.action.setBadgeBackgroundColor({color: color});
}

// 5. MESSAGE HANDLERS (Reset & Downloads)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "USER_BYPASS") {
        try {
            const hostname = new URL(request.url).hostname;
            chrome.storage.local.get({ userTrust: {} }, (result) => {
                const trustData = result.userTrust;
                trustData[hostname] = (trustData[hostname] || 0) + 1;
                chrome.storage.local.set({ userTrust: trustData });
            });
        } catch (e) {}
    }
    
    // NEW: UNDO BUTTON LOGIC
    if (request.action === "RESET_MEMORY") {
        chrome.storage.local.set({ userTrust: {}, scanHistory: [] }, () => {
            sendResponse({ success: true });
        });
        return true; 
    }

    if (request.action === "FETCH_JUNK_DATA") {
        // ... (Keep your existing Counter Attack logic here) ...
        sendResponse({ success: true, data: { name: "Alex Cipher", email: "trap@dummy.net" } });
    }
});