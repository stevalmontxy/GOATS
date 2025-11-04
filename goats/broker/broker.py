# this class will act like an "API" to both strategy and portfolio, 
# to get market data and update the portfolio holdings/orderbook
# the alpaca broker child class will be a wrapper around their alpaca python api
# the backtest broker class will act like a fake API for historic data
class Broker:
    '''this parent class provides the structure for how the system interacts 
    with the outside world, be it the brokerage in live deployment
    or the historica data in backtesting. this class is made to be overwritten'''

    # === Fetching Data ===
    def get_stock_data(self):
        pass

    def get_options_chain(self):
        pass

    def get_closest_open_day(self):
        pass

    # === Executing Orders ===
    def place_order(self):
        pass

    def close_position(self):
        pass

    # === Querying Portfolio ===
    def get_orderbook(self):
        pass

    def get_positions(self):
        pass

    def get_acct_value(self) -> tuple[float, float]:
        pass
        # return cash, acct_value