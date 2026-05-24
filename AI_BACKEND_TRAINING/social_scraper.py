import urllib.request
import json
import matplotlib.pyplot as plt
from collections import Counter
import re
from datetime import datetime

print("Waking up the Social Scraper (Raw Data Mode)...")

# ==========================================
# 1. THE SCRAPER ENGINE (Public URL Method)
# ==========================================
def get_live_reddit_trends(subreddit_name, search_query):
    print(f"Scanning live public feed of r/{subreddit_name} for '{search_query}'...")
    
    # Reddit exposes a public JSON endpoint for every search. No API keys required.
    url = f"https://www.reddit.com/r/{subreddit_name}/search.json?q={search_query}&sort=hot&limit=25"
    
    # Fake our browser identity so Reddit doesn't block the request
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        # Hit the live internet
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        text_data = ""
        # Loop through the public posts returned in the JSON payload
        for post in data['data']['children']:
            post_data = post['data']
            text_data += f"{post_data['title']} {post_data['selftext']} "
            
        # Clean the text (only keep actual words, ignore punctuation/emojis)
        words = re.findall(r'\b[a-z]{4,}\b', text_data.lower())
        
        # Filter out boring grammar words so they don't ruin our chart
        stop_words = {"this", "that", "with", "they", "your", "what", "have", "from", "where", "about", "just", "like", "when", "there", "some", "more"}
        meaningful_words = [w for w in words if w not in stop_words]
        
        # Count the top 5 most used words exactly as they appear
        word_counts = Counter(meaningful_words).most_common(5)
        return word_counts
        
    except Exception as e:
        print(f" Could not connect to Reddit: {e}")
        return []

# ==========================================
# 2. THE VISUALIZER (Matplotlib)
# ==========================================
def plot_trend_chart(word_counts, topic):
    if not word_counts:
        print(" No data found to plot. Try a different search term.")
        return

    # Split the words and their exact counts for the graph
    words = [item[0] for item in word_counts]
    counts = [item[1] for item in word_counts]

    # Build the High-Res Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # A professional blue color gradient based on the number of words found
    colors = ['#2C5282', '#3182CE', '#4299E1', '#63B3ED', '#90CDF4'][:len(words)]
    
    bars = ax.bar(words, counts, color=colors, edgecolor='black', linewidth=0.5)

    # Add the exact number on top of every bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), 
                    textcoords="offset points",
                    ha='center', va='bottom', 
                    fontweight='bold', fontsize=12, color='#2D3748')

    # Professional Typography and Spacing
    ax.set_title(f"Live Keyword Mentions: '{topic.upper()}'", fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel("Trending Keywords", fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel("Exact Mentions (Last 24h)", fontsize=12, fontweight='bold', labelpad=10)
    
    # Remove clunky borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#A0AEC0')
    ax.spines['bottom'].set_color('#A0AEC0')
    
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Add a Timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    plt.figtext(0.99, 0.02, f"Raw Data Pulled: {current_time}", 
                horizontalalignment='right', fontsize=9, color='gray', style='italic')

    plt.tight_layout()
    plt.savefig("live_social_trend_chart.png", dpi=300)
    print(" Success! High-res chart saved as 'live_social_trend_chart.png'.")
    
    plt.show()

# ==========================================
# 3. THE LIVE RUN
# ==========================================
if __name__ == "__main__":
    # Change these variables to whatever you want to search!
    business_topic = "corduroy"
    target_subreddit = "streetwear"
    
    # 1. Scrape the raw data
    top_words = get_live_reddit_trends(target_subreddit, business_topic)
    
    # 2. Draw the chart
    plot_trend_chart(top_words, business_topic)