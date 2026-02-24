import datetime as dt
import numpy as np
import pandas as pd
from dataclasses import dataclass

class Portfolio:
    '''
    broker: this is the "brokerage" that will be used to fetch data and stuff
    cash: aka buying power
    acct_value: cash + positions
    positions: list that holds Position objects
    open_orders: list that holds real orders
    pseudo_orders: list that holds "pseudo" orders- these are things that strat monitors, and submits a real order upon condition
    '''
    def __init__(self, broker, initial_cash):
        self.broker = broker
        self.cash = initial_cash
        self.acct_value = initial_cash
        self.positions = []
        self.open_orders = []
        self.pseudo_orders = []

    # def add_position(self, option, symbol, qty, entry_time, entry_price):
    def add_position(self, pos):
        '''entry_time should be input of date.today(). if position is being updated, it will be None'''
        self.positions.append(pos)

    def remove_position(self, symbol):
        '''only removes position from portfolio object
        removing from broker is handled by stratgey
        symbol: string'''
        for i, pos in enumerate(self.positions):
            if pos.symbol == symbol:
                self.positions.pop(i)
                break

    def add_order(self, ord):
        self.open_orders.append(ord)

    def remove_order(self, symbol):
        for i, ord in enumerate(self.open_orders):
            if ord.symbol == symbol:
                self.open_orders.pop(i)
                break
    
    def add_pseudo_order(self, ord):
        self.pseudo_orders.append(ord)

    def update_portfolio(self):
        '''will sync portfolio to its current status. works with a brand
        new portfolio as well as a preexisting outdated one
        the reason to manually check instead of just replacing the whole list is bc local stores some metadata'''
        positions_broker = self.broker.get_positions()
        if self.has_positions:
            symbols_broker = [p.symbol for p in positions_broker]
            for p in self.positions[:]: # Iterate over a copy to avoid modification issues
                if p.symbol not in symbols_broker:
                    self.remove_position(p.symbol)

        if len(positions_broker) > 0:
            symbols_port = [p.symbol for p in self.positions]
            for p in positions_broker[:]:
                if p.symbol not in symbols_port:
                    self.add_position(p)

        orders_broker = self.broker.get_open_orders()
        if self.has_orders:
            symbols_broker = [o.symbol for o in orders_broker]
            for o in self.open_orders[:]:
                if o.symbol not in symbols_broker:
                    self.remove_order(o.symbol)

        if len(orders_broker) > 0:
            symbols_port = [p.symbol for p in self.positions]
            for o in orders_broker[:]:
                if o.symbol not in symbols_port:
                    self.add_order(o)

        self.update_acct_value()
        return self # optional return

    def update_acct_value(self):
        acct = self.broker.get_acct_value()
        self.cash = acct.cash
        self.acct_value = acct.portfolio_value
        # buying power ignored

    @property
    def has_positions(self):
        return len(self.positions) > 0

    @property
    def has_orders(self):
        return len(self.open_orders) > 0

    def __repr__(self):
        return f"Portfolio: cash: ${self.cash}, # positions: {len(self.positions)}, Acct value: {self.acctValue}"

@dataclass
class Stock:
    '''bid/ask/price data handled by position/portfolio'''
    symbol: str
    # self.ID = sym_ID # CURRENTLY NOT IN USE
    # def __init__(self, symbol, sym_ID=0):


@dataclass
class Option:
    '''bid/ask/price data handled by position/portfolio'''
    strike: float
    expr: dt.date
    side: str # C or P for call/put
    underlying: str
    symbol: str = None

    def __post_init__(self):
        if self.symbol is None:# make OCC style symbol for option
            self.symbol = f'{self.underlying}{self.expr.strftime("%y%m%d")}{self.side}{int(round(self.strike*1000)):08d}'
        if isinstance(self.expr, dt.datetime):
            self.expr = self.expr.date() # make sure its a date, without a time


@dataclass
class Position:
    '''This is an intermediary between portfolio -> position -> option.'''
    symbol: str 
    asset: Stock | Option = None
    qty: float = 1 # + indicates long, - indicates short
    entry_time: dt.datetime = None
    exit_time: dt.datetime = None
    price: float = None # can be bid or ask. value is kept at this level. at Stock or Option level, they are only used to identify

    @property
    def is_stock(self):
        if self.symbol is None:
            return isinstance(self.asset, Stock)
        else:
            return len(self.symbol) < 5

    def __repr__(self):
        return (f"Position(symbol='{self.symbol}', qty={self.qty})") # super simple for now

