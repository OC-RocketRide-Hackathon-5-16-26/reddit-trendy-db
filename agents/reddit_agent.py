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
                author = post.get('author', 'anonymous')
                
                combined_text += f"=== POST START ===\n"
                combined_text += f"Subreddit: r/{sub_name}\n"
                combined_text += f"Author: u/{author}\n"
                combined_text += f"Title: {title}\n"
                combined_text += f"Upvotes: {upvotes}\n"
                combined_text += f"Comments: {num_comments}\n"
                combined_text += f"Body:\n{selftext}\n"
                combined_text += f"=== POST END ===\n\n"
                    
        except Exception as e:
            print(f"Error fetching data from r/{sub_name}: {e}")
            
    # Save as a single combined text file (good for backup)
    file_path = os.path.join(output_dir, "reddit_data.txt")
    with open(file_path, "w") as f:
        f.write(combined_text)
        
    print(f"Saved local backup at {file_path}")
    
    # Upload the text file to the RocketRide Dropper via headless browser (Playwright)
    dropper_url = os.getenv("ROCKETRIDE_DROPPER_URL")
    dropper_key = os.getenv("ROCKETRIDE_DROPPER_KEY")
    
    if dropper_url and dropper_key:
        abs_file_path = os.path.abspath(file_path)
        auth_url = f"{dropper_url}?auth={dropper_key}"
        print(f"Uploading to RocketRide Dropper via browser: {auth_url}")
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(auth_url, wait_until="networkidle")
                # Find the file input in the dropper UI and upload the file
                file_input = await page.query_selector("input[type='file']")
                if file_input:
                    await file_input.set_input_files(abs_file_path)
                    print("File uploaded. Keeping browser open for 10 seconds to allow pipeline to process...")
                    await page.wait_for_timeout(10000)  # 10 seconds
                    print("Dropper upload complete via file input.")
                else:
                    # Try drag-and-drop simulation on the drop zone
                    await page.evaluate(f"""
                        const dt = new DataTransfer();
                        const file = new File([`placeholder`], 'reddit_data.txt', {{type: 'text/plain'}});
                        dt.items.add(file);
                        document.querySelector('[class*="drop"]')?.dispatchEvent(
                            new DragEvent('drop', {{dataTransfer: dt, bubbles: true}})
                        );
                    """)
                    await page.wait_for_timeout(3000)
                    print("Dropper upload attempted via drag-and-drop simulation.")
                await browser.close()
        except Exception as e:
            print(f"Error uploading to dropper via Playwright: {e}")
    else:
        print("No ROCKETRIDE_DROPPER_URL or ROCKETRIDE_DROPPER_KEY found in .env")

if __name__ == "__main__":
    asyncio.run(fetch_and_process_reddit())
