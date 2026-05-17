import os
import json
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def fetch_and_process_reddit():
    print("Starting Reddit Agent (Dropper Mode)...")
    limit = 20 # Limit to 20 posts for this prototype
    
    output_dir = "incoming_data"
    os.makedirs(output_dir, exist_ok=True)
    
    headers = {
        'User-Agent': os.getenv('REDDIT_USER_AGENT', 'python:trendy_stocks_bot:v1.0 (by /u/yourusername)')
    }
    
    endpoints = {
        "stocks": os.getenv("REDDIT_HOT_STOCKS"),
        "wallstreetbets": os.getenv("REDDIT_HOT_WSB")
    }
    
    combined_text = ""
    for sub_name, base_url in endpoints.items():
        if not base_url:
            print(f"Skipping {sub_name}, URL not found in .env")
            continue
            
        print(f"Fetching from r/{sub_name}...")
        url = f"{base_url}?limit={limit}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            posts = data.get('data', {}).get('children', [])
            
            for post_obj in posts:
                post = post_obj.get('data', {})
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                upvotes = post.get('score', 0)
                num_comments = post.get('num_comments', 0)
                
                combined_text += f"=== POST START ===\n"
                combined_text += f"Subreddit: r/{sub_name}\n"
                combined_text += f"Title: {title}\n"
                combined_text += f"Upvotes: {upvotes}\n"
                combined_text += f"Comments: {num_comments}\n"
                combined_text += f"Body:\n{selftext}\n"
                combined_text += f"=== POST END ===\n\n"
                    
        except Exception as e:
            print(f"Error fetching data from r/{sub_name}: {e}")
            
    # Save as a single combined text file in the dropper directory
    file_path = os.path.join(output_dir, "reddit_data.txt")
    with open(file_path, "w") as f:
        f.write(combined_text)
        
    print(f"Successfully dropped combined file at {file_path}")

if __name__ == "__main__":
    asyncio.run(fetch_and_process_reddit())
