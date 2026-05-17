import yfinance as yf
import json
import os

def fetch_stock_financials(symbols):
    print(f"Fetching Yahoo Finance data for symbols: {symbols}")
    financial_data = []
    
    if not symbols:
        return financial_data
        
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="5d")
            if not hist.empty:
                last_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else last_close
                change_pct = ((last_close - prev_close) / prev_close) * 100
                
                financial_data.append({
                    "symbol": sym,
                    "price": last_close,
                    "change_percent": change_pct,
                    "volume": int(hist['Volume'].iloc[-1])
                })
        except Exception as e:
            print(f"Failed to fetch data for {sym}: {e}")
            
    # Sort by volume to rank the hype mathematically
    financial_data.sort(key=lambda x: x.get('volume', 0), reverse=True)
    return financial_data

def fetch_yahoo_trending():
    print("Fetching Yahoo Finance general trending stocks...")
    try:
        # Since we are using standard yfinance, let's fetch data for typical major indices and active stocks
        # as a proxy for the general "Yahoo Trending" side table.
        symbols = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "AMZN", "META", "GOOGL", "SPY", "QQQ"]
        
        trending_data = fetch_stock_financials(symbols)
        
        os.makedirs("data", exist_ok=True)
        with open("data/yahoo_trending.json", "w") as f:
            json.dump(trending_data, f, indent=4)
        
        print(f"Saved Yahoo Finance data for {len(trending_data)} general trending stocks.")
        return trending_data
    except Exception as e:
        print(f"Error fetching Yahoo general data: {e}")
        return []

if __name__ == "__main__":
    fetch_yahoo_trending()
