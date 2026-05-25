import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom backend modules
from AI_BACKEND_TRAINING.social_scraper import get_live_reddit_trends
from AI_BACKEND_TRAINING.market_scraper import get_stock_data, get_live_news
from AI_BACKEND_TRAINING.sentiment_analyst import analyze_financial_data, analyze_social_media_data
from AI_BACKEND_TRAINING.strategy_synthesizer import generate_growth_strategy

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for easy front-end debugging

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
        
        # Pull news based on a combination of niche and keyword
        news_query = f"{niche} {keyword}"
        news_articles = get_live_news(news_query)
        
        # ---------------------------------------------
        # STEP 3: SENTIMENT ANALYSIS (FinBERT + RoBERTa)
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 3 of 5: Analyzing text sentiments...")
        
        # Analyze sentiment of live news articles
        news_headlines = [art["title"] for art in news_articles]
        news_sentiments = []
        if news_headlines:
            news_sentiments = analyze_financial_data(news_headlines)
        
        # Append sentiment results to news articles
        for idx, art in enumerate(news_articles):
            if idx < len(news_sentiments):
                art["sentiment"] = news_sentiments[idx]
            else:
                art["sentiment"] = {"label": "neutral", "score": 0.50}
                
        # Analyze sentiment of social topics based on top keywords
        social_keywords = [kw[0] for kw in social_data.get("keywords", [])]
        social_sentiments = []
        if social_keywords:
            social_sentiments = analyze_social_media_data(social_keywords)
            
        # Compute an aggregate sentiment value for social media feeds
        pos_count = sum(1 for s in social_sentiments if s["label"] == "positive")
        neg_count = sum(1 for s in social_sentiments if s["label"] == "negative")
        
        if pos_count > neg_count:
            agg_social_label = "positive"
            agg_social_score = 0.5 + (0.1 * min(5, pos_count - neg_count))
        elif neg_count > pos_count:
            agg_social_label = "negative"
            agg_social_score = 0.5 + (0.1 * min(5, neg_count - pos_count))
        else:
            agg_social_label = "neutral"
            agg_social_score = 0.50
            
        social_data["aggregate_sentiment"] = {
            "label": agg_social_label,
            "score": round(agg_social_score, 2)
        }

        # ---------------------------------------------
        # STEP 4: STRATEGY SYNTHESIS (Gemini AI Engine)
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 4 of 5: Synthesizing strategy with Gemini API...")
        # Prepare stock detail
        market_details = {
            "symbol": ticker.upper(),
            "current_price": stock_data.get("current_price", 0.0),
            "change": stock_data.get("change", 0.0),
            "percent_change": stock_data.get("percent_change", 0.0)
        }
        
        strategy_playbook = generate_growth_strategy(
            niche=niche,
            topic=keyword,
            problem=problem,
            reddit_data={
                "keywords": social_data.get("keywords", []),
                "hashtags": social_data.get("hashtags", []),
                "news": news_articles[:5] # Include top 5 news with sentiment
            },
            market_data=market_details,
            news_sentiment=news_sentiments[:5]
        )

        # ---------------------------------------------
        # STEP 5: DELIVER DOCK PAYLOAD
        # ---------------------------------------------
        print("\n[ORCHESTRATOR] Step 5 of 5: Packaging payload for dashboard.")
        
        payload = {
            "status": "success",
            "niche": niche,
            "keyword": keyword,
            "subreddit": subreddit,
            "ticker": ticker.upper(),
            "social": {
                "keywords": social_data.get("keywords", []),
                "hashtags": social_data.get("hashtags", []),
                "trending_audios": social_data.get("trending_audios", []),
                "trending_people": social_data.get("trending_people", []),
                "sentiment": social_data["aggregate_sentiment"],
                "raw_count": social_data.get("raw_posts_count", 0)
            },
            "market": {
                "symbol": stock_data.get("symbol", ticker.upper()),
                "current_price": stock_data.get("current_price", 0.0),
                "change": stock_data.get("change", 0.0),
                "percent_change": stock_data.get("percent_change", 0.0),
                "dates": stock_data.get("dates", []),
                "prices": stock_data.get("prices", []),
                "source": stock_data.get("source", "mock")
            },
            "news": news_articles,
            "strategy": strategy_playbook
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
    # Get port from environment or default to 5000
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print(f"Launching flask server on port {port} (Debug: {debug_mode})...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
