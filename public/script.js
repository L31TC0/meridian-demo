/* ==========================================================================
   Foundations — Account Brief Generator (client)
   ========================================================================== */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let allAccounts = [];          // [{ account_id, company_name }, ...]
let scenarios = {};            // { upsell: [...], active_deal: [...], complex: [...] }
let activeScenario = null;
const DEMO_PASSWORD = null;    // Set via inline script from env, or null to skip gate

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async () => {
    // Check if password gate should show — skip if placeholder or empty
    const pw = window.__DEMO_PASSWORD;
    if (pw && pw !== "__DEMO_PASS__" && pw !== "") {
        setupGate(pw);
    } else {
        showApp();
    }
});

// ---------------------------------------------------------------------------
// Password gate
// ---------------------------------------------------------------------------

function setupGate(password) {
    const gate = document.getElementById("gate");
    const app = document.getElementById("app");
    const input = document.getElementById("gate-password");
    const btn = document.getElementById("gate-submit");
    const error = document.getElementById("gate-error");

    // Check if already authenticated this session
    if (sessionStorage.getItem("foundations_auth") === "1") {
        gate.style.display = "none";
        showApp();
        return;
    }

    gate.style.display = "flex";

    const attempt = () => {
        if (input.value === password) {
            sessionStorage.setItem("foundations_auth", "1");
            gate.style.display = "none";
            showApp();
        } else {
            error.textContent = "Incorrect password";
            input.value = "";
            input.focus();
        }
    };

    btn.addEventListener("click", attempt);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") attempt();
    });
}

async function showApp() {
    const app = document.getElementById("app");
    app.classList.add("visible");
    await loadAccounts();
    wireUI();
}

// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

async function loadAccounts() {
    try {
        const res = await fetch("/api/generate");
        const data = await res.json();
        allAccounts = data.accounts;
        scenarios = data.scenarios;
        populateDropdown(allAccounts);
    } catch (err) {
        console.error("Failed to load accounts:", err);
    }
}

function populateDropdown(accounts) {
    const select = document.getElementById("account-select");
    // Keep the first placeholder option
    select.length = 1;
    for (const a of accounts) {
        const opt = document.createElement("option");
        opt.value = a.account_id;
        opt.textContent = `${a.company_name}  \u00b7  ${a.account_id}`;
        select.appendChild(opt);
    }
}

// ---------------------------------------------------------------------------
// UI wiring
// ---------------------------------------------------------------------------

function wireUI() {
    // Scenario buttons
    document.querySelectorAll(".scenario-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const key = btn.dataset.scenario;
            if (activeScenario === key) {
                clearFilter();
            } else {
                setScenario(key);
            }
        });
    });

    // Clear filter
    document.getElementById("clear-filter").addEventListener("click", clearFilter);

    // Generate button
    document.getElementById("btn-generate").addEventListener("click", generateBrief);

    // Also generate on Enter in the select
    document.getElementById("account-select").addEventListener("keydown", (e) => {
        if (e.key === "Enter") generateBrief();
    });
}

function setScenario(key) {
    activeScenario = key;

    // Update button active states
    document.querySelectorAll(".scenario-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.scenario === key);
    });

    // Filter dropdown
    const filtered = allAccounts.filter((a) => scenarios[key]?.includes(a.account_id));
    populateDropdown(filtered);

    // Show status
    const labels = {
        upsell: "Upsell / Cross-Sell",
        active_deal: "Active Deal",
        complex: "Complex Pipeline",
    };
    const status = document.getElementById("filter-status");
    status.innerHTML = `Showing <strong>${filtered.length}</strong> accounts matching <strong>${labels[key]}</strong>`;
    document.getElementById("clear-filter").style.display = "inline";
}

function clearFilter() {
    activeScenario = null;
    document.querySelectorAll(".scenario-btn").forEach((btn) => {
        btn.classList.remove("active");
    });
    populateDropdown(allAccounts);
    document.getElementById("filter-status").innerHTML = "";
    document.getElementById("clear-filter").style.display = "none";
}

// ---------------------------------------------------------------------------
// Brief generation
// ---------------------------------------------------------------------------

