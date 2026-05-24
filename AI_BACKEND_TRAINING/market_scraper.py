import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Import yfinance. If not fully installed yet in background, we handle import dynamically or import it here
try:
    import yfinance as yf
except ImportError:
    yf = None

print("Waking up the Market Scraper...")

# ==========================================
# 1. THE STOCK DATA ENGINE (yfinance)
# ==========================================
def get_stock_data(ticker_symbol):
    """
    Fetches stock history and current metrics for a given ticker symbol.
    Returns a dictionary of closing prices and percent changes.
    """
    print(f"Fetching stock data for ticker: {ticker_symbol.upper()}...")

    # ensure we can assign to the module-level yf variable if needed
    global yf

    if yf not in globals() or yf is None:
        try:
            import yfinance as temp_yf
            yf = temp_yf
        except ImportError:
            print(" [WARNING] yfinance is not installed yet. Returning mock stock data for development.")
            return get_mock_stock_data(ticker_symbol)

    try:
        ticker = yf.Ticker(ticker_symbol)
        # Fetch 1 month of daily stock history
        hist = ticker.history(period="1mo", interval="1d")
        
        if hist.empty:
            print(f" [WARNING] No stock history found for {ticker_symbol}. Returning empty dataset.")
            return {}

        # Format history data for Chart.js
        dates = [date.strftime("%b %d") for date in hist.index]
        prices = [round(float(price), 2) for price in hist['Close']]
        
        # Calculate key metrics
        current_price = prices[-1]
        previous_price = prices[0]
        price_change = round(current_price - previous_price, 2)
        pct_change = round((price_change / previous_price) * 100, 2)
        
        return {
            "symbol": ticker_symbol.upper(),
            "current_price": current_price,
            "change": price_change,
            "percent_change": pct_change,
            "dates": dates,
            "prices": prices,
            "source": "yfinance"
        }
        
    except Exception as e:
        print(f" [ERROR] Could not fetch data from yfinance: {e}")
        return get_mock_stock_data(ticker_symbol)

def get_mock_stock_data(ticker_symbol):
    """
    Backup mock generator if yfinance fails to load or connect.
    """
    print(f"Generating fallback mock stock data for {ticker_symbol.upper()}...")
    import random
    base_prices = {"NKE": 98.5, "AAPL": 175.2, "MSFT": 415.0, "TSLA": 178.4, "AMZN": 180.1}
    base = base_prices.get(ticker_symbol.upper(), 50.0)
    
    prices = []
    dates = []
    current_val = base
    for i in range(15):
        current_val = round(current_val * (1 + random.uniform(-0.02, 0.025)), 2)
        prices.append(current_val)
        dates.append(f"Day {i+1}")
        
    change = round(prices[-1] - prices[0], 2)
    pct = round((change / prices[0]) * 100, 2)
    
    return {
        "symbol": ticker_symbol.upper(),
        "current_price": prices[-1],
        "change": change,
        "percent_change": pct,
        "dates": dates,
        "prices": prices,
        "source": "mock"
    }

# ==========================================
# 2. THE NEWS SEARCH ENGINE (RSS / NewsAPI)
# ==========================================
def get_live_news(query, news_api_key=None):
    """
    Fetches recent news articles using NewsAPI if a key is provided,
    otherwise falls back to parsing Google News RSS feed for the query.
    Requires no API keys by default!
    """
    if news_api_key:
        return get_news_from_api(query, news_api_key)
    else:
        return get_news_from_rss(query)

def get_news_from_rss(query):
    """
    Parses Google News RSS XML feed to extract titles, links, sources, and dates.
    Very stable and requires no registration/keys.
    """
    print(f"Scraping live public news feed for '{query}' via Google News RSS...")
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    # Fake our browser identity so we don't get blocked
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        articles = []
        
        # Parse the XML elements
        for item in root.findall('.//item')[:10]:
            title = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
            source_el = item.find('source')
            source = source_el.text if source_el is not None else "Google News"
            
            # Clean up the title (Google News titles are often 'Article Title - Source Name')
            clean_title = title
            if " - " in title:
                parts = title.split(" - ")
                # Strip off the last part if it matches the source name
                if parts[-1].strip().lower() in source.lower() or source.lower() in parts[-1].strip().lower():
                    clean_title = " - ".join(parts[:-1]).strip()
                    
            # Parse publication date to a simpler format
            try:
                dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                formatted_date = dt.strftime("%b %d, %Y")
            except Exception:
                formatted_date = pub_date_str
                
            articles.append({
                "title": clean_title,
                "link": link,
                "published": formatted_date,
                "source": source
            })
            
        return articles
        
    except Exception as e:
        print(f" [ERROR] Could not parse Google News RSS: {e}")
        return []

def get_news_from_api(query, api_key):
    """
    Alternative news retrieval using official NewsAPI.org.
    """
    print(f"Fetching official NewsAPI articles for '{query}'...")
    encoded_query = urllib.parse.quote(query)
    url = f"https://newsapi.org/v2/everything?q={encoded_query}&sortBy=publishedAt&pageSize=10&apiKey={api_key}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        articles = []
        if data.get("status") == "ok":
            for item in data.get("articles", []):
                pub_date_str = item.get("publishedAt", "")
                try:
                    dt = datetime.strptime(pub_date_str, "%Y-%m-%dT%H:%M:%SZ")
                    formatted_date = dt.strftime("%b %d, %Y")
                except Exception:
                    formatted_date = pub_date_str
                    
                articles.append({
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "published": formatted_date,
                    "source": item.get("source", {}).get("name", "NewsAPI")
                })
        return articles
        
    except Exception as e:
        print(f" [WARNING] NewsAPI error: {e}. Falling back to Google News RSS.")
        return get_news_from_rss(query)

# ==========================================
# 3. LIVE TEST COMMAND
# ==========================================
if __name__ == "__main__":
    # Test market scraper
    stock_info = get_stock_data("NKE")
    print("\nStock Info Returned:")
    print(f"Symbol: {stock_info.get('symbol')}")
    print(f"Current Price: ${stock_info.get('current_price')}")
    print(f"Price Change: ${stock_info.get('change')} ({stock_info.get('percent_change')}%)")
    print(f"Data Points: {len(stock_info.get('prices', []))} days retrieved.\n")
    
    # Test news scraper
    news_items = get_live_news("Nike apparel sales")
    print("News Headlines Found:")
    for idx, art in enumerate(news_items[:3], 1):
        print(f"{idx}. {art['title']} [{art['source']}] ({art['published']})")
