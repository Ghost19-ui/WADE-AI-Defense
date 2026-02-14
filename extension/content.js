// content.js - WADE Visual Interface (With "Proceed" Option)

let blockData = null;
const observer = new MutationObserver(() => {
    if (blockData && !document.getElementById('wade-block-screen')) {
        // console.log("Re-applying shield..."); // Optional: Commented out to allow bypass
    }
});

// 1. LISTEN FOR BLOCK COMMANDS
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "BLOCK_PAGE") {
        blockData = request.data;
        showBlockScreen(blockData);
    }
});

// 2. GENERATE BLOCK SCREEN UI
function showBlockScreen(data) {
    if (document.getElementById('wade-block-screen')) return;

    const div = document.createElement('div');
    div.id = 'wade-block-screen';
    div.innerHTML = `
        <div style="position:fixed; top:0; left:0; width:100%; height:100%; background:black; color:red; z-index:2147483647; display:flex; flex-direction:column; justify-content:center; align-items:center; font-family:Courier New, monospace; text-align:center;">
            <h1 style="font-size: 50px; text-shadow: 0 0 10px red;">🚫 ACCESS DENIED</h1>
            <h2>WADE Security Protocol Engaged</h2>
            
            <div style="border: 1px solid red; padding: 20px; margin: 20px; box-shadow: 0 0 20px red;">
                <p><strong>VERDICT:</strong> ${data.threat_type || "MALICIOUS"}</p>
                <p><strong>REASON:</strong> ${data.harm || "High Risk Detected"}</p>
            </div>

            <div style="display:flex; gap: 20px; flex-wrap: wrap; justify-content: center;">
                <button id="wade-back-btn" style="background:#333; color:white; padding:15px 30px; border:1px solid white; cursor:pointer; font-size:16px;">GO BACK</button>
                
                <button id="wade-proceed-btn" style="background:transparent; color:#888; padding:15px 30px; border:1px solid #888; cursor:pointer; font-size:16px;">
                    ⚠️ I KNOW THE RISK, PROCEED
                </button>

                <button id="wade-attack-btn" style="background:red; color:white; padding:15px 30px; border:none; cursor:pointer; font-size:16px; font-weight:bold; box-shadow: 0 0 15px red;">
                    ⚔️ LAUNCH COUNTER-ATTACK
                </button>
            </div>
            
            <div id="wade-console" style="margin-top:20px; color:#0f0; font-size:12px; height:150px; overflow:hidden; width:80%; text-align:left; background:#111; padding:10px; border:1px dashed #0f0;">
                System Ready. Awaiting Command...
            </div>
        </div>
    `;
    document.body.appendChild(div);
    document.body.style.overflow = 'hidden';

    // --- BUTTON ACTIONS ---
    
    // 1. Go Back (Safe)
    document.getElementById('wade-back-btn').onclick = () => window.history.back();

    // 2. Proceed (The Bypass Feature)
    document.getElementById('wade-proceed-btn').onclick = () => {
        // A. Remove the screen visually
        document.getElementById('wade-block-screen').remove();
        document.body.style.overflow = 'auto';
        blockData = null; // Stop the observer from re-blocking

        // B. Tell Background to learn this preference
        chrome.runtime.sendMessage({ action: "USER_BYPASS", url: window.location.href });
    };

    // 3. Counter Attack
    document.getElementById('wade-attack-btn').onclick = startCounterAttack;
}

function startCounterAttack() {
    const btn = document.getElementById('wade-attack-btn');
    const consoleDiv = document.getElementById('wade-console');
    
    btn.innerText = "⚡ DEPLOYING PAYLOADS...";
    btn.disabled = true;
    consoleDiv.innerHTML += `<br>> INITIATING COUNTER-MEASURES...<br>`;

    chrome.runtime.sendMessage({ action: "FETCH_JUNK_DATA" }, (response) => {
        if (response && response.success) {
            const junk = response.data;
            consoleDiv.innerHTML += `> CONNECTED TO CLOUD... 🟢<br>`;
            consoleDiv.innerHTML += `> GENERATING IDENTITY...<br>`;
            consoleDiv.innerHTML += `> --------------------------------<br>`;
            consoleDiv.innerHTML += `> NAME: ${junk.name}<br>`;
            consoleDiv.innerHTML += `> EMAIL: ${junk.email}<br>`;
            consoleDiv.innerHTML += `> PASS: ************<br>`;
            consoleDiv.innerHTML += `> CARD: ${junk.credit_card}<br>`;
            consoleDiv.innerHTML += `> --------------------------------<br>`;
            consoleDiv.innerHTML += `> PAYLOAD INJECTED. 🚀<br>`;
            btn.style.background = "green";
            btn.innerText = "✅ ATTACK COMPLETE";
        } else {
            consoleDiv.innerHTML += `> ERROR: Connection Failed.<br>`;
        }
    });
}