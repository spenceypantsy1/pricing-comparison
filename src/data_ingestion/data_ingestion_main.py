from data_ingestion_utils import MarketDataDownloader
from pathlib import Path

def main():
    # Initializing parameters for MarketDataDownloader class 
    start_date = "2023-01-01"
    end_date = "2025-01-01"
    interval = "1h"

    # Create an instance of your downloader with common params (without asset and ticker)
    downloader = MarketDataDownloader(interval=interval, lookback = "730D", start=None, end=None)

    # Project root and data directory
    project_root = Path(__file__).parents[2]  # parent of src/
    data_dir = project_root / 'data/raw_data'
    data_dir.mkdir(parents=True, exist_ok=True)  # make sure 'data/' exists
    
    # Define assets
    assets = [
        # Crypto
        {"asset": "Crypto", "ticker": "BTCUSDT", "save_path": data_dir / f"crypto_BTCUSDT_{interval}.csv"},
        {"asset": "Crypto", "ticker": "XRPUSDT", "save_path": data_dir / f"crypto_XRPUSDT_{interval}.csv"},
        
        # Stocks
        {"asset": "Stock", "ticker": "MSFT", "save_path": data_dir / f"stock_MSFT_{interval}.csv"},
        {"asset": "Stock", "ticker": "UPST", "save_path": data_dir / f"stock_UPST_{interval}.csv"},
        
        # Forex
        {"asset": "Forex", "ticker": "EUR/USD", "save_path": data_dir / f"forex_EURUSD_{interval}.csv"},  # high liquidity
        {"asset": "Forex", "ticker": "USD/ZAR", "save_path": data_dir / f"forex_USDZAR_{interval}.csv"},  # low liquidity
    ]

    # Fetch all assets in a loop
    for a in assets:
        print(f"Fetching {a['asset']} data for {a['ticker']}...")
        data = downloader.fetch(asset=a["asset"], ticker=a["ticker"], save_path=a["save_path"])


if __name__ == "__main__":
    main()
