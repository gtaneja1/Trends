import os
import pandas as pd
import numpy as np
import tensorflow as tf
from google import genai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress background hardware initialization logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Import your custom backend data-scraping and sentiment modules
from AI_BACKEND_TRAINING.social_scraper import get_live_reddit_trends
from AI_BACKEND_TRAINING.market_scraper import get_stock_data, get_live_news
from AI_BACKEND_TRAINING.sentiment_analyst import analyze_financial_data, analyze_social_media_data

print(" Booting Dual-Model Cascade Strategy Engine...")

app = Flask(__name__)
CORS(app)

# Configure Gemini using the new SDK
gemini_client = genai.Client(api_key=os.getenv("AIzaSyCY3Vr0GC_uyU1CmR5b0C5wtw7skO1ql2M"))

general_categories = ['politics', 'gaming', 'movies', 'sports', 'food', 'music', 'technology', 'books', 'science', 'art']

# =====================================================================
#   DYNAMIC PATH RESOLUTION MECHANISM (Fixes FileNotFoundError)
# =====================================================================
# Find the exact folder where this app.py file lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build bulletproof absolute paths to your subfolder assets
csv_path = os.path.join(BASE_DIR, "AI_BACKEND_TRAINING", "marketing_strategy_dataset.csv")
topic_model_path = os.path.join(BASE_DIR, "AI_BACKEND_TRAINING", "saved_general_topic_model.keras")
strategy_model_path = os.path.join(BASE_DIR, "AI_BACKEND_TRAINING", "saved_routing_model.keras")

# =====================================================================
#   LOAD DATA AND NEURAL NETWORKS WITH SYSTEM PATHS
# =====================================================================
print(f" Loading dataset from: {csv_path}...")
try:
    df_marketing = pd.read_csv(csv_path)
    marketing_categories = df_marketing["category_label"].unique().tolist()
except FileNotFoundError:
    print(f" Critical Error: Could not find CSV file at {csv_path}")
    exit(1)

print(" Loading Neural Networks into server memory...")
try:
    model_topic = tf.keras.models.load_model(topic_model_path)
    model_strategy = tf.keras.models.load_model(strategy_model_path)
    print("Cascade classification layers loaded successfully and warm!")
except Exception as e:
    print(f" Error loading models from their path dependencies: {e}")
    exit(1)

# =====================================================================
#   ROUTES
# =====================================================================
@app.route("/")
def home():
    return render_template("index.html")

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
        
        print("\n[ORCHESTRATOR] Step 1 of 5: Scraping Social trends...")
        social_data = get_live_reddit_trends(subreddit, keyword)
        
        print("\n[ORCHESTRATOR] Step 2 of 5: Fetching Market and Competitor News...")
        stock_data = get_stock_data(ticker)
        
        news_query = f"{niche} {keyword}"
        news_articles = get_live_news(news_query)
        
        print("\n[ORCHESTRATOR] Step 3 of 5: Analyzing text sentiments...")
        news_headlines = [art["title"] for art in news_articles]
        news_sentiments = []
        if news_headlines:
            news_sentiments = analyze_financial_data(news_headlines)
        
        for idx, art in enumerate(news_articles):
            if idx < len(news_sentiments):
                art["sentiment"] = news_sentiments[idx]
            else:
                art["sentiment"] = {"label": "neutral", "score": 0.50}
                
        social_keywords = [kw[0] for kw in social_data.get("keywords", [])]
        social_sentiments = []
        if social_keywords:
            social_sentiments = analyze_social_media_data(social_keywords)
            
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

        print("\n[ORCHESTRATOR] Step 4 of 5: Running Local Neural Classifications...")
        routing_tensor = tf.constant([problem])
        
        preds_topic = model_topic.predict(routing_tensor, verbose=0)
        idx_topic = np.argmax(preds_topic[0])
        detected_topic = general_categories[idx_topic]
        conf_topic = preds_topic[0][idx_topic] * 100
        
        preds_strategy = model_strategy.predict(routing_tensor, verbose=0)
        idx_strategy = np.argmax(preds_strategy[0])
        detected_strategy = marketing_categories[idx_strategy]
        
        print(f"   [Model 1 - Topic]: Sector targeted -> {detected_topic.upper()} ({conf_topic:.1f}% Confidence)")
        print(f"   [Model 2 - Route]: Operational route selected -> {detected_strategy.upper()}")
        
        matched_row = df_marketing[df_marketing["category_label"] == detected_strategy].iloc[0]
        custom_blueprint = matched_row["strategic_blueprint"]
        
        market_details = f"Symbol: {ticker.upper()} | Price: {stock_data.get('current_price', 0.0)} | Trend: {stock_data.get('change', 0.0)}"
        
        master_prompt = f"""
        You are an elite, enterprise-level growth consulting executive.
        
        CONTEXT AND SCOPE:
        - The client operates in the "{niche}" space.
        - Core product/focus word: "{keyword}"
        - Industry Sector Classification: {detected_topic.upper()}
        - Core Business Hurdle: "{problem}"
        - Live Market Metrics: {market_details}
        - Social Media Sentiment: {agg_social_label.upper()} (Score: {agg_social_score})
        
        OPERATIONAL STRATEGY FRAMEWORK ({detected_strategy.upper()}):
        You must structure this growth roadmap entirely around these mandatory guidelines from our internal database:
        {custom_blueprint}
        
        OUTPUT REQUIREMENT:
        Provide an exhaustive, phase-by-phase execution timeline mapping out how to fix the problem. 
        Do not include introductory or closing conversational fluff. Get straight to the business tactics.
        """
        
        print(" Synthesizing customized strategic roadmap with Gemini...")
        response = gemini_client.models.generate_content(
            model="gemini-1.5-pro",
            contents=master_prompt
        )
        strategy_playbook = response.text

        print("\n[ORCHESTRATOR] Step 5 of 5: Packaging payload for dashboard.")
        payload = {
            "status": "success",
            "niche": niche,
            "keyword": keyword,
            "subreddit": subreddit,
            "ticker": ticker.upper(),
            "detected_sector": detected_topic.upper(),
            "detected_framework": detected_strategy.upper(),
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
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"Launching flask server on port {port} (Debug: {debug_mode})...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=False)
