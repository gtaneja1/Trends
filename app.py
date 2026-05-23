# ========================================================================
#   SALES + MARKETING FORECAST - BACKEND SERVER (app.py)
# ========================================================================
#   A Flask application serving front-end static assets and handling:
#   1. `/api/trends` - Sending current macro-economic indices & platform trend lists.
#   2. `/api/forecast` - Orchestrating the 5-step analysis pipeline via core_pipeline.py.
# ========================================================================

import os
from flask import Flask, render_template

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app) # Enable CORS for all routes (useful for development)

# --- 1. FRONTEND ROUTING ---

@app.route('/')
def index():
    """
    Serves the primary index.html dashboard file.
    """
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    """
    Serves other static assets (style.css, app.js, images, fonts).
    """
    return send_from_directory(app.static_folder, path)

# --- 2. API ENDPOINTS ---

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """
    GET endpoint: Gathers and returns current market indices and social platform interest scores.
    Simulates real-time values including:
    - Consumer Price Index (CPI) & Inflation Rates
    - Consumer Sentiment Index
    - Hashtag search volume indicators (TikTok, Instagram, YouTube)
    """
    # Call data retrieval modules in core_pipeline.py
    # Return structured JSON list of trends
    return jsonify({"status": "stub", "message": "Trends data API skeleton ready."})

@app.route('/api/forecast', methods=['POST'])
def run_forecast():
    """
    POST endpoint: Triggers the Sales & Marketing forecast pipeline.
    Expects request JSON body:
    {
        "brand_name": str,
        "entity_type": str,
        "platforms": list,
        "target_audience": str,
        "issue": str,
        "goals": str
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400
        
    # Steps:
    # 1. Parse and validate parameters
    # 2. Call core_pipeline.py to process trends and query Gemini API
    # 3. Handle key validation (e.g. check GEMINI_API_KEY)
    # 4. Return the structured forecast (Next Steps & Marketing Ideas)
    
    return jsonify({"status": "stub", "message": "Forecasting API skeleton ready."})

# --- 3. SERVER START ---

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Sales + Marketing Forecast app on http://127.0.0.1:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
