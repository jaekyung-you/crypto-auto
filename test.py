
import pyupbit
import os
import requests
import pandas as pd
import pprint
from pathlib import Path

os.environ['UPBIT_ACCESS_KEY'] = "FyBmuspbffhOtOqXV5ezXLzkttE9E9oshADv8y7G"
os.environ['UPBIT_SECRET_KEY'] = "sRSFn95AxHFlegQdifJLhhKvA4axWBiuvnlAD9kf"

access = "FyBmuspbffhOtOqXV5ezXLzkttE9E9oshADv8y7G"          # 본인 값으로 변경
secret = "sRSFn95AxHFlegQdifJLhhKvA4axWBiuvnlAD9kf"          # 본인 값으로 변경

# print(pyupbit.get_tickers())

upbit = pyupbit.Upbit(access, secret) 

# print(upbit.get_balance("KRW-BTC"))
# print(upbit.get_balance("KRW"))


# 업비트 API1. 마켓 코드 조회
market_url = "https://api.upbit.com/v1/market/all"
param = {
    "isDetails": False 
}
market_response = requests.get(market_url, param)
data = market_response.json() 

tickers = pyupbit.get_tickers(fiat="KRW")
# print(tickers)

# krw_ticker = []
# for coin in data:
#     ticker = coin["market"]
#     if ticker.startswith("KRW"):
#         krw_ticker.append(ticker) 
 
# print(krw_ticker, len(krw_ ticker))

# 업비트 API2. 시세 캔들 조회(분봉)

candle_minute_url = "https://api.upbit.com/v1/candles/minutes/3?market=KRW-BTC&count=5" 
candle_resposne = requests.get(candle_minute_url)
# print(candle_resposne.json())

df = pyupbit.get_ohlcv("KRW-BTC", "minute3")
# print(df) 
# print(df['open'].resample('3T').max())

# 업비트 API3. 시세 캔들 조회(일봉)
candle_day_url = "https://api.upbit.com/v1/candles/days?market=KRW-BTC&count=1" 
candle_resposne1 = requests.get(candle_day_url)
# print(candle_resposne1.json())
df2 = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=5)
# print(df2)


# 업비트 API4. 시세 캔들 조회(월봉)
candle_month_url = "https://api.upbit.com/v1/candles/months?market=KRW-BTC&count=1" 
candle_resposne2 = requests.get(candle_month_url)
# print(candle_resposne1.json())

# value, volume과 같이 보기 어려운 경우
pd.options.display.float_format = "{:.1f}".format
df3 = pyupbit.get_ohlcv("KRW-BTC", interval="month", count=5)
# print(df3)


# 업비트 API5. 현재가 정보
tickers = ["KRW-BTC", "KRW-XRP"]
price = pyupbit.get_current_price(pyupbit.get_tickers(fiat="KRW"))
# print(price)
# for k, v in price.items():
#     print(k, v)


# 업비트 API6. 호가 정보(최대 5호까지 출력) ask - 매도, bid - 매수
order_list = pyupbit.get_orderbook("KRW-BTC")
# pprint.pprint(order_list)
# print("매도 호가 총합:", order_list["total_ask_size"])
# print("매수 호가 총합:", order_list["total_bid_size"])


# 업비트 API7. 로그인
data_folder = Path("/Users/jaekyungyou/project/cryptoauto/")
file_to_open = data_folder / "upbit_key.txt"

f = open(file_to_open)
lines = f.readlines()
access_key = lines[0].strip()
secret_key = lines[1].strip()
f.close()

upbit = pyupbit.Upbit(access_key, secret_key) # exchange API를 사용하려면 Upbit 객체를 생성해야함!
my_balance = upbit.get_balance("KRW")
# print(my_balance)


# 업비트 API7. 전체 계좌 조회 
balances = upbit.get_balances() 
# pprint.pprint(balances)


# 업비트 API8. 지정가 주문 buy_limit_order(티커, 주문가격, 주문량)
xrp_price = pyupbit.get_current_price("KRW-XRP")
# print("리플 가격:", xrp_price)
# buy_response = upbit.buy_limit_order("KRW-XRP" ,50, 100)
# pprint.pprint(buy_response)


# 업비트 API9. 지정가 주문 취소 buy_limit_order(티커, 주문가격, 주문량)
cancel_resposne = upbit.cancel_order(uuid="172c9812-36d6-4fd9-be98-c99f0619bbca")
# print(cancel_resposne)

# 업비트 API10. 지정가 매도 주문(티커, 주문가격, 주문량)
sei_balance = upbit.get_balance("KRW-SEI") # 몇 주 가지고 있는지
# print(sei_balance)
# sei_sell_resposne = upbit.sell_limit_order("KRW-SEI", 1000, sei_balance)
# print(sei_sell_resposne) 

# 업비트 API11. 시장가 매수/매도 주문(티커, 주문가격<원화>)
# ex. 주문가격<원화>1000원을 넣으면 200원짜리 주가 5개가 매수됨, 10000원어치 사고 싶다~~라는 뜻
# buy_market_order_response = upbit.buy_market_order("KRW-BTC", 10000)
# sell_market_order_response = upbit.sell_market_order("KRW-BTC", 10000)
# pprint.pprint(buy_market_order_response)
