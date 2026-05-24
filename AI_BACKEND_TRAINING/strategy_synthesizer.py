import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

print("Waking up the Strategy Synthesizer Module...")

# Dynamic detection of Google Gemini SDK versions (new google-genai vs. legacy google-generativeai)
genai_client = None
genai_legacy_model = None
api_key = os.getenv("GEMINI_API_KEY")

try:
    # Attempting to load the new SDK (google-genai)
    from google import genai
    # Ensure it's the new SDK module and has Client class
    if hasattr(genai, "Client"):
        if api_key:
            genai_client = genai.Client(api_key=api_key)
            print(" -> Google GenAI New SDK loaded successfully.")
    else:
        # It's not the new SDK module
        raise ImportError
except (ImportError, Exception):
    # Attempt to load the legacy SDK (google-generativeai)
    try:
        import google.generativeai as legacy_genai
        if api_key:
            legacy_genai.configure(api_key=api_key)
            genai_legacy_model = legacy_genai
            print(" -> Google GenerativeAI Legacy SDK loaded and configured successfully.")
    except ImportError:
        print(" [WARNING] No Google Gemini SDK could be loaded. Ensure 'google-genai' or 'google-generativeai' is installed.")

if not api_key:
    print(" [WARNING] GEMINI_API_KEY not found in environment variables. Set it in .env for live AI synthesis!")

