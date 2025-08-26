from binance.client import Client 
import pandas as pd  
import os 
from dotenv import load_dotenv
from pathlib import Path
import time
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

if not API_KEY or not API_SECRET:
    raise EnvironmentError("API_KEY or API_SECRET not set.")

client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = "https://testnet.binance.vision/api"       # ! Make sure system time is correct
account = client.get_account()

def interval_to_ms(interval_str):
    return int(pd.to_timedelta(interval_str).total_seconds() * 1000) # pandas understands strings like "1h", "1m", "1d"

def download_klines_chunks(symbol, interval, start_dt, end_dt, out_csv,
                           limit=1000, pause=0.5, append=False):
    interval_ms = interval_to_ms(interval)
    start_ms = int(pd.to_datetime(start_dt).value // 10**6)  # ns -> ms
    end_ms = int(pd.to_datetime(end_dt).value // 10**6)

    all_dfs = []
    current_start = start_ms

    while current_start < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "limit": limit
        }
        r = requests.get("https://api.binance.com/api/v3/klines", params=params)
        r.raise_for_status()
        data = r.json()
        if not data:
            break

        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        numerics = ['open', 'high', 'low', 'close', 'volume']
        df[numerics] = df[numerics].apply(pd.to_numeric, axis=1)
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        all_dfs.append(df)

        # Advance to next candle after the last returned
        last_ts_ms = int(df['timestamp'].iloc[-1].value // 10**6)
        current_start = last_ts_ms + interval_ms

        # avoid spamming the API
        time.sleep(pause)

        # if returned fewer than limit, probably reached end range
        if len(data) < limit:
            break

    if not all_dfs:
        return pd.DataFrame(columns=['timestamp','open','high','low','close','volume'])

    result = pd.concat(all_dfs, ignore_index=True)

    # trim to requested end_dt and remove duplicates
    result = result[result['timestamp'] <= pd.to_datetime(end_dt)]
    result = result.drop_duplicates(subset=['timestamp']).reset_index(drop=True)

    # ensure output directory exists and write CSV (append or overwrite)
    out_path = Path(out_csv)
    # if provided a relative path, resolve relative to the notebook's cwd (notebooks folder)
    if not out_path.is_absolute():
        out_path = (Path.cwd() / out_path).resolve()

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # show the resolved absolute path so you know where file is written
    print("Writing CSV to:", out_path)

    if append:
        result.to_csv(out_path, mode='a', header=not out_path.exists(), index=False)
    else:
        result.to_csv(out_path, index=False)

    return result

# 2020 January 1 to 2024 December 31
start = pd.Timestamp("2020-01-01")
end   = pd.Timestamp("2024-12-31 23:59:59")

# save into project data/raw_data relative to the notebooks folder
out_file = Path('..') / 'data' / 'raw_data' / 'BTCUSDT_1h.csv'
print('Kernel cwd:', Path.cwd())
print('Resolved out_file:', (Path.cwd() / out_file).resolve())

# call downloader with the relative path 
df = download_klines_chunks('BTCUSDT', '1h', start, end, out_csv=str(out_file))
