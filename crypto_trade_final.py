import pyupbit
import time
import pandas
import datetime
import os
import requests
import numpy as np
from pprint import pprint

os.environ['UPBIT_ACCESS_KEY'] = "FyBmuspbffhOtOqXV5ezXLzkttE9E9oshADv8y7G"
os.environ['UPBIT_SECRET_KEY'] = "sRSFn95AxHFlegQdifJLhhKvA4axWBiuvnlAD9kf"
os.environ['SLACK_BOT_TOKEN'] = "xoxb-5749189164226-5766390357650-jekmTWcZjf8U0PKeiNsXmfpX"


def post_message(text):
    """슬랙 메세지 전송"""
    slack_bot_token = os.environ['SLACK_BOT_TOKEN']
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " +
                                      slack_bot_token},
                             data={"channel": "crypto",
                                   "text": text,
                                   "username": "자동화 챗봇",
                                   "icon_emoji": ":robot_face:"}
                             )
    print(text)


def buy(ticker):
    money = upbit.get_balance("KRW")  # 보유 원화 조회

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
    # 당일 종가가 전일 종가와 비교해서 얼마나 상승/하락했는지 default는 period=1
    delta = ohlc["close"].diff()
    ups, downs = delta.copy(), delta.copy()

    # diff = 전일 종가 - 당일 종가 가 음수이면, 상승한 것
    ups[ups < 0] = 0
    downs[downs > 0] = 0

    period = 14

    # 최근 것에 가중치를 주는데, 이를 '지수 이동 평균(exponential moving avg)'
    # pandas 모듈에서 지수 이동 평균을 구해주는 함수는 ewm 함수
    # 최근 13일 동안 상승분 하락분

    # com: 비율을 얼마나 감소시킬지 1/(1 + com) 의 비율로 반영하므로 period - 1 만큼
    # min_periods: 값을 갖기 위해 최소 얼마만큼의 관측 개수가 있어야 하는지

    AU = ups.ewm(com=period - 1, min_periods=period).mean()
    AD = downs.abs().ewm(com=period - 1, min_periods=period).mean()

    RS = AU / AD

    return pandas.Series(100 - (100 / (1 + RS)), name="RSI")

# 가장 좋은 k값 구하기