async function generateBrief() {
    const select = document.getElementById("account-select");
    const accountId = select.value;
    if (!accountId) return;

    const output = document.getElementById("output");
    const btn = document.getElementById("btn-generate");

    btn.disabled = true;

    // Loading animation
    output.innerHTML = '<p class="loading-msg">Reading 5 data sources\u2026</p>';
    const start = performance.now();

    await sleep(800);
    output.innerHTML = '<p class="loading-msg">Synthesizing account brief\u2026</p>';
    await sleep(600);

    try {
        const res = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ account_id: accountId }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || "Generation failed");
        }

        const data = await res.json();
        const elapsed = ((performance.now() - start) / 1000).toFixed(1);

        // Convert markdown to HTML
        const briefHtml = markdownToHtml(data.brief_md);

        output.innerHTML =
            `<div class="meta-strip">` +
            `Generated in ${elapsed}s &nbsp;\u00b7&nbsp; 5 sources &nbsp;\u00b7&nbsp; ${data.total_points} data points synthesized` +
            `</div>` +
            `<div class="brief-card">${briefHtml}</div>`;
    } catch (err) {
        output.innerHTML = `<p class="loading-msg" style="color:var(--ignite);">Error: ${err.message}</p>`;
    }

    btn.disabled = false;
}

// ---------------------------------------------------------------------------
// Minimal markdown -> HTML converter
// Handles: h1, h2, bold, italic, hr, unordered lists, ordered lists, <br>
// ---------------------------------------------------------------------------

function markdownToHtml(md) {
    const lines = md.split("\n");
    let html = "";
    let inUl = false;
    let inOl = false;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];

        // Horizontal rule
        if (/^---\s*$/.test(line)) {
            if (inUl) { html += "</ul>"; inUl = false; }
            if (inOl) { html += "</ol>"; inOl = false; }
            html += "<hr>";
            continue;
        }

        // Headers
        if (line.startsWith("## ")) {
            if (inUl) { html += "</ul>"; inUl = false; }
            if (inOl) { html += "</ol>"; inOl = false; }
            html += `<h2>${inlineFormat(line.slice(3))}</h2>`;
            continue;
        }
        if (line.startsWith("# ")) {
            if (inUl) { html += "</ul>"; inUl = false; }
            if (inOl) { html += "</ol>"; inOl = false; }
            html += `<h1>${inlineFormat(line.slice(2))}</h1>`;
            continue;
        }

        // Ordered list item (e.g., "1. ...")
        const olMatch = line.match(/^(\d+)\.\s+(.*)$/);
        if (olMatch) {
            if (inUl) { html += "</ul>"; inUl = false; }
            if (!inOl) { html += "<ol>"; inOl = true; }
            html += `<li>${inlineFormat(olMatch[2])}</li>`;
            continue;
        }

        // Unordered list item
        if (line.startsWith("- ")) {
            if (inOl) { html += "</ol>"; inOl = false; }
            if (!inUl) { html += "<ul>"; inUl = true; }
            html += `<li>${inlineFormat(line.slice(2))}</li>`;
            continue;
        }

        // Continuation line (indented under a list item)
        if (/^\s{2,}/.test(line) && (inUl || inOl)) {
            // Append to previous list item
            html = html.replace(/<\/li>$/, ` ${inlineFormat(line.trim())}</li>`);
            continue;
        }

        // Close any open list
        if (inUl) { html += "</ul>"; inUl = false; }
        if (inOl) { html += "</ol>"; inOl = false; }

        // Blank line
        if (line.trim() === "") continue;

        // Paragraph
        html += `<p>${inlineFormat(line)}</p>`;
    }

    if (inUl) html += "</ul>";
    if (inOl) html += "</ol>";

    return html;
}

function inlineFormat(text) {
    // Bold: **text**
    text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    // Italic: *text* (but not inside **)
    text = text.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, "<em>$1</em>");
    // _text_ italic
    text = text.replace(/_([^_]+?)_/g, "<em>$1</em>");
    // Line break: two trailing spaces
    text = text.replace(/ {2,}$/, "<br>");
    return text;
}

// ---------------------------------------------------------------------------
// Util
// ---------------------------------------------------------------------------

function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}
