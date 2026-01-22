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
        # self.now = self.now.tz_localize("America/New_York") # no longer timezone aware
        # self.now = timezone.utc.localize(self.now)

    # === Fetching Data ===

    def get_stock_data(self, symbol, timeframe, num_days) -> pd.DataFrame:
        '''for now, assume we only have AAPL df for trading on AAPL.
        ignore symbol param but its there for polymorphism'''
        if symbol != "AAPL":
            raise NotImplementedError
        if timeframe != "30Min":
            raise NotImplementedError

        end_date = self.now
        start_date = end_date - pd.Timedelta(days=num_days)
        stock_df = self.underly_df.loc[start_date:end_date]
        return stock_df

    def get_latest_quote(self, symbol=None, Stock=None, Option=None):
        '''returns latest quote (bid ask, etc), intake is very flexible
        for now this function is not in use or fully written'''
        raise NotImplementedError # not needed yet, may write later

    def get_asset_value(self, asset)-> float:
        ''' BTBRoker ONLY METHOD
        gets latest value/mid value for either stock or option
        BEWARE: it assumes that self.now time will be in there '''
        if isinstance(asset, Stock):
            if asset.symbol != "AAPL":
                raise NotImplementedError
            # return data.loc[self.now].Close
            return self.underly_df.loc[self.now].Close
        else: # if option
            quote_date = self.now.replace(hour=0, minute=0)
            quote_time_hour = self.now.hour + self.now.minute/60
            df_slice = self.options_df[(self.options_df["[QUOTE_DATE]"] == pd.to_datetime(quote_date)) &
                                    (self.options_df["[STRIKE]"]==float(asset.strike)) &
                                    (self.options_df["[EXPIRE_DATE]"]==pd.to_datetime(asset.expr)) &
                                    (self.options_df["[QUOTE_TIME_HOURS]"]==quote_time_hour) ]

            if asset.side == 'call':
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
        if underlying_symbol != "AAPL":
            raise NotImplementedError
        expiration_date = pd.to_datetime(expiration_date) # need to use pd timestamp type
        min_expiration = pd.to_datetime(min_expiration)
        max_expiration = pd.to_datetime(max_expiration)

        subset = self.options_df.loc[
            (self.options_df["[QUOTE_DATE]"] >= min_expiration) &
            (self.options_df["[QUOTE_DATE]"] <= max_expiration) &
            (self.options_df["[STRIKE]"] >= min_strike) &
            (self.options_df["[STRIKE]"] <= max_strike)
            ]
        return subset

    def get_closest_option(self, option: Option) -> Option:
        '''find option that best matches desired strike and expiration'''
        if option.underlying != "AAPL":
            raise NotImplementedError

        # get working date
        while pd.to_datetime(option.expr) not in self.options_df["[EXPIRE_DATE]"].values:
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
        # while date not in self.underly_df.index.date:
        if isinstance(date, dt.datetime):
            date = date.date() # i know this is ugly
        date = pd.to_datetime(date) # need to use pd timestamp type
        while date not in self.options_df["[QUOTE_DATE]"].values:
            date += dt.timedelta(days=1)
        return date

    # === Executing Orders ===

    def place_orders(self, order): # returns res
        '''works for single order or multiple orders
        backtest broker takse the "res" and puts it into the trade log'''
        # if order.is_stock:
        #     value = self.get_asset_value(order.stock)
        #     self.positions.append(Position(order.stock.symbol, True, order.qty, stock=order.stock))
        # else: # is option
        #     value = self.get_asset_value(order.option)
        #     self.positions.append(Postion(order.option.symbol, False, order.qty, option=order.option))

        value = self.get_asset_value(order.asset)
        self.positions.append(Position(order.asset.symbol, order.asset, order.qty))

        self.cash -= value * order.qty 
        # self.trade_log.append(f"Opened position ID: {option.ID} at time: {time} at ${value}")
        res = True
        return res
        # the way this is coded, currently orders will go straight to becoming positions.

    def delta_order_to_orders(self, delta_orders):
        '''takes over for orderMakerLive function
        works for single order or multiple orders on same
        example:    delta_orders = [
                        {'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1, underlying: "AAPL"},
                        {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1, underlying: "AAPL"} ]'''
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

    def close_positions(self, symbols=None, asset=None, order_type='market'): # returns res
        ''' remove an option from positions list, find value at close time, add to trade log
        works for single order or multiple orders'''
        if asset is not None:
            if asset.is_stock:
                value = self.get_asset_value(asset.expr, asset.strike, asset.strike, self.now)
                qty = self.positions[asset.ID].qty
                self.positions[asset.ID].delete #or whatever ~~~~~~~~~~~
        cash += 100 * value * qty
        # self.trade_log.append(f"closed position ID: {option.ID} at time: {time} at ${value}")
        res = True
        return res

    def close_all_positions(self): # returns res
        for p in self.positions:
            if p.is_stock:
                value = self.get_asset_value(p)
                cash += value * p.qty
            else: # is option
                value = self.get_asset_value(p.option.expr, p.option.strike, p.option.strike, self.now)
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

    def get_acct_value(self) -> Account:
        NAV = self.cash
        buying_power = self.cash
        for p in self.positions:
            NAV += self.get_asset_value(p) * p.qty
        # for o in orders: # assume its okay since BTBroker instantly turns orders into assets
            # buying_power -= self.get_asset_value(o.symbol) * o.qty
        
        return Account(self.cash, buying_power, NAV)
