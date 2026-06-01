import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize your exact Gemini client
# Note: Ensure your .env file has GEMINI_API_KEY=your_actual_api_key_here
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# MOCK DATA (Bypassing the scrapers and models for instant testing)
# ==========================================
niche = "indie video games"
keyword = "multiplayer RPG"
problem = "We launch in one month but have zero wishlists on Steam. No one knows our game exists."
detected_topic = "gaming"
detected_strategy = "community_led_growth"
market_details = "Symbol: SONY | Price: 85.50 | Trend: -2.4"
agg_social_label = "negative"
agg_social_score = 0.8
custom_blueprint = "- Leverage micro-influencers.\n- Create a viral waitlist.\n- Run Discord AMAs."

# ==========================================
# YOUR EXACT GEMINI PROMPT
# ==========================================
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

print("==================================================")
print(" FIRING UP GEMINI STRATEGY ENGINE")
print("==================================================")

try:
    print("Synthesizing customized strategic roadmap with Gemini...")
    
    # Run the exact Gemini 1.5 Pro call from your app.py
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=master_prompt
    )
    
    print("\n AI PIPELINE COMPLETE! Here is your generated playbook:\n")
    print("==================================================\n")
    
    # Print the raw markdown straight to your terminal screen
    print(response.text)
    
    print("\n==================================================")

except Exception as e:
    print(f"\n GEMINI ERROR: {e}")