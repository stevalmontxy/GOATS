# this class will act like an "API" to both strategy and portfolio, 
# to get market data and update the portfolio holdings/orderbook
# the alpaca broker child class will be a wrapper around their alpaca python api
# the backtest broker class will act like a fake API for historic data
class Broker:
    pass