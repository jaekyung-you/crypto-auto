import pyupbit
import time

# all_tickers = pyupbit.get_tickers(fiat="KRW")
# for ticker in all_tickers:
#     current_ohlcv = pyupbit.get_ohlcv(ticker, count=1)
#     time.sleep(0.3)
#     print(f"{ticker} 현재가: {current_ohlcv})")

# print(all_krw_data)

data = pyupbit.get_ohlcv("KRW-RFR", interval="minute1")
# print("close", data["close"], data["open"])
print("값", 1 - (data["close"]/data["open"]))

# 현재 비트코인 가격과 포트폴리오 내 보유 중인 비트코인 수량 설정
current_price = 10000  # 현재 비트코인 가격 (예: $10,000)
bitcoin_holding = 5   # 보유 중인 비트코인 수량 (예: 5 BTC)

# 손실 허용 비율 설정 (10% 손실 시 추가매수)
loss_threshold = 0.1  # 10% 손실 허용

# 손실 계산
initial_investment = bitcoin_holding * current_price
current_value = initial_investment

# 현재 포트폴리오 가치와 초기 투자금 출력
print("현재 포트폴리오 가치:", current_value)
print("초기 투자금:", initial_investment)

# 손실 계산
loss = initial_investment - current_value

# 손실이 허용한 비율 이상이면 추가매수
if loss >= initial_investment * loss_threshold:
    additional_investment = current_value * (loss_threshold / (1 - loss_threshold))
    bitcoin_holding += additional_investment / current_price
    current_value += additional_investment
    print("10% 손실 발생! 추가매수 수행.")
    print("현재 포트폴리오 가치:", current_value)
    print("보유 중인 비트코인 수량:", bitcoin_holding)


# 현재 비트코인 가격과 구매 기준가 설정
current_price = 10000  # 현재 비트코인 가격 (예: 10,000달러)
buy_threshold = 0.10  # 10% 하락할 때 추가 매수

# 사용자가 소유한 비트코인 수량
current_holdings = 5  # 예: 5개의 비트코인을 소유

# 비트코인이 10% 이상 하락할 때 추가 매수
def buy_bitcoin(current_price, current_holdings, buy_threshold):
    target_price = current_price * (1 - buy_threshold)
    
    if current_price <= target_price:
        # 추가 매수 로직을 여기에 구현
        # 예를 들어, 거래소 API를 사용하여 비트코인을 구매하는 코드를 추가합니다.
        print(f"비트코인을 {current_price}에 추가 매수합니다.")
        current_holdings += 1  # 예: 1개 추가 매수
    else:
        print(f"비트코인 가격은 {current_price}로 아직 추가 매수 기준에 미치지 못했습니다.")

# 비트코인 가격 업데이트 (실제로는 거래소 API를 통해 업데이트됩니다)
new_price = 9000  # 예: 비트코인 가격이 9,000달러로 하락했다고 가정

# 추가 매수 함수 호출
buy_bitcoin(new_price, current_holdings, buy_threshold)
