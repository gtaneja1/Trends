# ========================================================================
#   SALES + MARKETING FORECAST - BACKEND SERVER (app.py)
# ========================================================================

import os
import sys
from flask import Flask, render_template, request, jsonify

# Add the AI backend directory to sys.path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'AI_BACKEND_TRAINING'))

# Import custom AI scraper and synthesizer modules
try:
    import social_scraper
    import market_scraper
    import sentiment_analyst
    import strategy_synthesizer
except ImportError as e:
    print(f" [WARNING] Could not import backend training modules: {e}")

# Initialize the Flask application
app = Flask(__name__)

# Helper to dynamically map niche key phrases to subreddits and tickers
def resolve_niche_parameters(business_field):
    field_lower = business_field.lower()
    
    # Fashion/Apparel Niche
    if any(word in field_lower for word in ["fashion", "apparel", "clothing", "streetwear", "shoe", "brand", "design"]):
        return "streetwear", "NKE", "fashion design"
    # Crypto Niche
    elif any(word in field_lower for word in ["crypto", "bitcoin", "ethereum", "coin", "blockchain"]):
        return "CryptoCurrency", "COIN", "crypto tokens"
    # Tech/AI Niche
    elif any(word in field_lower for word in ["tech", "software", "saas", "ai", "hardware", "app"]):
        return "technology", "MSFT", "artificial intelligence"
    # Finance/Stocks Niche
    elif any(word in field_lower for word in ["finance", "stock", "investing", "trading", "money"]):
        return "WallStreetBets", "SPY", "stock investing"
    # Default General Niche
    else:
        return "business", "AAPL", business_field

# Route 1: The Home Page (GET request)
@app.route('/')
def home():
    return render_template('index.html')

# Route 2: The Live AI Strategy API (POST request)
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    
    # Extract fields sent from the frontend form
    business_field = data.get('niche', 'Sustainable Apparel').strip()
    core_problem = data.get('problem', 'Increasing customer acquisition costs.').strip()
    target_audience = data.get('audience', 'Gen Z females').strip()
    
    print(f"\n[API Analyze Initiated] Field: '{business_field}' | Problem: '{core_problem}' | Audience: '{target_audience}'")
    
    # 1. Resolve subreddits and ticker symbols
    subreddit, ticker, search_topic = resolve_niche_parameters(business_field)
    
    # 2. Run Scraping Engines (Social & Market)
    try:
        social_data = social_scraper.get_live_reddit_trends(subreddit, search_topic)
    except Exception as e:
        print(f" -> Social scraper failed: {e}")
        social_data = {"keywords": [], "hashtags": []}
        
    try:
        market_data = market_scraper.get_stock_data(ticker)
        news_data = market_scraper.get_live_news(search_topic)
    except Exception as e:
        print(f" -> Market scraper failed: {e}")
        market_data = {"symbol": ticker, "current_price": 100.0, "change": 0.0, "percent_change": 0.0}
        news_data = []

    # 3. Analyze Sentiment vectors
    try:
        news_titles = [article.get("title", "") for article in news_data]
        sentiment_scores = sentiment_analyst.analyze_financial_data(news_titles) if news_titles else []
    except Exception as e:
        print(f" -> Sentiment analyst failed: {e}")
        sentiment_scores = []

    # 4. Synthesize AI Strategy Playbook
    try:
        strategy_playbook = strategy_synthesizer.generate_growth_strategy(
            niche=business_field,
            topic=search_topic,
            problem=f"Struggling with target audience ({target_audience}). Core challenge: {core_problem}",
            reddit_data=social_data,
            market_data=market_data,
            news_sentiment=sentiment_scores
        )
    except Exception as e:
        print(f" -> Strategy synthesizer failed: {e}")
        strategy_playbook = strategy_synthesizer.get_mock_synthesizer_response(business_field, search_topic, core_problem)

    # 5. Respond with full payload
    response_payload = {
        "status": "success",
        "market": {
            "symbol": ticker,
            "current_price": market_data.get("current_price", 100.0),
            "change": market_data.get("change", 0.0),
            "percent_change": market_data.get("percent_change", 0.0),
            "prices": market_data.get("prices", []),
            "dates": market_data.get("dates", [])
        },
        "social": {
            "keywords": social_data.get("keywords", []),
            "hashtags": social_data.get("hashtags", [])
        },
        "strategy": strategy_playbook
    }
    
    return jsonify(response_payload)

# Route 3: The Submission Catcher (POST request fallback)
@app.route('/submit', methods=['POST'])
def submit():
    business_field = request.form.get('business_field')
    core_problem = request.form.get('core_problem')
    target_audience = request.form.get('target_audience')

    print(f"Field: {business_field}")
    print(f"Problem: {core_problem}")
    print(f"Audience: {target_audience}")

    return "Success! Check your terminal to see the captured data. (We will make a real results page later)."

# Run Flask server
if __name__ == '__main__':
    app.run(debug=True)

