import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Import our custom backend modules
from AI_BACKEND_TRAINING.social_scraper import get_live_reddit_trends
from AI_BACKEND_TRAINING.market_scraper import get_stock_data, get_live_news
from AI_BACKEND_TRAINING.sentiment_analyst import analyze_financial_data, analyze_social_media_data

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for easy front-end debugging

# Initialize OpenAI Client for the Multi-Agent Engine
# MAKE SURE 'OPENAI_API_KEY' IS IN YOUR .env FILE!
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================================
# MULTI-AGENT SYNTHESIZER FUNCTION
# ==========================================
def generate_elite_strategy(scraped_data):
    print("\n   -> [AGENT 1] Drafting Strategy via Chain-of-Thought...")
    draft_prompt = f"""
    You are an elite business strategist. Analyze this live data:
    {json.dumps(scraped_data)}
    
    Think step-by-step:
    1. Identify the core market gap based on the Reddit sentiment and News.
    2. Assess the competitor ticker weakness.
    3. Formulate 3 ruthless, non-generic tactical steps to solve the user's problem.
    
    Output the raw strategy draft.
    """
    
    draft_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": draft_prompt}],
        temperature=0.4
    )
    draft_strategy = draft_response.choices[0].message.content

    print("   -> [AGENT 2] Self-Correcting and formatting to strict JSON...")
    critic_prompt = f"""
    You are a skeptical hedge fund manager. Review this strategy draft:
    {draft_strategy}
    
    Remove all marketing fluff, corporate jargon, and generic advice.
    Reformat it into a strict JSON payload containing EXACTLY these keys:
    - "summary": A 4-sentence executive summary. Wrap exactly 2 critical business terms in <span class='highlight'> tags.
    - "proofText": A 2-sentence explanation of market drop-off. Wrap 1 term in <span class='highlight'> tags.
    - "chartLabels": An array of 3 string labels representing a funnel (e.g., ["Ad Impressions", "Cart Adds", "Purchases"]).
    - "chartData": An array of 3 descending integers representing funnel drop-off (e.g., [100, 45, 12]).
    - "tactical_steps": An array of exactly 3 objects. Each object must have:
        - "title" (string)
        - "description" (string)
        - "bullets" (array of 2-3 strings)
        - "confidence_score" (integer between 80 and 99)
        - "execution_asset" (string: A specific prompt, script, or email template to execute the step)
    """

    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": critic_prompt}],
        response_format={ "type": "json_object" },
        temperature=0.2 
    )
    
    return json.loads(final_response.choices[0].message.content)


