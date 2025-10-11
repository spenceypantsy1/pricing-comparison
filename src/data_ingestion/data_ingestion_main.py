from data_ingestion_utils import MarketDataDownloader
from pathlib import Path

def main():
    # Initializing parameters for MarketDataDownloader class 
    start_date = "2022-01-01"
    end_date = "2025-01-01"
    interval = "1d"

    # Create an instance of your downloader with common params (without asset and ticker)
    downloader = MarketDataDownloader(interval=interval, start=start_date, end=end_date)

    # Project root and data directory
    project_root = Path(__file__).parent.parent  # parent of src/
    data_dir = project_root / 'data/raw_data'
    data_dir.mkdir(parents=True, exist_ok=True)  # make sure 'data/' exists
    
    # Paths for each asset data file
    crypto_path = data_dir / 'crypto_BTCUSDT.csv'
    forex_path = data_dir / 'forex_EURUSD.csv'
    stock_path = data_dir / 'stock_AAPL.csv'

    # Fetch Crypto data
    print("Fetching Crypto data...")
    crypto_data = downloader.fetch(asset='Crypto', ticker='BTCUSDT', save_path=crypto_path)
    
    # Fetch Forex data
    print("Fetching Forex data...")
    forex_data = downloader.fetch(asset='Forex', ticker='EUR/USD', save_path=forex_path)

    # Fetch Stock data
    print("Fetching Stock data...")
    stock_data = downloader.fetch(asset='Stock', ticker='AAPL', save_path=stock_path)

if __name__ == "__main__":
    main()
