import pyupbit
import numpy as np

# 가장 좋은 k값 구하기
def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC", count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0032
    df['ror'] = np.where(df['high'] - df['target'],
                         df['close'] / df['target'] - fee,
                         1)
    
    # 누적 곱에서 -2 인덱스?
    ror = df['ror'].cumprod()[-2]
    return ror

# 하락장일수록 ror(수익률)이 낮으며, ror이 높은 k값을 찾는게 최우선
for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))