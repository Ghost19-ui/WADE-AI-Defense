// hover_script.js - WADE Heads-Up Display (Delegated Mode)

let hoverTimer = null;
let currentHUD = null;

// --- HELPERS ---
function formatAge(days) {
    if (days === "Hidden" || days === -1 || !days) return "❓ Age Unknown";
    const d = parseInt(days);
    if (isNaN(d)) return "❓ Data Unavailable";
    if (d < 30) return `⚠️ Fresh Site (${d} days)`;
    if (d < 365) return `📅 ${Math.floor(d/30)} Months Old`;
    return `🛡️ ${(d/365).toFixed(1)} Years Old`;
}

function formatVT(vt) {
    if (!vt || !vt.total || vt.total === "Database" || vt.total === "N/A") return "📡 No Database Match";
    if (vt.malicious > 0) return `🦠 ${vt.malicious}/${vt.total} Vendors Flagged This`;
    return `✅ Clean (${vt.total} Engines)`;
}

// --- LISTENERS ---
document.addEventListener('mouseover', (e) => {
    const target = e.target.closest('a');
    if (target && target.href.startsWith('http') && target.href !== window.location.href) {
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(() => showHUD(target, target.href), 800);
    }
});

document.addEventListener('mouseout', () => {
    clearTimeout(hoverTimer);
    if (currentHUD) currentHUD.remove();
});

// --- UI LOGIC ---
function showHUD(element, url) {
    if (currentHUD) currentHUD.remove();
    const hud = document.createElement('div');
    currentHUD = hud;
    
    hud.style.cssText = `
        position: absolute; z-index: 2147483647;
        background: rgba(5, 5, 8, 0.98); border: 1px solid #00f3ff;
        color: #00f3ff; padding: 15px; border-radius: 6px;
        font-family: 'Courier New', monospace; font-size: 12px;
        backdrop-filter: blur(8px); box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
        min-width: 260px; pointer-events: none; text-align: left; opacity: 0; transition: opacity 0.2s;
    `;
    
    const rect = element.getBoundingClientRect();
    hud.style.top = (window.scrollY + rect.bottom + 12) + 'px';
    hud.style.left = (window.scrollX + rect.left) + 'px';
    
    hud.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background: #00f3ff; box-shadow: 0 0 10px #00f3ff; animation: pulse 1s infinite;"></div>
            <span>SCANNING TARGET...</span>
        </div>
        <style>@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }</style>
    `;
    
    document.body.appendChild(hud);
    requestAnimationFrame(() => hud.style.opacity = '1');

    // DELEGATE TO BACKGROUND SCRIPT
    chrome.runtime.sendMessage({ action: "ANALYZE_URL", url: url }, (response) => {
        if (!response || !response.success) {
            hud.style.borderColor = '#ff003c';
            hud.innerHTML = `<div style="color: #ff003c; font-weight: bold;">❌ SCAN FAILED</div>`;
            return;
        }

        const data = response.data;
        let color = '#00f3ff';
        if (data.risk_score > 30) color = '#ffa500';
        if (data.risk_score > 75) color = '#ff003c';

        hud.style.borderColor = color;
        hud.style.boxShadow = `0 0 20px ${color}40`;

        hud.innerHTML = `
            <div style="border-bottom: 1px solid #333; padding-bottom: 8px; margin-bottom: 8px; display: flex; justify-content: space-between;">
                <span style="color: #888; font-size: 10px;">WADE PROTOCOL</span>
                <span style="color: ${color}; font-weight: bold; font-size: 14px;">RISK: ${data.risk_score}%</span>
            </div>
            <div style="margin-bottom: 6px; font-weight: bold; color: #fff;">${formatAge(data.domain_age)}</div>
            <div style="margin-bottom: 10px; font-size: 11px; color: #aaa;">${formatVT(data.vt_data)}</div>
            ${data.risk_score > 0 ? `<div style="color:${color}">⚠️ ${data.threat_type || "Threat Detected"}</div>` : `<div style="color:#00ff00">✅ VERIFIED SAFE</div>`}
        `;
    });
}