import time
import datetime
import pyupbit
import os
import requests

os.environ['UPBIT_ACCESS_KEY'] = "FyBmuspbffhOtOqXV5ezXLzkttE9E9oshADv8y7G"
os.environ['UPBIT_SECRET_KEY'] = "sRSFn95AxHFlegQdifJLhhKvA4axWBiuvnlAD9kf"
os.environ['SLACK_BOT_TOKEN'] = "xoxb-5749189164226-5766390357650-jekmTWcZjf8U0PKeiNsXmfpX"

def post_message(text):
    """슬랙 메세지 전송"""
    slack_bot_token = os.environ['SLACK_BOT_TOKEN']
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer "+ slack_bot_token},
                             data = {"channel": "crypto", "text": text}
                             )


def get_target_price(ticker, k):
    """
    변동성 돌파 전략으로 매수 목표가 조회
    """
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2) # 0: 어제, 1: 오늘
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """
    시작 시간 조회
    """
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    # print(start_time)
    return start_time

def get_ma15(ticker):
    """
    변동성 돌파 + 상승장 투자 전략, 15일 이동 평균선 조회
    이동평균선 정해놓고 그 이상으로 올라갔을 때 매수
    """
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    print(df['close'].rolling(15))
    return ma15

def get_balance(ticker):
    """
    잔고 조회
    """
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
        return 0
    
def get_current_price(ticker):
    """
    현재가 조회
    """
    return pyupbit.get_current_price(ticker)['orderbook_units'][0]['ask_price']

# post_message1(os.environ['SLACK_BOT_TOKEN'], "crypto", "하이")
post_message("auto_trade!!")

# 로그인
upbit = pyupbit.Upbit(os.environ['UPBIT_ACCESS_KEY'], os.environ['UPBIT_SECRET_KEY'])
print("🔥auto trade start")
target_ticker = "KRW-BTC"
# print(get_target_price(target_ticker, 0.5))
# print(get_ma15(target_ticker))


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(target_ticker)
        end_time = start_time + datetime.timedelta(days=1)
    
#         if start_time < now < end_time - datetime.timedelta(seconds=10):
#             target_price = get_target_price(target_ticker, 0.5)
#             current_price = get_current_price(target_ticker)
#             ma15 = get_ma15(target_ticker)

#             # 목표치를 넘어섰다면,  잔고 조회해서 최소 5천원 이상이라면 매수
#             if target_price < current_price and ma15 < current_price:
#                 krw = get_balance(target_ticker)
#                 if krw > 5000:
#                     upbit.buy_market_order(target_ticker, krw * 0.9995) # 수수료 제외
            

#             # 해당 시간대 아닌 10초간 전량 매도
#             else:
#                 btc = get_balance(target_ticker)
#                 if btc > 0.00008:
#                     upbit.sell_market_order(target_ticker, btc * 0.9995)

#             time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)