# Root Route: Serve the interactive dashboard
@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# CORE ENDPOINT: PIPELINE ORCHESTRATION
# ==========================================
@app.route("/api/analyze", methods=["POST"])
def analyze_pipeline():
    try:
        # 1. Parse request parameters
        data = request.get_json() or {}
        
        niche = data.get("niche", "streetwear apparel").strip()
        keyword = data.get("keyword", "corduroy").strip()
        subreddit = data.get("subreddit", "streetwear").strip()
        ticker = data.get("ticker", "NKE").strip()
        problem = data.get("problem", "Competitors selling cheap alternatives.").strip()
        
        if not niche or not keyword or not subreddit or not ticker:
            return jsonify({"status": "error", "message": "Missing required search parameters."}), 400
            
        print(f"\n[ORCHESTRATOR] Initializing Growth Analysis Pipeline...")
        print(f" -> Niche: '{niche}' | Target: '{keyword}' | Subreddit: r/{subreddit} | Ticker: '{ticker}'")
        
        # ---------------------------------------------
        # STEP 1: SOCIAL SCRAPING (Reddit)
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 1 of 5: Scraping Social trends...")
        social_data = get_live_reddit_trends(subreddit, keyword)
        
        # ---------------------------------------------
        # STEP 2: MARKET & NEWS SCRAPING (yfinance + RSS)
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 2 of 5: Fetching Market and Competitor News...")
        stock_data = get_stock_data(ticker)
        
        news_query = f"{niche} {keyword}"
        news_articles = get_live_news(news_query)
        
        # ---------------------------------------------
        # STEP 3: SENTIMENT ANALYSIS (FinBERT + RoBERTa)
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 3 of 5: Analyzing text sentiments...")
        news_headlines = [art["title"] for art in news_articles]
        news_sentiments = analyze_financial_data(news_headlines) if news_headlines else []
        
        for idx, art in enumerate(news_articles):
            art["sentiment"] = news_sentiments[idx] if idx < len(news_sentiments) else {"label": "neutral", "score": 0.50}
                
        social_keywords = [kw[0] for kw in social_data.get("keywords", [])]
        social_sentiments = analyze_social_media_data(social_keywords) if social_keywords else []
            
        pos_count = sum(1 for s in social_sentiments if s["label"] == "positive")
        neg_count = sum(1 for s in social_sentiments if s["label"] == "negative")
        
        if pos_count > neg_count:
            agg_social_label, agg_social_score = "positive", 0.5 + (0.1 * min(5, pos_count - neg_count))
        elif neg_count > pos_count:
            agg_social_label, agg_social_score = "negative", 0.5 + (0.1 * min(5, neg_count - pos_count))
        else:
            agg_social_label, agg_social_score = "neutral", 0.50
            
        social_data["aggregate_sentiment"] = {
            "label": agg_social_label,
            "score": round(agg_social_score, 2)
        }

        # ---------------------------------------------
        # STEP 4: STRATEGY SYNTHESIS (Multi-Agent Engine)
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 4 of 5: Synthesizing strategy with Multi-Agent AI Engine...")
        
        # We package everything we scraped into one big dictionary to feed to the AI
        scraped_context = {
            "niche": niche,
            "problem": problem,
            "reddit_data": social_data.get("keywords", []),
            "social_sentiment": social_data["aggregate_sentiment"],
            "market_data": {
                "symbol": ticker.upper(),
                "percent_change": stock_data.get("percent_change", 0.0)
            },
            "news_headlines": news_headlines[:5]
        }
        
        # RUN THE AI!
        ai_strategy = generate_elite_strategy(scraped_context)

        # Build the HTML for the steps so it looks perfect on the frontend
        html_steps = ""
        for idx, step in enumerate(ai_strategy.get("tactical_steps", [])):
            bullet_html = "".join([f"<li>{b}</li>" for b in step.get("bullets", [])])
            html_steps += f"""
            <div class="linear-step">
                <div class="step-num">0{idx + 1}</div>
                <div class="step-content">
                    <h4>{step.get("title", "")}</h4>
                    <p>{step.get("description", "")}</p>
                    <ul class="step-list">{bullet_html}</ul>
                    <div class="confidence-wrapper">
                        <div class="confidence-ring" data-target="{step.get("confidence_score", 90)}"><span class="confidence-value">0%</span></div>
                        <span class="confidence-label">AI Execution Confidence</span>
                    </div>
                    <button class="deep-dive-btn">+ View Execution Assets</button>
                    <div class="deep-dive-content">
                        <span class="asset-tag">[ EXECUTION ASSET ]</span><br><br>{step.get("execution_asset", "")}
                    </div>
                </div>
            </div>
            """

        # ---------------------------------------------
        # STEP 5: DELIVER DOCK PAYLOAD
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 5 of 5: Packaging payload for dashboard.")
        
        payload = {
            "status": "success",
            "social": {
                "raw_count": social_data.get("raw_posts_count", "Live")
            },
            "market": {
                "symbol": stock_data.get("symbol", ticker.upper()),
                "dates": stock_data.get("dates", ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']),
                "prices": stock_data.get("prices", [0,0,0,0,0])
            },
            "strategy": {
                "summary": ai_strategy.get("summary", ""),
                "proofText": ai_strategy.get("proofText", ""),
                "chartLabels": ai_strategy.get("chartLabels", []),
                "chartData": ai_strategy.get("chartData", []),
                "steps": html_steps
            }
        }
        
        return jsonify(payload)

    except Exception as e:
        print(f"\n[ORCHESTRATOR ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Pipeline failure: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print(f"Launching flask server on port {port} (Debug: {debug_mode})...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)