@dataclass
class Account:
    cash: float
    buying_power: float
    portfolio_value: float


@dataclass
class DeltaOrder:
    '''not related to primary order class. used as input to create a real order'''
    pass


class Order:
    '''
    symbol: symbol - using this, can find link to a position (str)
    is_stock: whether its stock or not (bool)
    qty: qty (float)
    pseudo: whether an order is actually in the broker or it has to be manually entered as a limit at the right time (bool)
    '''
    def __init__(self, symbol=None, asset=None, qty=1, pseudo=False):
        self.symbol = symbol
        self.asset=asset
        self.qty = qty # + indicates long, - indicates short
        # self.conditional = conditional
        # self.minimum = minimum
        # self.pseudo = pseudo # bool, whether it's a "pseudo or no" removed, just storing separate from real ones

    '''check_condition() all of them need to be moved into like strategy or execution or a standalone function.
    OR leave them here, and just input what is needed into the method?'''
    def check_condition(self, price):
        return false
        #maybe they should return either an Order or None

    @property
    def is_stock(self):
        if self.symbol is None:
            return isinstance(self.asset, Stock)
        else:
            return len(self.symbol) < 5


class MarketOrder(Order):
    '''just a market order'''
    def __init__(self, symbol=None, asset=None, qty=1):
        super().__init__(symbol=symbol, asset=asset, qty=qty)

    def check_condition(self, price):
        return True


class ScheduledOrder(Order):
    def __init__(self, symbol=None, asset=None, qty=1, place_time=None, order_type='limit'):
        super().__init__(symbol=symbol, asset=asset, qty=qty)
        self.place_time = place_time
        self.order_type = order_type

    def check_condition(self, time):
        return time >= self.place_time

    def __repr__(self):
        return (f"ScheduledOrder(symbol='{self.symbol}', qty={self.qty}, "
                f"place_time='{self.place_time}', order_type='{self.order_type}')")


class LimitOrder(Order):
    '''Limit price can be provided, or if None, will automatically get a quote'''
    def __init__(self, symbol=None, asset=None, qty=1, limit_price=None):
        super().__init__(symbol=symbol, asset=asset, qty=qty)
        self.limit_price = limit_price

    def check_condition(self, price):
        # price is current price. maybe it should be an address so func has no args?
        if qty > 0:
            return price > limit_price
        else:
            return price < limit_price


class StopOrder(Order):
    def __init__(self, symbol, is_stock, qty, stop_price):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=not is_stock)
        self.stop_price = stop_price

    def check_condition(self, price):
        if qty > 0:
            return price < stop_price
        else:
            return price > stop_price


class TrailingStopOrder(Order):
    def __init__(self, symbol, is_stock, qty, trail_nom=None, trail_pc=None):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=not is_stock)
        self.trail_nom = trail_nom
        self.trail_pc = trail_pc
        if (self.trail_nom and self.trail_pc):
            raise ValueError("Only provide trail_nom OR trail_pc, not both.")
        elif (not self.trail_nom and not self.trail_pc):
            raise ValueError("Provide trail_nom OR trail_pc.")
        self.trail_price = None

    def check_condition(self, price):
        if qty > 0:
            self.trail_price = min(self.trail_price, price*(1+self.trail_pc), price+self.trail_nom)
            return price > self.trail_price
        else:
            self.trail_price = max(self.trail_price, price*(1-self.trail_pc), price-self.trail_nom)
            return price < self.trail_price


class SLTPOrder(Order):
    def __init__(self, symbol, is_stock, qty, sl=None, tp=None):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=not is_stock)
        self.sl = sl
        self.tp = tp

    def check_condition(self, price):
        if qty > 0:
            return (price > self.tp) or (price > self.sl)
        else:
            return (price < self.tp) or (price < self.sl)


class DynamicTrailingOrder(Order):
    '''
    this order type is more of an "position exit strategy"
    it's like a trailing stop where the trailing
    amt is variable based on a few inputs and adjustable params
    a: param for init_trail_pc: it starts as a trailing at this level
    b: param for vol: volatility of price
    c: param for upward_vol: vol in position dir - vol against position dir
    d: param for rec_price_velo: recent price "velocity" -- I might set this as a function i.e. d = f(rec_price_velo)
    '''
    def __init__(self, symbol, is_stock, qty, a, b, c, d):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=True)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def check_condition(self, price, init_trail_pc, vol, upward_vol, rec_price_velo):
        pass
