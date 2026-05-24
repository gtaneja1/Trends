/**
 * ========================================================================
 *   SALES + MARKETING FORECAST - FRONTEND CONTROLLER (app.js)
 * ========================================================================
 *   Establishes connection between the Flask backend (/api/analyze)
 *   and your UI elements, safely handling empty HTML shells.
 * ========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("[Growth Matrix Active] Frontend controller connected and running.");

    // 1. DOM Element Cache References (Safe-checked)
    const form = document.getElementById('forecast-form');
    
    // 2. Initialize Charts (Only if canvas elements exist in HTML)
    initTrendsCharts();

    // 3. Register Event Listeners (Safe-checked)
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
        console.log(" -> Registered form submit event listener on #forecast-form.");
    } else {
        console.log(" -> Standing by. Awaiting text boxes and #forecast-form elements in index.html.");
        console.log(" -> TIP: You can test the Flask connection live right now in your browser console by typing:");
        console.log("    window.launchAnalysis({niche: 'streetwear', keyword: 'jacket', subreddit: 'streetwear', ticker: 'NKE', problem: 'Competitors selling cheap polyester.'});");
    }

    // Expose global test connection handle
    window.launchAnalysis = debugTestConnection;
});

/**
 * Initializes and configures Chart.js line and bar charts.
 * Safely checks if targeted canvas tags exist before initializing.
 */
function initTrendsCharts() {
    const stockCanvas = document.getElementById('stockChart');
    const socialCanvas = document.getElementById('socialChart');

    if (!stockCanvas && !socialCanvas) {
        console.log(" -> Canvas tags (#stockChart / #socialChart) not present in HTML. Bypassing Chart.js init.");
        return;
    }

    // If Chart.js library is loaded and canvases exist, configure them here
    console.log(" -> Chart canvas containers detected. Initializing Chart.js dashboards...");
}

/**
 * Handles the submit action of the inputs.
 * Validates data and sends it to `/api/analyze` via Fetch API.
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    console.log("[Growth Matrix] Form submitted. Extracting parameter parameters...");

    // Grabbing DOM values safely
    const nicheInput = document.getElementById('niche-input');
    const keywordInput = document.getElementById('keyword-input');
    const subredditInput = document.getElementById('subreddit-input');
    const tickerInput = document.getElementById('ticker-input');
    const problemInput = document.getElementById('problem-input');
    const submitBtn = document.getElementById('submit-btn');

    const params = {
        niche: nicheInput ? nicheInput.value.trim() : "streetwear apparel",
        keyword: keywordInput ? keywordInput.value.trim() : "corduroy",
        subreddit: subredditInput ? subredditInput.value.trim() : "streetwear",
        ticker: tickerInput ? tickerInput.value.trim() : "NKE",
        problem: problemInput ? problemInput.value.trim() : "Competitors selling cheap copies."
    };

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "SYNTHESIZING MATRIX...";
    }

    // Visual loading animations
    updatePipelineLoader(1, 'active');

    try {
        console.log(" -> Launching analysis pipelines for:", params);
        
        updatePipelineLoader(2, 'active');
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            console.log("[Growth Matrix Success] Scraped & Synthesized successfully!");
            updatePipelineLoader(4, 'complete');
            updatePipelineLoader(5, 'complete');
            
            // Populating UI cards
            renderForecastResults(data);
        } else {
            throw new Error(data.message || 'Pipeline failed');
        }

    } catch (err) {
        console.error("[Growth Matrix Error] Connection failed:", err);
        alert("Flask Pipeline Error: " + err.message);
        
        updatePipelineLoader(1, 'error');
        updatePipelineLoader(2, 'error');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "LAUNCH GROWTH ENGINE";
        }
    }
}

/**
 * Simulates or updates progress indicators for the 5-step pipeline.
 * Safely looks for list elements before executing toggles.
 */
function updatePipelineLoader(stepNum, status) {
    const stepEl = document.getElementById(`step-${stepNum}`);
    if (!stepEl) return;

    if (status === 'active') {
        stepEl.className = 'step active';
        stepEl.querySelector('.step-status').textContent = 'Scanning...';
    } else if (status === 'complete') {
        stepEl.className = 'step complete';
        stepEl.querySelector('.step-status').textContent = 'Done';
    } else if (status === 'error') {
        stepEl.className = 'step pending';
        stepEl.querySelector('.step-status').textContent = 'Error';
    }
}

/**
 * Parses and renders the structured JSON forecast returned by the Gemini API.
 * Safely updates text blocks, lists, and charts if they exist in templates.
 */
function renderForecastResults(data) {
    console.log("[Forecast Data Received]", data);

    // 1. Safe binding for Stock Quote Indicators
    const widgetPrice = document.getElementById('widget-ticker-price');
    if (widgetPrice) {
        widgetPrice.textContent = `$${data.market.current_price.toFixed(2)}`;
    }

    // 2. Safe binding for Niche Insights Markdown
    const insightsText = document.getElementById('insights-text');
    if (insightsText) {
        insightsText.textContent = data.strategy.niche_insights;
    }

    // 3. Safe binding for Actionable Next Steps cards
    const stepsContainer = document.getElementById('steps-card-container');
    if (stepsContainer) {
        stepsContainer.innerHTML = '';
        data.strategy.next_steps.forEach(step => {
            const card = document.createElement('div');
            card.className = 'step-card';
            card.innerHTML = `
                <h4>${step.title} (${step.impact} Impact / ${step.difficulty} Difficulty)</h4>
                <p>${step.description}</p>
            `;
            stepsContainer.appendChild(card);
        });
    }

    console.log(" -> Completed binding strategies to page elements.");
}

/**
 * Console Debugging Tool.
 * Directly calls the Flask backend and prints the AI generated sales playbook in console.
 */
async function debugTestConnection(testParams) {
    const defaultParams = {
        niche: "streetwear apparel",
        keyword: "corduroy",
        subreddit: "streetwear",
        ticker: "NKE",
        problem: "Sales are down because competitors sell cheap polyester copies."
    };
    
    const params = Object.assign({}, defaultParams, testParams);
    
    console.log("\n[TEST PIPELINE] Connecting to Flask server...");
    console.log(" -> Request Parameters:", params);
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        console.log("\n[TEST PIPELINE SUCCESS] Connected successfully!");
        console.log(" -> Social keywords & hashtags scraped:", data.social);
        console.log(" -> Competitor Market Prices pulled:", data.market);
        console.log(" -> Live News & Sentiments evaluated:", data.news);
        console.log(" -> Gemini AI Growth Playbook Synthesized:\n", data.strategy);
        return data;
    } catch (err) {
        console.error("\n[TEST PIPELINE ERROR] Connection failed:", err);
    }
}