def generate_growth_strategy(niche, topic, problem, reddit_data, market_data, news_sentiment):
    """
    Consolidates market metrics, social trends, and business problems,
    queries Gemini, and parses a highly detailed, structured sales & marketing JSON playbook.
    """
    global api_key, genai_client, genai_legacy_model
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            # Configure on the fly if key was just added
            try:
                from google import genai
                if hasattr(genai, "Client"):
                    genai_client = genai.Client(api_key=api_key)
                else:
                    raise ImportError
            except (ImportError, Exception):
                try:
                    import google.generativeai as legacy_genai
                    legacy_genai.configure(api_key=api_key)
                    genai_legacy_model = legacy_genai
                except ImportError:
                    pass

    # 1. PREPARE THE CONTEXT PAYLOAD FOR GEMINI
    reddit_keywords_str = ", ".join([f"{kw} (used {count}x)" for kw, count in reddit_data.get("keywords", [])])
    reddit_hashtags_str = ", ".join([f"{tag} ({count}x)" for tag, count in reddit_data.get("hashtags", [])])
    
    stock_change_str = "Unavailable"
    if market_data and "percent_change" in market_data:
        stock_change_str = f"${market_data['current_price']} (Change: {market_data['change']} / {market_data['percent_change']}%)"
        
    news_titles = []
    for idx, art in enumerate(reddit_data.get("news", []) or market_data.get("news", []) or []):
        sentiment_label = news_sentiment[idx]["label"] if idx < len(news_sentiment) else "neutral"
        news_titles.append(f"- '{art['title']}' [{art['source']}] (Sentiment: {sentiment_label.upper()})")
    
    news_str = "\n".join(news_titles) if news_titles else "No recent news headlines scraped."
    
    prompt = f"""
You are an elite Chief Marketing Officer (CMO), Growth Hacker, and financial business strategist. Your goal is to solve a user's critical business problem using real-time social trend data, competitor financial performance, and news sentiments.

### BUSINESS CONTEXT
- **Niche/Industry**: {niche}
- **Target Search Query/Topic**: {topic}
- **Specific Business Problem**: {problem}

### REAL-TIME DATA COLLECTED
1. **Competitor/Market Stock Ticker ({market_data.get('symbol', 'N/A')})**: {stock_change_str}
2. **Online Forum Keyword Volume**: {reddit_keywords_str}
3. **Public Discussion & Social Hashtags**: {reddit_hashtags_str}
4. **Live Industry News & Sentiment**:
{news_str}

---

### YOUR INSTRUCTIONS
Synthesize these inputs and output a highly actionable growth strategy.

CRITICAL COMPLIANCE RULE: Do not explicitly mention 'Reddit' anywhere in your analysis, strategies, copywriting, or generated content. Instead, refer to it as 'public social forums', 'online communities', 'social discussion feeds', or 'social keyword metrics'.
You must return your output strictly in JSON format. Do not add any conversational text or formatting outside of JSON. 

Your JSON structure MUST look EXACTLY like this:
{{
  "niche_insights": "A 2-3 sentence strategic analysis of the current market conditions. Mention what the competitor's stock price or the news indicates, and how the social trends represent an opportunity.",
  "sentiment_overview": "A 1-2 sentence overview of the collective customer sentiment (social media vibes vs news sentiment). Is there hype, skepticism, or unmet demands?",
  "next_steps": [
    {{
      "id": 1,
      "title": "Actionable Sales or Product Strategy",
      "impact": "High",
      "difficulty": "Easy",
      "description": "Provide a concrete 2-3 sentence execution plan detailing how the user can implement this and why it directly counters their problem (e.g. competitor actions or quality issues)."
    }},
    {{
      "id": 2,
      "title": "Actionable Sales or Product Strategy",
      "impact": "High",
      "difficulty": "Medium",
      "description": "Provide another concrete execution plan."
    }},
    {{
      "id": 3,
      "title": "Actionable Sales or Product Strategy",
      "impact": "Medium",
      "difficulty": "Hard",
      "description": "Provide another concrete execution plan."
    }}
  ],
  "marketing_ideas": {{
    "content_hooks": [
      {{
        "hook": "TikTok/Reels overlay text hook designed to grab attention in 1 second",
        "caption": "Instagram/TikTok description with engaging copywriting and popular hashtags like those in the data.",
        "audio_suggestion": "Recommend a trending audio or type of sound to pair with this video."
      }},
      {{
        "hook": "Another high-engaging video hook",
        "caption": "Engaging caption",
        "audio_suggestion": "Sound recommendation"
      }}
    ],
    "ad_copy": [
      {{
        "headline": "High-CTR advertising headline highlighting the user's competitive edge",
        "body": "Emotional and persuasive primary ad body copy addressing customer pain points.",
        "cta": "Shop Now / Learn More"
      }},
      {{
        "headline": "Alternative Benefit-focused Ad Headline",
        "body": "Alternative ad copy body.",
        "cta": "Get Started"
      }}
    ],
    "messaging_guide": {{
      "phrases_to_use": [
        "Key marketing phrase highlighting quality, origin, or specific benefit",
        "Another key phrase or value prop"
      ],
      "phrases_to_avoid": [
        "Banned words or clichés that turn customers off",
        "Another phrase to avoid"
      ]
    }}
  }}
}}
"""

    if not api_key or (genai_client is None and genai_legacy_model is None):
        print(" [WARNING] Running in MOCK API MODE because GEMINI_API_KEY is not configured or SDK failed to load.")
        return get_mock_synthesizer_response(niche, topic, problem)

    response_text = ""
    # Try multiple standard model names to handle key tier / version variances gracefully
    model_candidates = ["gemini-2.5-flash", "gemini-1.5-flash"]
    api_success = False
    last_error = None

    for model_name in model_candidates:
        try:
            if genai_client is not None:
                # Use new google-genai SDK
                print(f" -> Trying live strategy synthesis with {model_name} (New SDK)...")
                response = genai_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                response_text = response.text
                api_success = True
                break
            else:
                # Use legacy google-generativeai SDK
                print(f" -> Trying live strategy synthesis with {model_name} (Legacy SDK)...")
                model = genai_legacy_model.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                response_text = response.text
                api_success = True
                break
        except Exception as e:
            last_error = e
            print(f"    [WARNING] Model {model_name} failed or not supported: {e}")

    if not api_success:
        print(f" [ERROR] Gemini API failed for all model candidates. Last error: {last_error}. Falling back to mock strategy.")
        return get_mock_synthesizer_response(niche, topic, problem)

    try:
        # Parse JSON
        result_json = json.loads(response_text.strip())
        return result_json
        
    except Exception as e:
        print(f" [ERROR] Failed to parse Gemini response: {e}. Attempting manual JSON extraction or fallback.")
        try:
            # Fallback regex extraction if there are markdown blocks
            if response_text:
                clean_text = response_text.strip()
            elif 'response' in locals() and hasattr(response, 'text'):
                clean_text = response.text.strip()
            else:
                clean_text = ""
                
            match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as ex:
            print(f" [ERROR] Regex extraction also failed: {ex}")
        return get_mock_synthesizer_response(niche, topic, problem)

