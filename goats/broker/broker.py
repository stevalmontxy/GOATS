# this class will act like an "API" to both strategy and portfolio, 
# to get market data and update the portfolio open positions and orders
# the alpaca broker child class will be a wrapper around their alpaca python api
# the backtest broker class will act like a fake API for historic data
class Broker:
    '''this parent class provides the structure for how the system interacts 
    with the outside world, be it the brokerage in live deployment
    or the historica data in backtesting. this class is made to be overwritten'''

    # === Fetching Data ===

    def get_stock_data(self, symbols, timeframe, num_candles):
        pass
        # return pd.dataframe(?)

    def get_latest_quote(self):
        pass

    def get_options_chain(self, underlying):
        pass
        # return pd.dataframe(?)

    def get_options_contracts(self):
        pass

    def get_closest_option(self):
        '''find option that best matches desired strike and expiration'''
        pass
        # return closest option

    def get_closest_open_date(self):
        pass
        # return datetime

    # === Executing Orders ===

    def place_orders(self, orders):
        '''works for single order or multiple orders'''
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

    def cancel_order(self, order):
        '''works for single order or multiple orders'''
        pass

    def cancel_all_orders(self):
        pass

    def close_positions(self, symbols):
        '''works for single order or multiple orders'''
        pass
        # return res

    def close_all_positions(self):
        pass

    # === Querying Portfolio ===

    def get_open_orders(self):
        pass
        # return list of orders

    def get_positions(self):
        pass
        # return list of positions

    def get_acct_details(self):
        pass
