/**
 * ========================================================================
 *   SALES + MARKETING FORECAST - FRONTEND CONTROLLER (app.js)
 * ========================================================================
 *   Bridges your premium NeuroStrat UI with the scraping and synthesis
 *   pipelines served by Flask on '/api/analyze'.
 * ========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("[NeuroStrat Active] Frontend controller connected and running.");

    // Expose the analysis starter globally so it can be called from index.html
    window.handleStrategySynthesis = triggerLiveAnalysis;
});

/**
 * Triggers the live analysis by capturing form inputs, sending a POST request 
 * to '/api/analyze', and populating the results panel.
 */
async function triggerLiveAnalysis() {
    console.log("[NeuroStrat] Launching backend scraping and AI synthesis...");

    // 1. Get DOM inputs safely
    const fieldInput = document.getElementById('business_field');
    const problemInput = document.getElementById('core_problem');
    const audienceInput = document.getElementById('target_audience');
    const resultsPanel = document.getElementById('strategy-results-panel');
    const initBtn = document.getElementById('init-btn');

    const params = {
        niche: fieldInput ? fieldInput.value.trim() : "Sustainable Apparel",
        problem: problemInput ? problemInput.value.trim() : "Increasing customer acquisition costs.",
        audience: audienceInput ? audienceInput.value.trim() : "Gen Z females"
    };

    if (initBtn) {
        initBtn.disabled = true;
        initBtn.textContent = "SYNTHESIZING STRATEGIES...";
    }

    try {
        console.log(" -> Dispatching parameters to Flask:", params);
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error(`HTTP Error! Status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            console.log("[NeuroStrat Success] Strategic Playbook compiled successfully!");
            renderForecastResults(data);
        } else {
            throw new Error(data.message || 'Scraper or synthesis pipeline failed.');
        }

    } catch (err) {
        console.error("[NeuroStrat Error] Execution failed:", err);
        alert("Strategic Sync Error: " + err.message + "\n\nEnsure Flask is running and check your Python terminal for details.");
    } finally {
        if (initBtn) {
            initBtn.disabled = false;
            initBtn.textContent = "Initialize AI Strategy";
        }
    }
}

/**
 * Renders the consolidated scraper results and the Gemini playbook on the screen.
 */
function renderForecastResults(data) {
    console.log("[Forecast Data Ingested]", data);

    const resultsPanel = document.getElementById('strategy-results-panel');
    const insightsText = document.getElementById('insights-text');
    const stepsContainer = document.getElementById('steps-card-container');

    // 1. Render Niche Insights text
    if (insightsText) {
        // If the AI key is active, it returns live strategies; otherwise it returns custom fallbacks
        insightsText.textContent = data.strategy.niche_insights || "Insights successfully processed.";
    }

    // 2. Render Actionable Next Steps cards
    if (stepsContainer && data.strategy.next_steps) {
        stepsContainer.innerHTML = '';
        
        data.strategy.next_steps.forEach(step => {
            const card = document.createElement('div');
            card.className = 'panel hover-card';
            card.style.display = 'flex';
            card.style.flexDirection = 'column';
            card.style.gap = '12px';
            card.style.transition = 'all 0.3s ease';
            card.style.cursor = 'pointer';
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-light); padding-bottom: 8px;">
                    <h4 style="font-size: 18px; font-weight: 800; font-family: 'Plus Jakarta Sans', sans-serif;">${step.title}</h4>
                    <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 4px 10px; background: var(--bg-main); border-radius: 100px;">
                        ${step.impact} Impact
                    </span>
                </div>
                <p style="font-size: 14px; line-height: 1.6; color: var(--text-muted);">${step.description}</p>
                <div style="margin-top: auto; font-size: 12px; font-weight: 700; color: var(--brand-primary); text-transform: uppercase; letter-spacing: 0.5px;">
                    Difficulty: ${step.difficulty}
                </div>
            `;
            
            // Add mouse-move parallax effect listener to new cards
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
                card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
            });
            
            stepsContainer.appendChild(card);
        });
    }

    // 3. Display Results Panel & Scroll Into View smoothly
    if (resultsPanel) {
        resultsPanel.style.display = 'block';
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
