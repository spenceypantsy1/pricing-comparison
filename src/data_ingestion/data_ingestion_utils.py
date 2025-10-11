import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta

from binance.client import Client
import yfinance as yf 

from pathlib import Path
from dotenv import load_dotenv


"""
I'm still in between having the asset and ticker as part of the class or as part of the fetch method.
Having them as part of the class makes it easier to manage state, but having them as part of the fetch method makes it easier to use the same instance to fetch multiple assets.
For now, I'll keep them as part of the fetch method.
"""


class MarketDataDownloader:
    """
    Class to download historical market data.
    Args:
    - asset: 'Crypto', 'Stock', or 'Forex'
    - ticker: Ticker symbol (e.g., 'BTCUSDT', 'AAPL', 'EURUSD')
    - interval: Data interval (e.g., '1m', '5m', '1h', '1d')
    - lookback: Lookback period (e.g., '1d', '7d', '1m', '1y')
    """

    def __init__(
            self,
            # asset: str,
            # ticker: str,
            interval = '1d',
            lookback = None,
            start = None,
            end = None):
        
        # self.asset = asset
        # self.ticker = ticker
        self.interval = interval

        # Initializing lookback from NOW or a fixed time
        if lookback:
            self.lookback = lookback
            self.start_dt, self.end_dt = self._parse_lookback(self.lookback)
        elif start and end:
            self.start_dt = pd.to_datetime(start)
            self.end_dt = pd.to_datetime(end)
        else:
            raise ValueError('Either lookback or both start and end must be provided')

        # # Initializing asset class and tickers
        # if self.asset is None:
        #     raise ValueError('Asset must be "Crypto", "Stock", or "Forex"')
        # if self.ticker is None:
        #     raise ValueError('Ticker must be provided')
        
        # Initializing interval mapping for Binance or YF
        
        

    def _parse_lookback(self, lookback):
        """
        Converts lookback strings understood by pandas
        (e.g., '1d', '7d', '1m', '1y') into milliseconds
        """
        now = pd.Timestamp.now()                    # TODO check if this is able to do local tz
        if isinstance(lookback, str):
            delta = pd.to_timedelta(lookback)
            start = now - delta
        else:
            raise ValueError('Lookback must be a string like "1d", "7d", "1m", "1y"')
        return start, now


    def _interval_to_ms(self, interval): 
        """
        Converts a pandas-compatible interval string to milliseconds.
        """
        return int(pd.to_timedelta(interval).total_seconds() * 1000)
    

    def _map_interval(self, asset, interval):
        """
        Maps a generic interval string to the specific format required by YF or Binance.
        This method is called in the fetch method after asset and interval are set!!
        """
        interval_map = {
            '1m': {'binance': '1m', 'yahoo': '1m'},
            '5m': {'binance': '5m', 'yahoo': '5m'},
            '15m': {'binance': '15m', 'yahoo': '15m'},
            '30m': {'binance': '30m', 'yahoo': '30m'},
            '1h': {'binance': '1h', 'yahoo': '1h'},
            '2h': {'binance': '2h', 'yahoo': None},
            '4h': {'binance': '4h', 'yahoo': None},
            '1d': {'binance': '1d', 'yahoo': '1d'},
            '1wk': {'binance': '1w', 'yahoo': '1wk'},
            '1mo': {'binance': '1M', 'yahoo': '1mo'}
        }

        if interval not in interval_map:
            raise ValueError(f"Interval {interval} not supported.")
        
        if asset.lower() == 'crypto':
            mapped = interval_map[interval]['binance']
        else:  # stock or forex
            mapped = interval_map[interval]['yahoo']

        if mapped is None:
            raise ValueError(f"Interval '{interval}' is not supported for asset type '{asset_type}'")

        return mapped


    def fetch(
            self, 
            save_path: str = None,
            asset: str = None,
            ticker: str = None):
        """
        Main fetching method for respective asset class.
        It calls the respective fetch methods.
        Args:
        - save_path: Optional path to save the fetched data as CSV.
        - asset: 'Crypto', 'Stock', or 'Forex'
        - ticker: Ticker symbol (e.g., 'BTCUSDT', 'AAPL', 'EUR/USD')
        """
        self.asset = asset
        self.ticker = ticker

        self.interval = self._map_interval(self.asset, self.interval)
        
        if self.asset.lower() == 'crypto':
            data = self._fetch_crypto()
        elif self.asset.lower() == 'stock':
            data = self._fetch_stock()
        elif self.asset.lower() == 'forex':
            data = self._fetch_forex()
        else:
            raise ValueError('Asset must be "Crypto", "Stock", or "Forex"')

        self.data = data

        if save_path:
            self.data.to_csv(save_path)
            print("Data saved to", save_path)
        else:
            print("No save path provided, data will not be saved to disk.")

        print(f"Fetched {len(data)} rows of data.")
        return data


    def _fetch_crypto(self):
        """
        Method to fetch crypto data from Binance.
        Binance API limits to 1000 data points per request, so we need to roll over multiple requests
        """
        interval_ms = self._interval_to_ms(self.interval)
        start_ms = int(self.start_dt.value // 10**6)
        end_ms = int(self.end_dt.value // 10**6)
        current_start = start_ms
        all_dfs = []
        limit = 1000        # Binance max limit, if premium account maybe we can change this later

        while current_start < end_ms:
            params = {
                'symbol': self.ticker, 
                'interval': self.interval,
                'startTime': current_start,
                'limit': limit
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

            # Avoid spamming the API
            time.sleep(0.5)

            # If returned fewer than limit, probably reached end range
            if len(data) < limit:
                break

        if not all_dfs:
            return pd.DataFrame(columns=['timestamp','open','high','low','close','volume'])
        
        result = pd.concat(all_dfs, ignore_index=True)
        result = result[result['timestamp'] <= pd.to_datetime(self.end_dt)]
        result = result.drop_duplicates(subset=['timestamp']).reset_index(drop=True)
        return result


    def _fetch_stock(self):
        df = yf.download(self.ticker, start=self.start_dt, end=self.end_dt, interval=self.interval)
        if df.empty:
            print("No data fetched from Yahoo Finance.")
            return df
        df = df.reset_index()
        df.rename(columns = {
            'Date': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace = True)
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        return df
    
    def _fetch_forex(self):
        self.ticker = self.ticker.replace('/', '') + "=X"
        return self._fetch_stock() # Can use YF to fetch Forex as well