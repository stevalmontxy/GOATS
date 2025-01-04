# https://www.youtube.com/watch?v=B0Z7oCmr5nM

from alpaca.trading.stream import TradingStream
from mysecrets import ALPACA_API_KEY_PAPER, ALPACA_SECRET_KEY_PAPER

trade_stream_client = TradingStream(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER, paper=True)

async def trade_updates_handler(data):
    print(data)

trade_stream_client.subscribe_trade_updates(trade_updates_handler)
trade_stream_client.run()