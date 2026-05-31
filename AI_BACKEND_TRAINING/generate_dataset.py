import pandas as pd
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os
 
load_dotenv()  # Load environment variables from .env file

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# We use 1.5 Flash because it is incredibly fast and cheap for bulk data generation
model = genai.GenerativeModel('gemini-2.5-flash')

print(" Waking up Synthetic Dataset Factory...")

# These are the exact categories and blueprints we established for your engine
frameworks = {
    "influencer_marketing": "Framework: Creator-Led Growth. Guidelines: Focus on micro-influencer tiers,product integration, and audience trust. KPIs: CPA, Engagement Rate.",
    "organic_content_growth": "Framework: Algorithmic Retention Loops. Guidelines: Hook viewers in 3 seconds, syndicate across TikTok/Reels/Shorts. KPIs: View Duration, Follower Conversion.",
    "paid_performance_marketing": "Framework: Creative Testing Funnels. Guidelines: Use UGC for ad creative, aggressive retargeting. KPIs: ROAS, CPC."
}

dataset_rows = []

for category, blueprint in frameworks.items():
    print(f" Generating synthetic training data for: {category.upper()}...")
    
    prompt = f"""
    You are helping me build a machine learning text classification dataset.
    The category label is: "{category}"
    
    Generate 15 completely unique, realistic sentences that a user might type into a chat interface if they wanted help with this specific marketing category.
    Vary the tone (some professional, some casual, some frantic).
    
    Return the response as a strict JSON array of strings.
    Example: ["How do I get more views on TikTok?", "Need a brand deal strategy for skincare."]
    """
    
    # Force the model to return clean JSON so our script doesn't break
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    
    try:
        # Parse the JSON string array back into a Python list
        synthetic_prompts = json.loads(response.text)
        
        # Append each generated prompt to our dataset list alongside its category and blueprint
        for text in synthetic_prompts:
            dataset_rows.append({
                "text_input": text,
                "category_label": category,
                "strategic_blueprint": blueprint
            })
    except Exception as e:
        print(f"Error parsing JSON for {category}: {e}")

# Convert our list of dictionaries into a Pandas DataFrame
df = pd.DataFrame(dataset_rows)

# Save it to a CSV file!
csv_filename = "marketing_strategy_dataset.csv"
df.to_csv(csv_filename, index=False)

print(f"\nSUCCESS! Dataset generated and saved as '{csv_filename}'.")
print(f"Total Training Examples created: {len(df)}")