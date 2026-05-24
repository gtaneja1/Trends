from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

print("Waking up the Analysts (This might take a minute the first time)...")

# load model
print("Loading Corporate Financial AI (FinBERT)...")
finance_model = pipeline("sentiment-analysis", model="ProsusAI/finbert")

print("Loading social media AI")
social_model = pipeline("sentiment-analysis", model = "cardiffnlp/twitter-roberta-base-sentiment-latest")

# analyze model / read data
def analyze_financial_data(text_list):
    print("reading financial data")
    return finance_model(text_list)

def analyze_social_media_data(text_list):
    print ("understanding social media sentiment")
    return social_model(text_list)

# test if module works 

if __name__ == "__main__":
    financial_texts = [
        "The company's quarterly earnings exceeded expectations, leading to a surge in stock price.",
        "The recent data breach has raised concerns about the company's cybersecurity measures.",
        "The new product launch has been met with positive reviews and strong sales."
    ]
    
    social_texts = [
        "I love the new features in this product! #excited",
        "This service is terrible, I'm never using it again. #disappointed",
        "Meh, it's okay. Not great but not bad either. #neutral"
    ]
    
    print("Financial Sentiment Analysis:")
    print(analyze_financial_data(financial_texts))
    
    print("\nSocial Media Sentiment Analysis:")
    print(analyze_social_media_data(social_texts))
    
    
    







