import asyncio
import time
import os
from agents.reddit_agent import fetch_and_process_reddit
from agents.yahoo_agent import fetch_yahoo_trending
from agents.synthesis_agent import synthesize_brief, load_yahoo_data, query_qdrant_for_trends

async def run_ingestion():
    print("=== Phase 1: Ingestion ===")
    # Run Reddit ingestion and Yahoo fetch concurrently
    # The Reddit agent will push to the RocketRide webhook
    await asyncio.gather(
        fetch_and_process_reddit(),
        asyncio.to_thread(fetch_yahoo_trending)
    )
    print("=== Ingestion Complete ===\n")

def run_synthesis():
    print("=== Phase 2: Synthesis ===")
    # Give the RocketRide pipeline a moment to process embeddings into Qdrant
    print("Waiting for RocketRide pipeline to process embeddings...")
    time.sleep(5) 
    
    y_data = load_yahoo_data()
    r_data = query_qdrant_for_trends()
    
    if not r_data:
        print("Qdrant is empty. Fetching live Reddit data directly for synthesis...")
        import requests
        r_data = []
        headers = {'User-Agent': 'python:trendy_stocks_bot:v1.0'}
        try:
            # Fallback to fetching live data directly
            url = os.getenv("REDDIT_HOT_STOCKS", "https://www.reddit.com/r/stocks/.json")
            resp = requests.get(f"{url}?limit=10", headers=headers)
            if resp.status_code == 200:
                posts = resp.json().get('data', {}).get('children', [])
                for p in posts:
                    pdata = p.get('data', {})
                    r_data.append({
                        "title": pdata.get('title'),
                        "text": pdata.get('selftext'),
                        "upvotes": pdata.get('score'),
                        "num_comments": pdata.get('num_comments')
                    })
        except Exception as e:
            print(f"Error fetching live fallback data: {e}")
            
    synthesize_brief(r_data, y_data)
    print("=== Synthesis Complete ===")

async def main():
    print("Starting Reddit Trendy Stocks Pipeline...")
    await run_ingestion()
    run_synthesis()
    print("All tasks finished successfully. Check the reports/ directory.")

if __name__ == "__main__":
    asyncio.run(main())
