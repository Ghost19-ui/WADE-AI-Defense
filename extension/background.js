// background.js - WADE Intelligence Center (v5.0 - Dynamic Tranco Feed)
const API_URL = "https://reaper1907-wade-engine.hf.space"; 

// 1. DYNAMIC THREAT INTEL SYNC
chrome.runtime.onStartup.addListener(syncTrustedDomains);
chrome.runtime.onInstalled.addListener(syncTrustedDomains);

chrome.alarms.create("dailySync", { periodInMinutes: 1440 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "dailySync") syncTrustedDomains();
});

function syncTrustedDomains() {
    console.log("🛡️ WADE: Syncing Global Trusted Domains (Tranco Top 10k)...");
    fetch(`${API_URL}/trusted-domains`)
        .then(res => res.json())
        .then(data => {
            if (data.success && data.domains) {
                chrome.storage.local.set({ globalTrusted: data.domains }, () => {
                    console.log(`✅ WADE: Successfully memorized ${data.domains.length} safe domains.`);
                });
            }
        })
        .catch(err => console.error("❌ WADE: Failed to sync Tranco domains", err));
}

// 2. LOGGING HELPER
function saveToHistory(url, score, reason) {
    chrome.storage.local.get({ scanHistory: [] }, (result) => {
        let history = result.scanHistory;
        if (history.length > 0 && history[history.length - 1].url === url) return;

        history.push({
            url: url,
            score: score,
            reason: reason,
            date: new Date().toLocaleTimeString()
        });

        if (history.length > 20) history.shift();
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
    try {
        const hostname = new URL(url).hostname;

        chrome.storage.local.get({ globalTrusted: [], userTrust: {} }, (result) => {
            const globalList = result.globalTrusted;
            const userTrustData = result.userTrust;
            
            // A. Check Global Tranco List
            const isGlobal = globalList.some(d => hostname === d || hostname.endsWith("." + d));
            if (isGlobal || hostname === "localhost") {
                markSafe(tabId, "Global Trusted", url);
                return;
            }

            // B. Check User Learned Trust (Recalibrated to 2 for faster learning)
            const bypassCount = userTrustData[hostname] || 0;
            if (bypassCount >= 2) {
                markSafe(tabId, "User Trusted", url);
                return;
            }

            // C. If unknown, trigger the AI
            performScan(tabId, url);
        });
    } catch (e) { performScan(tabId, url); }
}

function markSafe(tabId, reason, url) {
    chrome.action.setBadgeText({text: "SAFE"});
    chrome.action.setBadgeBackgroundColor({color: "#00FF00"});
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
        saveToHistory(url, data.risk_score, data.threat_type || "AI Analysis");

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

// 5. MESSAGE HANDLERS
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
    
    if (request.action === "RESET_MEMORY") {
        chrome.storage.local.set({ userTrust: {}, scanHistory: [] }, () => {
            sendResponse({ success: true });
        });
        return true; 
    }

    if (request.action === "FETCH_JUNK_DATA") {
        sendResponse({ success: true, data: { name: "Alex Cipher", email: "trap@dummy.net" } });
    }

    // SMART HOVER/POPUP INTERCEPTOR
    if (request.action === "ANALYZE_URL" || request.action === "HOVER_SCAN") {
        try {
            const hostname = new URL(request.url).hostname;
            
            chrome.storage.local.get({ globalTrusted: [], userTrust: {} }, (result) => {
                const isGlobal = result.globalTrusted.some(d => hostname === d || hostname.endsWith("." + d));
                const bypassCount = result.userTrust[hostname] || 0;

                // Recalibrated here as well
                if (isGlobal || bypassCount >= 2 || hostname === "localhost") {
                    sendResponse({ 
                        success: true, 
                        data: { 
                            risk_score: 0, 
                            verdict: "SAFE", 
                            threat_type: "Trusted by Global DB", 
                            target_domain: hostname,
                            domain_age: 10000, 
                            vt_data: { total: "Tranco", malicious: 0 } 
                        } 
                    });
                    return;
                }

                fetch(`${API_URL}/analyze`, {
                    method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url: request.url })
                })
                .then(res => res.json())
                .then(data => sendResponse({ success: true, data: data }))
                .catch(err => sendResponse({ success: false, error: "API_FAILED" }));
            });
            return true; 
        } catch (e) {
            sendResponse({ success: false });
        }
    }
});