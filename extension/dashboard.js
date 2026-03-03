document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();

    // --- NEW SMART URL EXTRACTOR ---
    function extractHostname(input) {
        let cleanInput = input.trim().toLowerCase();
        if (!cleanInput) return "";
        try {
            // If the user pastes a full URL with http/https
            if (cleanInput.startsWith("http://") || cleanInput.startsWith("https://")) {
                return new URL(cleanInput).hostname;
            }
            // If they just type "google.com", force parse it
            return new URL("https://" + cleanInput).hostname;
        } catch (e) {
            return cleanInput; // Fallback
        }
    }

    // Event Listeners for Manual Input
    document.getElementById("add-whitelist").addEventListener("click", () => {
        const domain = document.getElementById("whitelist-input").value.trim().toLowerCase();
        if (domain) modifyList('whitelist', 'add', domain);
        document.getElementById("whitelist-input").value = '';
    });

    document.getElementById("add-blacklist").addEventListener("click", () => {
        const domain = document.getElementById("blacklist-input").value.trim().toLowerCase();
        if (domain) modifyList('blacklist', 'add', domain);
        document.getElementById("blacklist-input").value = '';
    });
});

function loadDashboardData() {
    chrome.storage.local.get({ scanHistory: [], userTrust: {}, userBlacklist: [] }, (data) => {
        const history = data.scanHistory.reverse();
        const trustData = data.userTrust;
        const blacklistData = data.userBlacklist;
        
        // 1. Calculate Stats
        const trustedDomains = Object.keys(trustData).filter(d => trustData[d] >= 2);
        document.getElementById("stat-total-scans").innerText = history.length;
        document.getElementById("stat-blocked").innerText = blacklistData.length;
        document.getElementById("stat-trusted").innerText = trustedDomains.length;

        // 2. Populate History
        const historyTable = document.getElementById("history-table-body");
        historyTable.innerHTML = "";
        if (history.length === 0) {
            historyTable.innerHTML = `<tr><td colspan="5" class="empty-state">No scans logged.</td></tr>`;
        } else {
            history.forEach(scan => {
                let hostname = "unknown";
                try { hostname = new URL(scan.url).hostname; } catch(e) {}

                const tr = document.createElement("tr");
                let badgeClass = scan.score > 75 ? "danger" : (scan.score > 30 ? "warning" : "safe");
                let badgeText = scan.score > 75 ? "BLOCKED" : (scan.score > 30 ? "WARNING" : "SAFE");
                const displayUrl = scan.url.length > 35 ? scan.url.substring(0, 35) + "..." : scan.url;

                tr.innerHTML = `
                    <td style="color: var(--text-muted);">${scan.date}</td>
                    <td title="${scan.url}">${displayUrl}</td>
                    <td style="color: var(--primary-cyan); font-weight:bold;">${scan.score}</td>
                    <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                    <td>
                        <button class="btn-action btn-white" onclick="modifyList('whitelist', 'add', '${hostname}')">Trust</button>
                        <button class="btn-action btn-black" onclick="modifyList('blacklist', 'add', '${hostname}')">Block</button>
                    </td>
                `;
                historyTable.appendChild(tr);
            });
        }

        // 3. Populate Whitelist
        const whitelistTable = document.getElementById("whitelist-table-body");
        whitelistTable.innerHTML = "";
        if (trustedDomains.length === 0) whitelistTable.innerHTML = `<tr><td class="empty-state">No trusted domains.</td></tr>`;
        else {
            trustedDomains.forEach(domain => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="color: var(--safe-green); font-weight: bold;">${domain}</td>
                    <td style="text-align:right;"><button class="btn-action btn-remove" onclick="modifyList('whitelist', 'remove', '${domain}')">Remove</button></td>
                `;
                whitelistTable.appendChild(tr);
            });
        }

        // 4. Populate Blacklist
        const blacklistTable = document.getElementById("blacklist-table-body");
        blacklistTable.innerHTML = "";
        if (blacklistData.length === 0) blacklistTable.innerHTML = `<tr><td class="empty-state">No custom blocks.</td></tr>`;
        else {
            blacklistData.forEach(domain => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="color: var(--danger-red); font-weight: bold;">${domain}</td>
                    <td style="text-align:right;"><button class="btn-action btn-remove" onclick="modifyList('blacklist', 'remove', '${domain}')">Remove</button></td>
                `;
                blacklistTable.appendChild(tr);
            });
        }
    });
}

// Logic to modify Chrome Storage
window.modifyList = function(listType, action, domain) {
    if (!domain || domain === 'unknown') return;

    chrome.storage.local.get({ userTrust: {}, userBlacklist: [] }, (data) => {
        let trustData = data.userTrust;
        let blacklistData = data.userBlacklist;

        if (listType === 'whitelist') {
            if (action === 'add') {
                trustData[domain] = 3; // Set threshold high enough to trust
                blacklistData = blacklistData.filter(d => d !== domain); // Remove from blacklist if it's there
            } else if (action === 'remove') {
                delete trustData[domain];
            }
        } 
        else if (listType === 'blacklist') {
            if (action === 'add') {
                if (!blacklistData.includes(domain)) blacklistData.push(domain);
                delete trustData[domain]; // Remove from whitelist if it's there
            } else if (action === 'remove') {
                blacklistData = blacklistData.filter(d => d !== domain);
            }
        }

        // Save back to storage and reload UI
        chrome.storage.local.set({ userTrust: trustData, userBlacklist: blacklistData }, () => {
            loadDashboardData();
        });
    });
};