def get_mock_synthesizer_response(niche, topic, problem):
    """
    Returns a beautifully pre-formatted mock strategy response.
    Ensures the UI functions perfectly for demonstration if the API key is not configured.
    """
    print("Generating fallback mock strategy guide...")
    
    # Customize mock data slightly based on inputs
    fallback_niche = niche.upper()
    fallback_topic = topic.capitalize()
    
    return {
        "niche_insights": f"The market for {fallback_niche} shows a heavy shift towards authentic, high-quality manufacturing as social sentiment moves away from low-cost plastic options. Competitor stock movements indicate retail pressure, but strong social interest in #{topic.lower()} reveals a major direct-to-consumer opening.",
        "sentiment_overview": f"Social media feeds indicate high interest in '{topic}', but customers complain about cheap polyester blends. Keywords reveal a massive, unaddressed demand for heavy-weight, durable goods.",
        "next_steps": [
            {
                "id": 1,
                "title": "Launch a Premium 'Heavyweight' Limited Line",
                "impact": "High",
                "difficulty": "Medium",
                "description": f"Directly counter cheaper competitors by introducing a limited run focusing on premium materials. Leverage the high social forum interest for #{topic.lower()} to position this as the ultimate enthusiast product."
            },
            {
                "id": 2,
                "title": "Transparent Cost-Per-Wear Breakdown",
                "impact": "High",
                "difficulty": "Easy",
                "description": "Create a simple infographic comparing your product's lifespan against cheaper competitors. Demonstrate that paying 1.5x more upfront saves 3x money over the year, targeting the specific consumer fatigue regarding low quality."
            },
            {
                "id": 3,
                "title": "Micro-Influencer Seeding Campaign",
                "impact": "Medium",
                "difficulty": "Hard",
                "description": f"Send free samples to top community accounts. Leverage the organic interest to generate high-resolution user-created content (UCC) emphasizing tactile details, stitching, and fit."
            }
        ],
        "marketing_ideas": {
            "content_hooks": [
                {
                    "hook": f"Stop buying cheap {topic.lower()}. Here's why it's ruining your outfit...",
                    "caption": f"Are you tired of jackets that shrink after one wash? We took #{topic.lower()} and rebuilt it from the ground up using double-ply knit fabrics. Durable. Structured. Aesthetic. Link in bio to shop. #streetstyle #ootd #thrifted #streetwear",
                    "audio_suggestion": "Lo-Fi Vintage Vinyl Loop (Slowed) - 98 Trend Score"
                },
                {
                    "hook": "The fabric test competitors don't want you to see...",
                    "caption": f"We compared our custom knit against the fast-fashion giants. See the weight and structure difference for yourself. Quality isn't expensive, it's an investment. #{topic.lower()} #streetwearfits #grwm",
                    "audio_suggestion": "Heavy Phonk - Street Drip Mix - 95 Trend Score"
                }
            ],
            "ad_copy": [
                {
                    "headline": "Buy it Once. Wear it Forever.",
                    "body": f"Cheap competitor jackets look good on the rack, but lose their structure in weeks. Our custom #{topic.lower()} is built with heavy-weight fabric designed to hold its shape for years. Experience the difference.",
                    "cta": "Shop Premium Collection"
                },
                {
                    "headline": "Ditch the Polyester. Feel the Weight.",
                    "body": "Tired of paying for brand logos printed on low-grade synthetic plastics? Our materials are organically sourced, carefully double-stitched, and custom-tailored for maximum daily comfort.",
                    "cta": "Get 15% Off Your First Order"
                }
            ],
            "messaging_guide": {
                "phrases_to_use": [
                    "Heavy-weight structure",
                    "Organically sourced fibers",
                    "Durable daily wear",
                    "Built to outlast trends"
                ],
                "phrases_to_avoid": [
                    "Fastest shipping",
                    "Cheapest on the market",
                    "Basic essential styles",
                    "Just another hoodie"
                ]
            }
        }
    }

if __name__ == "__main__":
    # Test generator with mock credentials
    test_reddit = {
        "keywords": [("quality", 28), ("fit", 21), ("vintage", 19)],
        "hashtags": [("#ootd", 42), ("#streetstyle", 38)]
    }
    test_market = {
        "symbol": "NKE",
        "current_price": 98.5,
        "change": 1.25,
        "percent_change": 1.28
    }
    test_news_sent = [{"label": "positive", "score": 0.8}, {"label": "negative", "score": 0.7}]
    
    strategy = generate_growth_strategy(
        niche="streetwear apparel",
        topic="corduroy jacket",
        problem="Sales are slowing down because competitors sell cheap polyester jackets at half the price.",
        reddit_data=test_reddit,
        market_data=test_market,
        news_sentiment=test_news_sent
    )
    
    print("\n--- Strategy Synthesis Output ---")
    print(json.dumps(strategy, indent=2))
