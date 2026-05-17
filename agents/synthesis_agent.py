import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Import the new dynamic fetch function from our yahoo agent
from agents.yahoo_agent import fetch_stock_financials

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3.1-flash-lite')

def load_yahoo_data():
    try:
        with open("data/yahoo_trending.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"No Yahoo data found: {e}")
        return []

def query_chroma_for_trends():
    # Try to read local file first to preserve authors and full posts
    try:
        file_path = "incoming_data/reddit_data.txt"
        if os.path.exists(file_path):
            print(f"Reading local backup from {file_path} to preserve authors...")
            with open(file_path, "r") as f:
                content = f.read()
            
            posts = content.split("=== POST START ===\n")
            parsed_posts = []
            for post in posts:
                if not post.strip(): continue
                
                import re
                author_match = re.search(r"Author: u/(.*)\n", post)
                title_match = re.search(r"Title: (.*)\n", post)
                upvotes_match = re.search(r"Upvotes: (\d+)", post)
                body_match = re.search(r"Body:\n([\s\S]*)=== POST END ===", post)
                
                author = author_match.group(1) if author_match else "anonymous"
                title = title_match.group(1) if title_match else ""
                upvotes = int(upvotes_match.group(1)) if upvotes_match else 0
                body = body_match.group(1).strip() if body_match else ""
                
                parsed_posts.append({
                    "author": author,
                    "text": body,
                    "title": title,
                    "upvotes": upvotes
                })
            
            print(f"Parsed {len(parsed_posts)} posts from local file.")
            return parsed_posts
    except Exception as e:
        print(f"Error reading local file: {e}")
        
    # Fallback to Chroma if file fails
    try:
        import chromadb
        print("Falling back to Chroma on port 8330...")
        client = chromadb.HttpClient(host='localhost', port=8330)
        col = client.get_collection('ROCKETRIDE')
        results = col.get(limit=50)
        
        documents = results.get("documents", [])
        print(f"Found {len(documents)} documents in Chroma.")
        
        return [{"text": doc, "author": "anonymous"} for doc in documents]
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
    
    import html
    import re
    # Extract raw text for easy substring matching
    raw_texts = []
    for doc in raw_documents:
        if isinstance(doc, dict):
            text = doc.get('text', '')
            title = doc.get('title', '')
            combined = (title + " " + text).strip()
            # Unescape HTML entities like &amp;
            combined = html.unescape(combined)
            # Remove markdown links [text](url) and just keep the text
            combined = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', combined)
            raw_texts.append(combined)
        elif isinstance(doc, str):
            raw_texts.append(html.unescape(doc.strip()))

    for line in lines:
        if "Section 3: Representative Quotes" in line or "## Representative Quotes" in line or "Section 3: Top Comments" in line or "## Top Comments" in line or "## Top Post Excerpts" in line:
            in_quotes_section = True
            new_lines.append(line)
            continue
            
        if in_quotes_section and (line.strip().startswith("-") or line.strip().startswith("[")):
            # Filter out (Stock: General) as requested by user
            if "*(Stock: General)*" in line or "(Stock: General)" in line:
                continue
                
            # This is likely a quote line
            import re
            # Try to find text between quotes first
            match = re.search(r'"([^"]*)"', line)
            if match:
                quote_text = match.group(1)
            else:
                quote_text = line.strip().lstrip("-").strip().strip('"').strip("'")
            
            # Normalize both for fuzzy matching (ignore punctuation, spacing, casing)
            def normalize(t):
                import re
                return re.sub(r'[^a-zA-Z0-9]', '', t).lower()
                
            norm_quote = normalize(quote_text)
            
            # Check if it exists in any raw text
            found = False
            for raw in raw_texts:
                if norm_quote in normalize(raw):
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
    
    # 1. Extract tickers and sentiment per post using Gemini
    try:
        extract_prompt = f"""
        Analyze these raw Reddit posts. For each post:
        1. Extract all stock ticker symbols mentioned.
        2. Determine the overall sentiment of the post (POSITIVE or NEGATIVE).
        
        Return ONLY a JSON list of objects, where each object corresponds to a post and has the format:
        [
          {{"post_index": 0, "tickers": ["AAPL", "NVDA"], "sentiment": "POSITIVE"}},
          {{"post_index": 1, "tickers": ["TSLA"], "sentiment": "NEGATIVE"}}
        ]
        
        The "post_index" should correspond to the index of the post in the input list.
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
        post_sentiments = json.loads(text)
    except Exception as e:
        print(f"Error extracting symbols and sentiment: {e}")
        post_sentiments = []

    # 2. Count mentions and upvotes in a single bucket
    symbol_stats = {}
    
    for item in post_sentiments:
        idx = item.get("post_index")
        tickers = item.get("tickers", [])
        
        if idx is not None and idx < len(reddit_data):
            post = reddit_data[idx]
            upvotes = post.get("upvotes", 0)
            if isinstance(upvotes, str):
                try: upvotes = int(upvotes)
                except: upvotes = 0
                
            for sym in tickers:
                if isinstance(sym, str) and sym.isalpha() and len(sym) <= 5:
                    sym = sym.upper()
                    if sym not in symbol_stats: symbol_stats[sym] = {"mentions": 0, "upvotes": 0}
                    symbol_stats[sym]["mentions"] += 1
                    symbol_stats[sym]["upvotes"] += upvotes

    # 3. Normalize and rank to pick top 5
    if symbol_stats:
        max_m = max(s["mentions"] for s in symbol_stats.values()) or 1
        min_m = min(s["mentions"] for s in symbol_stats.values())
        max_u = max(s["upvotes"] for s in symbol_stats.values()) or 1
        min_u = min(s["upvotes"] for s in symbol_stats.values())
        
        scored = []
        for sym, stats in symbol_stats.items():
            nm = (stats["mentions"] - min_m) / (max_m - min_m) if max_m != min_m else 1.0
            nu = (stats["upvotes"] - min_u) / (max_u - min_u) if max_u != min_u else 1.0
            scored.append((sym, nm + nu))
        trending_symbols = [s[0] for s in sorted(scored, key=lambda x: x[1], reverse=True)[:5]]
    else:
        trending_symbols = []
        
    print(f"Trending stocks selected: {trending_symbols}")
    
    # 4. Fetch financials for the selected symbols
    reddit_financials = fetch_stock_financials(trending_symbols)
    
    # 5. Prepare JSON dumps for the prompt
    reddit_summary = json.dumps(reddit_data, indent=2)
    reddit_financials_summary = json.dumps(reddit_financials, indent=2)
    
    trending_stats = {sym: symbol_stats[sym] for sym in trending_symbols if sym in symbol_stats}
    trending_stats_summary = json.dumps(trending_stats, indent=2)
    
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""
    You are a highly analytical financial AI. Generate a Daily Brief markdown document for today, {current_date}, based on the following data sources:
    
    1. **Raw Reddit Posts Data** (Contains titles, text, and engagement like upvotes/comments):
    {reddit_summary}
    
    2. **Real-time Financials for the Selected Stocks** (Actual market performance):
    {reddit_financials_summary}
    
    3. **Trending Stocks** (pre-selected: ranked by mentions+upvotes — use these exact counts in headings):
    {trending_stats_summary}
    
    Please synthesize a daily brief using EXACTLY these pre-selected stocks. Do NOT swap, replace, or re-rank stocks.
    
    ## Overall Trending Market Analysis
    - Provide a brief summary of the overall market sentiment and major themes discussed in the Reddit posts (1-2 paragraphs).
    
    - Write entries for the stocks listed in Data Source 3, in the order provided.
    
    For each of these 5 stocks, provide:
    - Ticker and Company Name with counts (e.g., `### 1. SPSC (SPS Commerce) [Mentions: X, Upvotes: Y]`).
    - **CRITICAL**: You MUST include the `[Mentions: X, Upvotes: Y]` part at the end of the heading line! You MUST use the exact counts from Data Source 3.
    - Confidence Score and Decision (e.g., `**Confidence Score: 4.8/5 (Buy)**`).
    - **Decision Rules**:
      - 4.0 to 5.0 -> Append `(Buy)`
      - 2.0 to 4.0 -> Append `(Hold)`
      - 0.0 to 2.0 -> Append `(Sell)`
    - **CRITICAL**: You MUST add a blank line after the Confidence Score line so that the performance line renders on its own line in markdown!
    - **Actual Market Performance**: You MUST use this exact format: `Price: $XX.XX, 1D %: +X.XX%` (or -X.XX%). Do NOT omit the "Price:" or "1D %:" labels! (You MUST use the values from Data Source 2. Do NOT hallucinate these values!).
    - **CRITICAL**: Add a blank line after the Performance line so the explanation renders as a new paragraph!
    - Explanation based on the results of the Reddit posts (why people are talking about it, what the consensus is).
    
    ## Top Post Excerpts
    - Extract EXACTLY 10 compelling, direct quotes from the Reddit posts related to the stocks above or general market sentiment. 
    - **CRITICAL**: You MUST provide EXACTLY 10 quotes. Outputting fewer than 10 (like 4 or 8) is a FAILURE. If you cannot find 10 perfect quotes, you MUST use the next best available ones from the data to reach exactly 10.
    - **Example of required output (You MUST provide exactly 10 lines like this)**:
      [POSITIVE] u/user1: "Text" *(Stock: TIC)* (10 upvotes)
      
      [POSITIVE] u/user2: "Text" *(Stock: TIC)* (20 upvotes)
      
      [POSITIVE] u/user3: "Text" *(Stock: TIC)* (30 upvotes)
      
      [POSITIVE] u/user4: "Text" *(Stock: TIC)* (40 upvotes)
      
      [POSITIVE] u/user5: "Text" *(Stock: TIC)* (50 upvotes)
      
      [NEGATIVE] u/user6: "Text" *(Stock: TIC)* (60 upvotes)
      
      [NEGATIVE] u/user7: "Text" *(Stock: TIC)* (70 upvotes)
      
      [NEGATIVE] u/user8: "Text" *(Stock: TIC)* (80 upvotes)
      
      [NEGATIVE] u/user9: "Text" *(Stock: TIC)* (90 upvotes)
      
      [NEGATIVE] u/user10: "Text" *(Stock: TIC)* (100 upvotes)
    - **Format**: Analyze the sentiment of the quote. If positive, start the line with `[POSITIVE]`. If negative, start the line with `[NEGATIVE]`.
    - **CRITICAL**: Do NOT use bullet points (asterisks `*`) at the start of the line! They must be plain lines starting directly with `[POSITIVE]` or `[NEGATIVE]`.
    - **CRITICAL**: You MUST add a blank line between each quote so that they render as separate paragraphs in markdown!
    - Full Format: `[POSITIVE] u/username: "Quote text" *(Stock: TICKER)* (N upvotes)` or `[NEGATIVE] u/username: "Quote text" *(Stock: TICKER)* (N upvotes)`
    - **Sorting**: Group all `[POSITIVE]` quotes at the top of the list, and all `[NEGATIVE]` quotes at the bottom of the list.
    - **CRITICAL**: You MUST include the exact upvote count from the data source at the very end of the line (e.g., `(479 upvotes)`). Do NOT hallucinate this number! If not available, use `(N/A upvotes)`.
    - **CRITICAL**: You MUST include the `*(Stock: TICKER)*` context at the end of the quote before the upvote count. If the quote is about general market sentiment and not a specific stock, use `*(Stock: General)*`. Do NOT omit this.
    - **CRITICAL**: These quotes MUST be exact matches from the 'Raw Reddit Posts Data' provided. Do NOT paraphrase, summarize, or create quotes. Do NOT use generic names like 'Reditor' or 'anonymous' if the author name is present in the data.







    
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
