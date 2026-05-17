import os
import json
import google.generativeai as genai
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Import the new dynamic fetch function from our yahoo agent
from agents.yahoo_agent import fetch_stock_financials

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def load_yahoo_data():
    try:
        with open("data/yahoo_trending.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"No Yahoo data found: {e}")
        return []

def query_qdrant_for_trends():
    try:
        client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        collection_name = "ROCKETRIDE" 
        
        records, _ = client.scroll(
            collection_name=collection_name,
            limit=50,
            with_payload=True
        )
        return [record.payload for record in records]
    except Exception as e:
        print(f"Error querying Qdrant: {e}")
        return []

def synthesize_brief(reddit_data, general_yahoo_data):
    print("Synthesizing daily brief with Gemini...")
    
    # 1. Extract unique symbols from the raw Reddit data using Gemini
    try:
        extract_prompt = f"""
        Analyze these raw Reddit posts and extract all stock ticker symbols mentioned.
        Return ONLY a JSON list of strings (e.g., ["AAPL", "TSLA", "NVDA"]).
        Do not include any other text, just the raw JSON list.
        
        Posts:
        {json.dumps([{"title": p.get("title"), "text": p.get("text")} for p in reddit_data])}
        """
        response = model.generate_content(extract_prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3]
        elif text.startswith('```'):
            text = text[3:-3]
        extracted_symbols = json.loads(text)
    except Exception as e:
        print(f"Error extracting symbols: {e}")
        extracted_symbols = []

    reddit_symbols = set()
    for sym in extracted_symbols:
        if isinstance(sym, str) and sym.isalpha() and len(sym) <= 5:
            reddit_symbols.add(sym.upper())
                
    # 2. Fetch real-time financials specifically for the Reddit symbols
    reddit_financials = fetch_stock_financials(list(reddit_symbols))
    
    # 3. Prepare JSON dumps for the prompt
    reddit_summary = json.dumps(reddit_data, indent=2)
    reddit_financials_summary = json.dumps(reddit_financials, indent=2)
    general_yahoo_summary = json.dumps(general_yahoo_data, indent=2)
    
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""
    You are a highly analytical financial AI. Generate a Daily Brief markdown document for today, {current_date}, based on the following three data sources:
    
    1. **Raw Reddit Posts Data** (Contains titles, text, and engagement like upvotes/comments):
    {reddit_summary}
    
    2. **Real-time Financials for the Reddit Stocks** (Actual market performance of the stocks being hyped):
    {reddit_financials_summary}
    
    3. **General Yahoo Finance Trending Data** (For a broader market comparison):
    {general_yahoo_summary}
    
    Please synthesize a daily brief that MUST include:
    - **A Header**: "Daily Brief - {current_date}"
    - **Reddit Trending Stocks Table**: A clean markdown table. You must calculate a "Hype Score" (0-10) for each stock based on the frequency of mentions in the Reddit data and the upvotes/comments. Include the ticker, your calculated Hype Score, determined Sentiment, and the actual market performance (price, change %) from Data Source 2.
    - **General Market Trends Table (On the Side)**: A separate markdown table showing the general Yahoo trending stocks from Data Source 3.
    - **Analysis & Insights**: Compare the Reddit buzz against the actual market movements. Is the hype justified?
    - **What's Angry vs Exciting**: Highlight negative sentiment vs positive sentiment based on the posts.
    - **Top Representative Quotes**: Extract compelling text directly from the Reddit posts.
    
    Format the output as a clean, highly aesthetic Markdown document. Use emojis and bold text for emphasis.
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
    except Exception as e:
        print(f"Error synthesizing brief: {e}")
        content = f"""# ⚠️ AI Synthesis Failed
        
The Gemini API key threw an error (`{e}`). However, here is the raw data that *would* have been synthesized:

## Reddit Hyped Stocks & Financials
```json
{reddit_financials_summary}
```

## General Market Trends
```json
{general_yahoo_summary}
```
"""

    os.makedirs("reports", exist_ok=True)
    report_path = "reports/daily_brief.md"
    with open(report_path, "w") as f:
        f.write(content)
    print(f"Daily brief generated successfully at {report_path}")

if __name__ == "__main__":
    y_data = load_yahoo_data()
    r_data = query_qdrant_for_trends()
    
    if not r_data:
        print("Injecting mock raw Reddit data for synthesis demonstration...")
        r_data = [
            {"title": "NVDA earnings gonna be wild", "text": "I'm putting my life savings on calls.", "upvotes": 1200, "num_comments": 400},
            {"title": "TSLA is bleeding", "text": "Can't believe the drop today. Totally irrational market.", "upvotes": 800, "num_comments": 300}
        ]
        
    synthesize_brief(r_data, y_data)
