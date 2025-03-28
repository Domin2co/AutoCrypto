#requirements.txt 파일에 입력된 패키지를 한번에 다운로드 받기
#pip install -r .\requirements.txt

import os
from dotenv import load_dotenv
load_dotenv()

def ai_trading():
    # 1. 업비트 차트 데이터 가져오기 (30일 일봉)
        # O(Open) : 시가, 첫 번째 거래 가격
        # H(High) : 고가, 최고 거래 가격
        # L(Low) : 저가, 최저 거래 가격
        # C(Close) : 종가, 마지막 거래 가격
        # V(Volume) : 거래량, 거래된 수량
    import pyupbit
    df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")

    # 2. AI에게 데이터 제공하고 판단 받기
    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "You are a Bitcoin investing expert. Tell me whether to BUY, SELL, or HOLD at the moment based on the chart data provided.response in json format.\n\nResponse Example:\n{\"decision\":\"buy\", \"reason\":\"some technical reason\"}\n{\"decision\":\"sell\", \"reason\":\"some technical reason\"}\n{\"decision\":\"hold\", \"reason\":\"some technical reason\"}"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": df.to_json()
            }
        ]
        }
    ],
    response_format={
        "type": "json_object"
    }
    )

    result = response.choices[0].message.content

    # 3. AI의 판단에 따라 실제로 자동매매 진행하기
    import json
    result = json.loads(result)

    import pyupbit

    access = os.getenv("UPBIT_ACCESS_KEY")
    secret = os.getenv("UPBIT_SECRET_KEY")
    upbit = pyupbit.Upbit(access, secret)

    print("### AI Decision: ", result["decision"].upper(), "###")
    print(f"### reason: {result['reason']} ###")

    if result["decision"] == "buy":
        # 매수
        my_krw = upbit.get_balance("KRW")

        if my_krw * 0.9995 > 5000:
            print("### Buy Order Executed ###")
            print(upbit.buy_market_order("KRW-BTC", my_krw * 0.9995))
        else:
            print("### Buy Order Failed : Insufficient KRW (less than 5000 KRW) ###")
    elif result["decision"] == "sell":
        # 매도
        my_btc = upbit.get_balance("KRW-BTC")
        current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]

        if my_btc * current_price > 5000:
            print("### Sell Order Executed ###")
            print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
        else:
            print("### Sell Order Failed : Insufficient BTC (less than 5000 KRW) ###")
    elif result["decision"] == "hold":
        # 대기
        print("### Hold Position ###")

while True:
    import time
    ai_trading()
    time.sleep(14400)