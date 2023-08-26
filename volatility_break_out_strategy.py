import pyupbit
import time
import datetime
import os
import requests
import numpy as np

os.environ['UPBIT_ACCESS_KEY'] = "FyBmuspbffhOtOqXV5ezXLzkttE9E9oshADv8y7G"
os.environ['UPBIT_SECRET_KEY'] = "sRSFn95AxHFlegQdifJLhhKvA4axWBiuvnlAD9kf"
os.environ['SLACK_BOT_TOKEN'] = "xoxb-5749189164226-5766390357650-jekmTWcZjf8U0PKeiNsXmfpX"

def post_message(text):
    """슬랙 메세지 전송"""
    # todo: 챗봇 꾸미기
    slack_bot_token = os.environ['SLACK_BOT_TOKEN']
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + slack_bot_token},
                             data = {"channel": "crypto", "text": text}
                             )
# 가장 좋은 k값 구하기
def get_ror(ticker, k=0.5):
    """변동성 돌파를 위해 이상적인 k값 구하기"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] - df['target'],
                         df['close'] / df['target'],
                         1)
    
    # 누적 곱에서 -2 인덱스?
    ror = df['ror'].cumprod()[-2]
    print("그 날의 ror", ror)
    return ror

def cal_target(ticker):
    """목표가 설정하기"""
    # 업비트 기준: 하루 거래일 9:00 ~ 익일 AM8:59
    df = pyupbit.get_ohlcv(ticker, "day")

    # print(df.tail()) // 최신 5개 데이터 추출
    yesterday = df.iloc[-2] # 어제 데이터.
    today = df.iloc[-1] # 오늘의 데이터. 행 번호로 가져오기 

    yesterday_range = yesterday['high'] - yesterday['low']
    ror = get_ror(ticker)
    target = today['open'] + (yesterday_range) * ror
    # print("목표가: ", target)
    return target

access = os.environ['UPBIT_ACCESS_KEY']
secret = os.environ['UPBIT_SECRET_KEY']
upbit = pyupbit.Upbit(access, secret)

# todo: 당일날 어떤 티커를 구매할건지, 1개 혹은 여러개 구매할건지 
# 기준: 1. 단타: 거래대금 2. 장타: 비트코인 & 이더리움 소량 매수
ticker = "KRW-BTC"
target = cal_target(ticker)
op_mode = False # 첫 날에는 사지 않는다. (현재가가 목표가보다 한 참 위에 있을 때 매수될 수 있기 때문)
hold = False # 현재 코인 보유 여부 
k = 0.1 # 잔고의 몇 퍼센트만큼 투자할건지 ex. 10퍼센트

while True:
    try:
        now = datetime.datetime.now()

        # 매도 시도 8:59:50~59
        if now.hour == 8 and now.minute == 59 and 50 <= now.second <= 59:
            if op_mode is True and hold is True:
                btc_balance = upbit.get_balance(ticker)
                upbit.sell_market_ordert(ticker, btc_balance)
                hold = False # 팔았으므로 보유 상태 False
                # todo: 얼마나 매도 했는지 슬랙 호출
            
            op_mode = False 

        # 9:00:20~30 사이에, 목표가 경신 (첫 거래까지 20초정도 기다림)
        # 다른 코인에는 좀 다르게 적용해야할 수도
        if now.hour == 9 and now.minute == 0 and (20 <= now.second <= 30):
            target = cal_target(ticker)
            op_mode = True 
            time.sleep(10) # 30초 이미 지나버려서 두 번 다시 안 돎  

        price = pyupbit.get_current_price(ticker)

        # 매 초마다 조건 확인 후, 매수 시도
        if op_mode is True and hold is False and price is not None and price >= target:
            krw_balance = upbit.get_balance("KRW") # 우선 원화 잔고 조회
            upbit.buy_market_order(ticker, krw_balance * k)
            hold = True  # 보유 상태를 True, 한 번 사면 더 이상 매수하지 않을 것
            # todo: 얼마나 매수 했는지 슬랙 호출

        # 1초마다 상태 출력중 -> 슬랙에 정해진 시간에 봇 출력하도록 혹은 매수/매도 진행했을 경우(특정 상황에 대해) 슬랙 메세지 쏘기
        # todo: 슬랙 쏘는 시간대 설정
        status = f"🔥 현재시간 : {now}, 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}"
        print(f"🔥 현재시간 : {now}, 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}")
        post_message(status)

        time.sleep(1)

    except Exception as e:
            error = f"❌에러 발생: {e}"
            print(error)
            post_message(error)
            time.sleep(1)