def get_ror(ticker, k=0.5):
    """변동성 돌파를 위해 이상적인 k값 구하기"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    # 수수료는 일단 제외함
    df['ror'] = np.where(df['high'] - df['target'],
                         df['close'] / df['target'],
                         1)

    # 누적 곱에서 -2 인덱스?
    ror = df['ror'].cumprod()[-2]
    # post_message(f"오늘의 ror: {ror}")
    # print("오늘의 ror", ror)
    return ror


def cal_target(ticker):
    """목표가 설정하기"""
    # 업비트 기준: 하루 거래일 9:00 ~ 익일 AM8:59
    df = pyupbit.get_ohlcv(ticker, "day")

    # print(df.tail()) // 최신 5개 데이터 추출
    yesterday = df.iloc[-2]  # 어제 데이터.
    today = df.iloc[-1]  # 오늘의 데이터. 행 번호로 가져오기

    yesterday_range = yesterday['high'] - yesterday['low']
    ror = get_ror(ticker)
    target = today['open'] + (yesterday_range) * ror
    return target


def get_my_account():
    response = upbit.get_balances()
    return response


# todo: 거래대금 높으면서, 많이 언급되는 캐시 위주 -> 추후 거래대금 위주로 변경하기
# RSI 전략
ticker_list = ["KRW-BTC", "KRW-XRP",
               "KRW-ETC", "KRW-ETH", "KRW-BCH", "KRW-GRS"]
lower28 = []
higher70 = []

# 변동성 돌파 전략
ticker = "KRW-BTC"
target = cal_target(ticker)
op_mode = False  # 첫 날에는 사지 않는다. (현재가가 목표가보다 한 참 위에 있을 때 매수될 수 있기 때문)
hold = False  # 현재 코인 보유 여부

# todo: 잔고의 몇 퍼센트를 투자할건지 정하기
k = 0.1  # 잔고의 몇 퍼센트만큼 투자할건지 ex. 10퍼센트

upbit = pyupbit.Upbit(
    os.environ['UPBIT_ACCESS_KEY'], os.environ['UPBIT_SECRET_KEY'])

while True:
    try:
        # todo: ticker_list에서 변동성이 크고 거래대금이 큰 코인들 5종목 정도 추출
        now = datetime.datetime.now()

        # print(f"현재시간: {now}")

        # print("🔥RSI 전략🔥 시작!!")

        # RSI 전략 시작
        for i in range(len(ticker_list)):
            # 28이하, 70이상 각 코인에 대한 정보 초기화
            lower28.append(False)
            higher70.append(False)
            data = pyupbit.get_ohlcv(ticker=ticker_list[i], interval="minute3")
            now_rsi = rsi(data, 14).iloc[-1]  # 뒤에서 첫 번째 요소 반환

            # print(f"🔥RSI🔥코인명: {ticker_list[i]}\nRSI: {now_rsi}\n")

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

        # 변동성 돌파 전략

        # print("🔥변동성 돌파 전략🔥 시작!!\n")

        # 매도 시도 8:59:50~59
        if now.hour == 8 and now.minute == 59 and 50 <= now.second <= 59:
            if op_mode is True and hold is True:
                btc_balance = upbit.get_balance(ticker)
                sell_resposne = upbit.sell_market_ordert(ticker, btc_balance)
                status = f"🔥 매도 시도: ${sell_resposne}"
                post_message(status)
                hold = False  # 팔았으므로 보유 상태 False

            op_mode = False

        # 9:00:20~30 사이에, 목표가 경신 (첫 거래까지 20초정도 기다림)
        # 다른 코인에는 좀 다르게 적용해야할 수도
        if now.hour == 9 and now.minute == 0 and (20 <= now.second <= 30):
            target = cal_target(ticker)
            op_mode = True
            time.sleep(10)  # 30초 이미 지나버려서 두 번 다시 안 돎

        price = pyupbit.get_current_price(ticker)

        # 매 초마다 조건 확인 후, 매수 시도
        if op_mode is True and hold is False and price is not None and price >= target:
            krw_balance = upbit.get_balance("KRW")  # 우선 원화 잔고 조회
            buy_resposne = upbit.buy_market_order(ticker, krw_balance * k)
            status = f"🔥 매수 시도: ${buy_resposne}"
            post_message(status)
            hold = True  # 보유 상태를 True, 한 번 사면 더 이상 매수하지 않을 것

        # 매 시간마다 || 매수하게 되었을 때 슬랙 호출 isNewHour = now.minute == 0 and now.second == 0
        # -> 최대 24번 호출해서,, 아침(9시에서 안정화된 10시) - 점심(중간 점검 15시) - 저녁(22시)으로 호출하도록

        # 현재 재정 상태 (+ 손익 % 도 추가)
        firstReport = now.hour == 10 and now.minute == 0 and (
            0 <= now.second <= 5)
        secondReport = now.hour == 15 and now.minute == 0 and (
            0 <= now.second <= 5)
        thirdReport = now.hour == 22 and now.minute == 0 and (
            0 <= now.second <= 5)

        my_balance = get_my_account()
        status = f"{my_balance}"  
        # 가독성 편하게 수정 필요

        if firstReport or hold is True:
            post_message(" 📝 firstReport" + status)

        if secondReport or hold is True:
            post_message(" 📝 secondReport" + status)

        if thirdReport or hold is True:
           post_message(" 📝 thirdReport" + status)

        time.sleep(1)

    except Exception as e:
        error = f"❌에러 발생: {e}"
        post_message(error)
        time.sleep(1)
