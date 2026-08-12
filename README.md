# NeuroStrat | Strategic Forecast

**Calculate your next move using real-time macro-economic data.**

NeuroStrat is an AI-powered growth strategy dashboard that combines live market data, social sentiment, and neural classification models to generate actionable strategic briefings for your business niche.

---

## Preview

### Forecast Hub — Strategy Parameters
Enter your business niche, core problem, and target audience to initialize the AI strategy engine.

![Strategy Parameters Dashboard](https://github.com/user-attachments/assets/80152942-78df-49cd-9a50-b9313a9795d6)

### Strategic Briefing — AI-Generated Playbook
After analysis, receive a formatted executive summary with sector classification, social sentiment, and a phase-by-phase growth roadmap.

![Strategic Briefing Output](https://github.com/user-attachments/assets/999bf6e5-9bba-4a9b-bae2-4ae6-e378d162)

### Full Dashboard View
Live market charts, telemetry metadata, and export-ready strategic dossiers.

![Full Dashboard](https://github.com/user-attachments/assets/602f97d2-946e-4d27-a34f-a2e2d5317a8c)

---

## Features

- **Dual-model cascade engine** — classifies industry sector and operational strategy framework from your problem statement
- **Live data ingestion** — Reddit trends, stock/market data, and Google News headlines
- **Sentiment analysis** — aggregates social and financial sentiment scores
- **Gemini-powered synthesis** — generates a customized growth playbook
- **Interactive UI** — glitch-style dashboard with live charts and exportable briefings

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | Flask, Python |
| AI / ML | TensorFlow (Keras), Google Gemini API |
| Data | Reddit API, yfinance, Google News RSS, Hugging Face sentiment models |

---

## Prerequisites

- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- Pre-trained model files in `AI_BACKEND_TRAINING/`:
  - `saved_general_topic_model.keras`
  - `saved_routing_model.keras`

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/gtaneja1/Trends.git
cd Trends
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install tensorflow pandas numpy yfinance matplotlib transformers torch
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
FLASK_DEBUG=False
```

> **Note:** Never commit your `.env` file. It is already listed in `.gitignore`.

---

## How to Run

1. Open a terminal in the `Trends` folder
2. Activate your virtual environment
3. Start the Flask server:

```bash
python app.py
```

4. Wait for the startup message (model loading can take 30–60 seconds):

```
Running on http://127.0.0.1:5000
```

5. Open your browser and go to:

```
http://127.0.0.1:5000
```

> **Important:** Always access the app through the Flask server URL above. Do not open `index.html` directly in the browser — the API will not work without the backend running.

---

## How to Use

1. Fill in **Strategy Parameters**:
   - **Business Field / Niche** — e.g. `Real Estate Books`
   - **Core Problem to Solve** — describe your main challenge
   - **Target Audience** — e.g. `People above 50`

2. Click **Initialize AI Strategy**

3. Wait while the pipeline runs (scraping, sentiment analysis, model classification, Gemini synthesis)

4. Review your **Strategic Briefing**:
   - Telemetry bar (sector, social sentiment, sync status)
   - Executive summary with formatted headings and bullet points
   - **Export Dossier** to print or save as PDF

5. Click **Run New Analysis** to start over

---

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the dashboard UI |
| `/api/health` | GET | Health check — returns `{ "status": "ok" }` |
| `/api/analyze` | POST | Runs the full analysis pipeline |

**Example request:**

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "niche": "Real Estate Books",
    "keyword": "People above 50",
    "subreddit": "entrepreneur",
    "ticker": "SPY",
    "problem": "Need to grow sales with a limited marketing budget."
  }'
```

---

## Project Structure

```
Trends/
├── app.py                      # Flask server & analysis pipeline
├── templates/
│   └── index.html              # Dashboard UI
├── static/
│   └── style.css               # Styles
├── AI_BACKEND_TRAINING/
│   ├── social_scraper.py       # Reddit trend scraping
│   ├── market_scraper.py       # Stock & news data
│   ├── sentiment_analyst.py    # Sentiment models
│   ├── saved_general_topic_model.keras
│   └── saved_routing_model.keras
├── requirements.txt
├── .env                        # API keys (not committed)
└── README.md
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **Server offline / disconnected** | Make sure `python app.py` is running and you are on `http://127.0.0.1:5000` |
| **Slow startup** | Normal — TensorFlow models take time to load on first run |
| **Missing API key** | Add `GEMINI_API_KEY` to your `.env` file |
| **Reddit 403 errors** | The app falls back to mock social data automatically |

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Author

[gtaneja1](https://github.com/gtaneja1)
