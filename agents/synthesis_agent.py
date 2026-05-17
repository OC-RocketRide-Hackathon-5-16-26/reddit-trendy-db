import os
import json
import google.generativeai as genai
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

def query_chroma_for_trends():
    try:
        import chromadb
        print("Querying Chroma on port 8330...")
        client = chromadb.HttpClient(host='localhost', port=8330)
        col = client.get_collection('ROCKETRIDE')
        results = col.get(limit=50)
        
        documents = results.get("documents", [])
        print(f"Found {len(documents)} documents in Chroma.")
        
        # Wrap the strings in a dict with 'text' so the rest of the code works
        return [{"text": doc} for doc in documents]
    except Exception as e:
        print(f"Error querying Chroma: {e}")
        return []

def verify_quotes(report_content, raw_documents):
    """
    Verifies that quotes in Section 3 exist in the raw documents.
    If not, removes them.
    """
    print("Verifying quotes against raw data...")
    lines = report_content.split('\n')
    new_lines = []
    in_quotes_section = False
    
    # Extract raw text for easy substring matching
    raw_texts = []
    for doc in raw_documents:
        if isinstance(doc, dict):
            text = doc.get('text', '')
            title = doc.get('title', '')
            raw_texts.append((title + " " + text).strip())
        elif isinstance(doc, str):
            raw_texts.append(doc.strip())

    for line in lines:
        if "Section 3: Representative Quotes" in line or "## Representative Quotes" in line:
            in_quotes_section = True
            new_lines.append(line)
            continue
            
        if in_quotes_section and line.strip().startswith("-"):
            # This is likely a quote line
            import re
            # Try to find text between quotes first
            match = re.search(r'"([^"]*)"', line)
            if match:
                quote_text = match.group(1)
            else:
                quote_text = line.strip().lstrip("-").strip().strip('"').strip("'")
            
            # Check if it exists in any raw text
            found = False
            for raw in raw_texts:
                if quote_text in raw:
                    found = True
                    break
            
            if found:
                new_lines.append(line)
            else:
                print(f"Removing hallucinated quote: {quote_text}")
                # We skip adding it to new_lines
        else:
            new_lines.append(line)
            
    return '\n'.join(new_lines)

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
    You are a highly analytical financial AI. Generate a Daily Brief markdown document for today, {current_date}, based on the following data sources:
    
    1. **Raw Reddit Posts Data** (Contains titles, text, and engagement like upvotes/comments):
    {reddit_summary}
    
    2. **Real-time Financials for the Reddit Stocks** (Actual market performance of the stocks being hyped):
    {reddit_financials_summary}
    
    Please synthesize a daily brief that contains ONLY the following information, separated into these sections: **Trending**, **Angry**, and **Representative Quotes**.
    
    **Section 1: Trending**
    - Focus on the **Top 3 Trending Stocks** on Reddit.
    - Ranked from highest confidence (out of 5) to 3rd highest confidence.
    
    **Section 2: Angry**
    - Focus on the **Bottom 3 "Trending Stocks"** (worst sentiment or lowest confidence among those mentioned).
    - Ranked from 3rd worst to absolute worst confidence.
    
    For each of these 6 stocks, provide:
    - Ticker and Company Name.
    - Confidence Score (on a scale of 0 to 5).
    - Explanation based on the results of the Reddit posts (why people are talking about it, what the consensus is).
    - **Actual Market Performance**: Price and change % (You MUST use the values from Data Source 2. Do NOT hallucinate these values!).
    
    **Section 3: Representative Quotes**
    - Extract a maximum of 10 compelling, direct quotes from the Reddit posts related to the stocks above or general market sentiment.
    - **Format**: Include the author in the format: `- u/author: "Quote text"`. If you cannot find the author's name in the text, use `- u/anonymous: "Quote text"`.
    - **CRITICAL**: These quotes MUST be exact matches from the 'Raw Reddit Posts Data' provided. Do NOT paraphrase, summarize, or create quotes.
    
    CRITICAL INSTRUCTIONS:
    - Do NOT include anything else! No general market tables, no separate analysis sections. Just these 3 sections.
    - Do NOT hallucinate answers! Rely ONLY on the provided data sources. If data is missing or insufficient, state it clearly.
    - Format the output as a clean, highly aesthetic Markdown document.
    - Do NOT use emojis anywhere in the document.
    - Avoid em-dashes (—). Use commas or parentheses instead.
    - Maintain professional, human-like prose throughout.
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        content = verify_quotes(content, reddit_data)
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
    r_data = query_chroma_for_trends()
    
    if not r_data:
        print("Injecting mock raw Reddit data for synthesis demonstration...")
        r_data = [
            {"title": "NVDA earnings gonna be wild", "text": "I'm putting my life savings on calls.", "upvotes": 1200, "num_comments": 400},
            {"title": "TSLA is bleeding", "text": "Can't believe the drop today. Totally irrational market.", "upvotes": 800, "num_comments": 300}
        ]
        
    synthesize_brief(r_data, y_data)
