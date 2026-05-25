import os
import warnings
warnings.filterwarnings("ignore")

# Caches for lazy loaded models
_finance_model = None
_social_model = None
_transformers_error = False

print("Waking up the Sentiment Analyst Module...")

# Check environment toggle. Default to False for faster development startup unless explicitly enabled.
USE_LOCAL_TRANSFORMERS = os.getenv("USE_LOCAL_TRANSFORMERS", "false").lower() == "true"

def _load_models():
    """
    Lazy-loads the transformers models only when requested to prevent server-load blocking.
    """
    global _finance_model, _social_model, _transformers_error
    if _transformers_error or not USE_LOCAL_TRANSFORMERS:
        return False
        
    if _finance_model is not None and _social_model is not None:
        return True

    print("\n[AI Model Initialization] Loading transformers pipelines (This might take a minute the first time)...")
    try:
        from transformers import pipeline
        
        if _finance_model is None:
            print(" -> Loading Corporate Financial AI (FinBERT)...")
            _finance_model = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            
        if _social_model is None:
            print(" -> Loading Social Media AI (RoBERTa)...")
            _social_model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            
        print("[AI Model Initialization] Successfully loaded FinBERT and RoBERTa.\n")
        return True
    except Exception as e:
        print(f"\n[AI Model Initialization WARNING] Could not load local transformers: {e}")
        print(" -> Switching Sentiment Analyst to high-efficiency API/Lexical fallback mode.\n")
        _transformers_error = True
        return False

# ==========================================
# 1. FINANCIAL SENTIMENT PIPELINE
# ==========================================
def analyze_financial_data(text_list):
    """
    Analyzes list of financial texts.
    Returns: List of dicts with 'label' (positive, negative, neutral) and 'score'.
    """
    print(f"Reading financial data for sentiment ({len(text_list)} items)...")
    
    if _load_models():
        try:
            results = _finance_model(text_list)
            # FinBERT returns labels like 'positive', 'negative', 'neutral'
            return [{"label": res["label"].lower(), "score": round(res["score"], 4)} for res in results]
        except Exception as e:
            print(f" [WARNING] FinBERT inference failed: {e}. Using fallback.")
            
    # API/Lexical Fallback
    return [lexical_sentiment_score(text, mode="finance") for text in text_list]

# ==========================================
# 2. SOCIAL MEDIA SENTIMENT PIPELINE
# ==========================================
def analyze_social_media_data(text_list):
    """
    Analyzes list of social texts.
    Returns: List of dicts with 'label' (positive, negative, neutral) and 'score'.
    """
    print(f"Understanding social media sentiment ({len(text_list)} items)...")
    
    if _load_models():
        try:
            results = _social_model(text_list)
            # RoBERTa returns labels like 'positive', 'neutral', 'negative'
            # Map common label variations
            label_map = {
                "positive": "positive", "neutral": "neutral", "negative": "negative",
                "LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"
            }
            return [{"label": label_map.get(res["label"], "neutral"), "score": round(res["score"], 4)} for res in results]
        except Exception as e:
            print(f" [WARNING] RoBERTa inference failed: {e}. Using fallback.")
            
    # API/Lexical Fallback
    return [lexical_sentiment_score(text, mode="social") for text in text_list]

# ==========================================
# 3. HIGH-EFFICIENCY LEXICAL FALLBACK ENGINE
# ==========================================
def lexical_sentiment_score(text, mode="social"):
    """
    Extremely fast rule-based lexicon sentiment analyzer that runs in microseconds.
    Perfect fallback for servers running on low-resource environments.
    """
    text_lower = text.lower()
    
    # Financial word catalogs
    fin_pos = {"growth", "profit", "succeed", "exceed", "bull", "surge", "higher", "gain", "dividend", "positive", "strong", "beat"}
    fin_neg = {"loss", "deficit", "decline", "bear", "drop", "warn", "inflation", "concern", "breach", "weak", "miss", "lower", "slow"}
    
    # General/Social word catalogs
    soc_pos = {"love", "like", "great", "awesome", "excited", "amazing", "happy", "best", "perfect", "cool", "clean", "beautiful"}
    soc_neg = {"terrible", "bad", "disappointed", "hate", "worst", "broken", "awful", "useless", "slow", "cheap", "expensive", "ruin"}
    
    pos_words = fin_pos if mode == "finance" else soc_pos
    neg_words = fin_neg if mode == "finance" else soc_neg
    
    # Count occurrences
    pos_count = sum(1 for word in pos_words if word in text_lower)
    neg_count = sum(1 for word in neg_words if word in text_lower)
    
    if pos_count > neg_count:
        score = 0.6 + (0.05 * min(5, pos_count - neg_count))
        return {"label": "positive", "score": round(score, 2)}
    elif neg_count > pos_count:
        score = 0.6 + (0.05 * min(5, neg_count - pos_count))
        return {"label": "negative", "score": round(score, 2)}
    else:
        return {"label": "neutral", "score": 0.5}

# ==========================================
# 4. MODULE TEST RUNNER
# ==========================================
if __name__ == "__main__":
    # Test texts
    financial_texts = [
        "The company's quarterly earnings exceeded expectations, leading to a surge in stock price.",
        "The recent data breach has raised concerns about the company's cybersecurity measures.",
        "The brand is expanding into new retail stores in Europe."
    ]
    
    social_texts = [
        "I love the new features in this product! #excited",
        "This service is terrible, I'm never using it again. #disappointed",
        "It was okay. Nothing write home about."
    ]
    
    print("\n--- Running Financial Sentiment ---")
    print(analyze_financial_data(financial_texts))
    
    print("\n--- Running Social Sentiment ---")
    print(analyze_social_media_data(social_texts))
