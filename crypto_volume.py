import pyupbit
import time

# data = pyupbit.get_ohlcv("KRW-BTC", interval="day")
all_tickers = pyupbit.get_tickers(fiat="KRW")
for ticker in all_tickers:
    current_ohlcv = pyupbit.get_ohlcv(ticker, count=1)
    time.sleep(0.3)
    print(f"{ticker} 현재가: {current_ohlcv})")

# print(all_krw_data)
# print(data)