"""This class will act like an "API" to both strategy and portfolio, getting
market data and querying portfolio status for live and backtesting environments"""

class Broker:
    """this parent class provides the structure for how the system interacts 
    with the outside world, be it the brokerage in live deployment
    or the historica data in backtesting. this class is made to be overwritten"""

    # === Fetching Data ===
    def get_stock_data(self, symbols, timeframe, num_candles):
        pass

    def get_latest_quote(self):
        pass

    def get_asset_value(self):
        pass

    def get_options_chain(self, underlying):
        pass

    def get_options_contracts(self):
        pass

    def get_closest_option(self):
        pass

    def get_closest_open_date(self):
        pass

    def now(self):
        pass

    # === Executing Orders ===
    def place_order(self, orders):
        pass

    def delta_order_to_orders(self, delta_orders):
        pass

    def cancel_order(self, order):
        pass

    def cancel_all_orders(self):
        pass

    def close_position(self, symbols):
        pass

    def close_all_positions(self):
        pass

    # === Querying Portfolio ===
    def get_open_orders(self):
        pass

    def get_positions(self):
        pass

    def get_acct_details(self):
        pass
