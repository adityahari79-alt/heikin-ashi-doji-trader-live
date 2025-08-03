import websocket
import json
from datetime import datetime

# Map to store current candle data
candles = {}

# Set your WebSocket URL and access token
WS_URL = "wss://api.upstox.com/v2/feed/market-data-feed/socket/websocket"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

# Instrument token you want to track
INSTRUMENT_TOKEN = "NSE_INDEX|Nifty 50"

def on_message(ws, message):
    data = json.loads(message)
    tick = data['data']  # Adjust this depending on Upstox's tick message format
    instrument = tick['instrument_token']
    price = float(tick['last_price'])
    volume = int(tick['volume_traded_today'])
    timestamp = datetime.fromtimestamp(tick['exchange_time'] / 1000)
    minute = timestamp.replace(second=0, microsecond=0)

    candle = candles.get(minute, {"open": price, "high": price, "low": price, "close": price, "volume": 0})
    candle["high"] = max(candle["high"], price)
    candle["low"] = min(candle["low"], price)
    candle["close"] = price
    candle["volume"] += volume
    candles[minute] = candle

    print(f"Candle for {minute}: {candle}")

def on_open(ws):
    # Subscribe to your instrument
    subscribe_message = json.dumps({
        "guid": "some_unique_id",
        "method": "sub",
        "data": {"instrumentKeys": [INSTRUMENT_TOKEN]}
    })
    ws.send(subscribe_message)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("WebSocket closed")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL + "?access_token=" + ACCESS_TOKEN,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()