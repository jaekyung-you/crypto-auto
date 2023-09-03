import pyupbit
import time
import pandas
import datetime
import os
from openpyxl import load_workbook

# ------------------------------------
# RSI: 상승 압력 / 하강 압력 * 100 -> 100에 가까울수룩 상승 압력이 크므로 매수세가 강함
# 70% 이상이면 과매도, 30% 이하 과매수 판단 
# 최근 RSI 가중치를 위해
# 최초 RSI - AU: 지난 14일간 상승분 합 / 14, AD: 지난 14일간 하락분 합 / 14
# 이후 RSI - AU: (이전 13일간 상승분 합 + 현재 상승분) / 14, AD: (이전 13일간 하락분 합 + 현재 하락분) / 14
# ------------------------------------

# data = pyupbit.get_ohlcv("KRW-BTC", interval="minute5")
# all_tickers = pyupbit.get_tickers(fiat="KRW")
# for ticker in all_tickers:
#     current_ohlcv = pyupbit.get_ohlcv(ticker, count=1)
#     time.sleep(0.3)
#     if current_ohlcv is None:
#         print("왜 none이지")
#     else:
#         print(f"{ticker} 현재가: {current_ohlcv})")

# print(all_krw_data)
# print(data)


os.environ['UPBIT_ACCESS_KEY'] = "FyBmuspbffhOtOqXV5ezXLzkttE9E9oshADv8y7G"
os.environ['UPBIT_SECRET_KEY'] = "sRSFn95AxHFlegQdifJLhhKvA4axWBiuvnlAD9kf"

upbit = pyupbit.Upbit(os.environ['UPBIT_ACCESS_KEY'],os.environ['UPBIT_SECRET_KEY'])

def buy(ticker):
     money = upbit.get_balance("KRW") # 보유 원화 조회

     # 보유량이 많을수록 적절히 분배
     if money < 20000:
         res = upbit.buy_market_order(ticker, money)
     elif money < 50000:
         res = upbit.buy_market_order(ticker, money * 0.4)
     elif money < 100000:
          res = upbit.buy_market_order(ticker, money * 0.3)
     else:
        res = upbit.buy_market_order(ticker, money * 0.2)
     return

def sell(ticker):
     # 보유 코인 & 현재 코인 시세 조회
     amount = upbit.get_balance(ticker)
     cur_price = pyupbit.get_current_price(ticker)
     total = amount * cur_price

     # 보유량이 많을수록 적절히 분배
     if total < 20000:
         res = upbit.buy_market_order(ticker, amount)
     elif total < 50000:
         res = upbit.buy_market_order(ticker, amount * 0.4)
     elif total < 100000:
          res = upbit.buy_market_order(ticker, amount * 0.3)
     else:
        res = upbit.buy_market_order(ticker, amount * 0.2)
     return

def rsi(ohlc: pandas.DataFrame, period: int = 14):
    delta = ohlc["close"].diff()  # 당일 종가가 전일 종가와 비교해서 얼마나 상승/하락했는지 default는 period=1
    ups, downs = delta.copy(), delta.copy()
    
    # diff = 전일 종가 - 당일 종가 가 음수이면, 상승한 것
    ups[ups < 0 ] = 0
    downs[downs > 0] = 0

    period = 14

    # 최근 것에 가중치를 주는데, 이를 '지수 이동 평균(exponential moving avg)'
    # pandas 모듈에서 지수 이동 평균을 구해주는 함수는 ewm 함수
    # 최근 13일 동안 상승분 하락분 

    # com: 비율을 얼마나 감소시킬지 1/(1 + com) 의 비율로 반영하므로 period - 1 만큼
    # min_periods: 값을 갖기 위해 최소 얼마만큼의 관측 개수가 있어야 하는지

    AU = ups.ewm(com = period - 1, min_periods= period).mean()
    AD = downs.abs().ewm(com = period - 1, min_periods= period).mean()

    RS = AU / AD

    return pandas.Series(100 - (100 / (1 + RS)), name= "RSI")


# def record(trade, diff):
#      """엑셀에 기록할거면 xlsx 필요"""
#      wb = load_workbook('')

# todo: 거래대금 높으면서, 많이 언급되는 캐시 위주 -> 추후 거래대금 위주로 변경하기 
ticker_list = ["KRW-BTC", "KRW-XRP", "KRW-ETC", "KRW-ETH", "KRW-BCH", "KRW-GRS"]
lower28 = []
higher70 = []

while True:
        # ticker = "KRW-XRP"
        # data = pyupbit.get_ohlcv(ticker=ticker, interval="minute5")
        # now_rsi = rsi(data, 14).iloc[-1] # 뒤에서 첫 번째 요소 반환
        # print(datetime.datetime.now(), now_rsi)
        # time.sleep(1)

        # todo: ticker_list에서 변동성이 크고 거래대금이 큰 코인들 5종목 정도 추출
        print(f"현재시간: {datetime.datetime.now()}\n")

        for i in range(len(ticker_list)):
            # 28이하, 70이상 각 코인에 대한 정보 초기화
            lower28.append(False)
            higher70.append(False)
            data = pyupbit.get_ohlcv(ticker=ticker_list[i], interval="minute3")
            now_rsi = rsi(data, 14).iloc[-1]
            
            print(f"코인명: {ticker_list[i]}\nRSI: {now_rsi}\n")

            if now_rsi <= 28:
                 lower28[i] = True

            elif now_rsi >= 33 and lower28[i] == True:
                 # 28이하에서 33으로 반등했을 때, 매수
                 buy(ticker_list[i])
                 lower28[i] = False
                 
            elif now_rsi >= 70 and higher70[i] == False:
                 # 70이상에 아직 매도하지 않았다면, 매도
                 sell(ticker_list[i])
                 higher70[i] = True

            elif now_rsi <= 60:
                 # RSI가 적어도 60까지 내려갔다가 다시 올라오는 경우에 매도
                 higher70[i] = False

        time.sleep(0.5)