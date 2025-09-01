part of a 3 part series - idk maybe i'll put them all together
1. pricing strategies comparison
2. algorithmic signals from pricing strategies
3. risk management


### possibly a structure  
```
crypto-vol-forecast/  
├─ data/  
│  ├─ raw/               # raw CSVs  
│  └─ processed/           
├─ src/  
│  ├─ data_download/  
│  │  ├─ binance_klines.py  
│  │  └─ yfinance_download.py  
│  ├─ features/  
│  │  └─ build_features.py  
│  ├─ models/  
│  │  ├─ ts_arima_garch.py  
│  │  ├─ har_rv.py  
│  │  ├─ ml_xgboost.py  
│  │  └─ dl_lstm_tcn.py  
│  ├─ eval/  
│  │  ├─ metrics.py      # RMSE, QLIKE, DM test  
│  │  └─ backtest.py     # simple rules + risk overlay  
│  └─ utils/  
│     └─ timesplit.py  
├─ notebooks/  
│  ├─ 01_data_ingestion.ipynb  
│  ├─ ......  
└─ README.md  ```
