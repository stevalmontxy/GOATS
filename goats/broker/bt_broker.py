# Standard Imports
import datetime as dt

# Third Party Imports
import pandas as pd

# Local Imports
from .broker import Broker
from goats.core.core_objects import Portfolio, Stock, Option, Position, Account
from goats.core.core_objects import Order, LimitOrder

class BTBroker(Broker):
    '''BTBroker class keeps its own copy of pos and ords for api calls. 
    state memory is stored in portfolio tho
    BTBroker holds the data dfs, but it's passed in via init of the backtest class
    trade log and return log is held in backtest class, not here '''
    def __init__(self, options_df, underly_df, initial_cash):
        self.positions = [] 
        self.orders = []
        self.cash = initial_cash
        self.options_df = options_df
        self.underly_df = underly_df
        self.now = None # will be type dt.datetime

    def set_time(self, time):
        ''' BTBRoker ONLY METHOD'''
        self.now = time
        # self.now = self.now.tz_localize("America/New_York")        
        # self.now = timezone.utc.localize(self.now)

    # === Fetching Data ===

    def get_stock_data(self, symbol, timeframe, num_days) -> pd.DataFrame:
        '''for now, assume we only have SPY df for trading on SPY.
        ignore symbol param but its there for polymorphism'''
        if symbol != "SPY":
            raise NotImplementedError
        if timeframe != "1Hour":
            raise NotImplementedError

        end_date = self.now
        start_date = end_date - pd.Timedelta(days=num_days)
        stock_df = self.underly_df.loc[start_date:end_date]
        return stock_df

    def get_latest_quote(self, symbol=None, Stock=None, Option=None):
        '''returns latest quote (bid ask, etc), intake is very flexible
        for now this function is not in use or fully written'''
        raise NotImplementedError # not needed yet, may write later

    def get_latest_value(self, Stock=None, Option=None) -> float:
        ''' BTBRoker ONLY METHOD
        gets latest value/mid value for either stock or option
        BEWARE: it assumes that self.now time will be in there '''
        if Stock is not none:
            if stock.symbol != "SPY":
                raise NotImplementedError
            return data.loc[self.now].close
        else: # if option
            quote_date = self.now.replace(hour=0, minute=0)
            quote_time_hour = self.now.hour + self.now.minute/60
            df_slice = self.options_df[(options_df["[QUOTE_DATE]"] == quote_date) &
                                    (options_df["[STRIKE]"]==float(option.strike)) &
                                    (options_df["[EXPIRE_DATE]"]==option.expr) &
                                    (options_df["[QUOTE_TIME_HOURS]"]==quote_time_hour) ]

            if option.side == 'call':
                return float(df_slice.iloc[0]["[C_LAST]"])
            else:  # for puts
                return float(df_slice.iloc[0]["[P_LAST]"])

    def get_options_chain(self, underlying_symbol, side, expiration_date=None, 
        min_expiration=None, max_expiration=None, min_strike=None, max_strike=None):
        '''skipping for now, just use get_options_contracts()'''
        raise NotImplementedError # not needed yet, may write later

    def get_options_contracts(self, underlying_symbol, side, expiration_date=None, 
        min_expiration=None, max_expiration=None, min_strike=None, max_strike=None) -> pd.DataFrame:
        '''fct might not be needed for BTBroker'''
        if underlying_symbol != "SPY":
            raise NotImplementedError

        subset = self.options_df.loc[
            (self.options_df["[QUOTE_DATE]"] >= min_expiration) &
            (self.options_df["[QUOTE_DATE]"] <= max_expiration) &
            (self.options_df["[STRIKE]"] >= min_strike) &
            (self.options_df["[STRIKE]"] <= max_strike)
            ]
        return subset

    def get_closest_option(self, option: Option) -> Option:
        '''find option that best matches desired strike and expiration'''
        if option.symbol != "SPY":
            raise NotImplementedError

        # get working date
        while option.expr not in self.options_df["[EXPIRE_DATE]"]:
            option.expr += dt.timedelta(days=1)

        # get working expr
        filler = 0
        while option.strike not in self.options_df["[STRIKE]"]:
            filler += 1
            if int(option.strike + filler) in self.options_df["[STRIKE]"]:
                option.strike = int(option.strike + filler) 
            elif int(option.strike - filler) in self.options_df["[STRIKE]"]:
                option.strike = int(option.strike - filler) 
            
        return option

    def get_closest_open_date(self, date) -> dt.date:
        '''given a date, it will return the soonest market open date'''
        while date not in self.underly_df.index.date:
            date += dt.timedelta(days=1)
        return date

    # === Executing Orders ===

    def place_orders(self, orders): # returns res
        '''works for single order or multiple orders
        backtest broker takse the "res" and puts it into the trade log'''
        if order.is_stock:
            value = self.get_stock_value(Stock(order.symbol))
            self.positions.append(Stock(symbol=order.symbol))
        else: # is option
            value = self.get_option_value(Option(order.option.symbol))
            self.positions.append(Option(symbol=order.symbol))

        self.cash -= value * order.qty 
        # self.trade_log.append(f"Opened position ID: {option.ID} at time: {time} at ${value}")
        res = True
        return res
        # the way this is coded, currently orders will go straight to becoming positions.

    def delta_order_to_orders(self, delta_orders):
        '''takes over for orderMakerLive function
        works for single order or multiple orders on same
        example:    delta_orders = [
                        {'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1, underlying: "SPY"},
                        {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1, underlying: "SPY"} ]'''
        # self.find_closest_option(self)
        # underlying_last = df["[UNDERLYING_LAST]"]
        # goal_strike = underlying_last+strike_dist
        # goal_expr = time + timedelta(days=expr_dist)
        # # find closest strike
        # # find closest expr
        # # if side == 'call': not needed, same process for call or put. strike dist is properly set to acct for either case
        # option = Option(strike, expr, side)

        # return res
        raise NotImplementedError # not needed yet, may write later

    def cancel_order(self, order):
        '''works for single order or multiple orders'''
        raise NotImplementedError # not needed yet, may write later

    def cancel_all_orders(self): # returns res
        self.orders = []
        res = True
        return res

    def close_positions(self, symbols, order_type='market'): # returns res
        '''
        remove an option from positions list, find value at close time, add to trade log
        works for single order or multiple orders'''
        value = self.get_option_value(option.expr, option.strike, option.strike, self.now)
        qty = self.positions[option.ID].qty
        self.positions[option.ID].delete #or whatever ~~~~~~~~~~~
        cash += 100 * value * qty
        # self.trade_log.append(f"closed position ID: {option.ID} at time: {time} at ${value}")
        res = True
        return res

    def close_all_positions(self): # returns res
        for p in self.positions:
            if p.is_stock:
                value = self.get_stock_value(p)
                cash += value * p.qty
            else: # is option
                value = self.get_option_value(p.option.expr, p.option.strike, p.option.strike, self.now)
                qty = p.qty
                cash += value * p.qty
        self.orders = []

        res = True
        return res

    # === Querying Portfolio ===

    def get_open_orders(self) -> list[Order]:
        return self.orders

    def get_positions(self) -> list[Position]:
        return self.positions

    def get_acct_details(self) -> Account:
        return Account(float(account.cash), float(account.buying_power), float(account.portfolio_value))
