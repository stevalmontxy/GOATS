# this class will act like an "API" to both strategy and portfolio, 
# to get market data and update the portfolio open positions and orders
# the alpaca broker child class will be a wrapper around their alpaca python api
# the backtest broker class will act like a fake API for historic data
class Broker:
    '''this parent class provides the structure for how the system interacts 
    with the outside world, be it the brokerage in live deployment
    or the historica data in backtesting. this class is made to be overwritten'''
    # def __init__(self):
    #     pass
    # you can delete if fully not needed
#Also, consider making this an abstract base class class Broker(ABC),
# and define methods as @abstractmethod. doesn't rly change functionality but makes sense to do
    # === Fetching Data ===
    def get_stock_data(self, symbols, timeframe, num_candles):
        pass
        # return pd.dataframe(?)

    def get_options_chain(self, underlying):
        pass
        # return pd.dataframe(?)

    def find_closest_option(self):
        '''find option that best matches desired strike and expiration'''
        self.get_options_chain()
        pass
        # return closest option

    def get_closest_open_day(self):
        pass
        # return datetime

    # === Executing Orders ===
    def place_orders(self, orders):
        '''works for single order or multiple orders'''
        if type == Limit:
            pass
        elif type == other:
            raise NotImplementedError("Only doing limit orders for now")
        pass
        # return res
        # return res's can be used by live to confirm working and also record results

    def delta_order_to_orders(self, delta_orders):
        '''takes over for orderMakerLive function
        works for single order or multiple orders on same
        example:    delta_orders = [
                        {'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1, underlying: "SPY"},
                        {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1, underlying: "SPY"} ]'''
        self.find_closest_option(self)
        pass
        # return res

    def close_positions(self, symbols):
        '''works for single order or multiple orders'''
        pass
        # return res

    # === Querying Portfolio ===
    def get_open_orders(self):
        pass
        # return list of orders

    def get_positions(self):
        pass
        # return list of positions

    def get_acct_value(self):
    # def get_acct_value(self) -> tuple[float, float]:
        pass
        # return cash, acct_value, buying_power