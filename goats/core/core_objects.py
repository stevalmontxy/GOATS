from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd


class Portfolio:
    '''
    broker: this is the "brokerage" that will be used to fetch data and stuff
    cash: aka buying power
    acct_value: cash+ positions
    positions: list that holds Position objects
    orderbook: list that holds real orders
    pseudo_orderbook: list that holds "pseudo" orders- these are things that strat monitors, and submits a real order upon condition
    '''
    def __init__(self, broker):
        self.broker = broker
        self.cash = 0.0
        self.acct_value = 0.0
        self.positions = []
        self.orderbook = []
        self.pseudo_orderbook = []

    # maybe use kwargs to "overload" for options or stock 
    def addPosition(self, option, symbol, qty, entryTime, entryPrice):
        '''the symbol entry helps to locate entries a lot easier
        entryTime should be input of date.today(). if position is being updated, it will be None'''
        pos = Position(option=option, symbol=symbol, entryTime=entryTime, exitTime=exitTime, qty=qty)
        self.positions.append(pos)

    def removePosition(self, symbol):
        '''only removes position from portfolio object
        removing from broker is handled by stratgey
        symbol: string'''
        for i, pos in enumerate(self.positions):
            if pos.symbol == symbol:
                print("symbol found")
                self.positions.pop(i)
                break

    def add_order(self):
        pass

    def remove_order(self):
        pass

    def updateAcctValue(self):
        self.cash, self.acct_value = self.broker.get_acct_value()

    def update_portfolio(self):
        '''will sync portfolio to its current status. works with a brand
        new portfolio as well as a preexisting outdated one
        the reason to manually check instead of just replacing the whole list is bc local stores some metadata'''
        positions_broker = self.broker.get_positions()
        if self.hasPositions:
            symbols_broker = [p.symbol for p in positions_broker]
            for p in self.positions[:]: # Iterate over a copy to avoid modification issues
                if p.symbol not in symbols_broker:
                    self.removePosition(p.symbol)

        if len(positions_broker) > 0:
            symbols_port = [p.symbol for p in self.positions]
            for p in positions_broker[:]:
                if p.symbol not in symbols_port:
                    self.addPosition(p, p.symbol, p.qty, None, None)

        orders_broker = self.broker.get_orderbook()
        if self.has_orders:
            symbols_broker = [o.symbol for o in orders_broker]
            for o in self.orderbook[:]:
                if o.symbol not in symbols_broker:
                    self.remove_order(o.symbol)

        if len(orders_broker) > 0:
            symbols_port = [p.symbol for p in self.positions]
            for o in orders_broker[:]:
                if o.symbol not in symbols_port:
                    self.add_order(o, o.symbol, o.qty, None, None)
        
        self.updateAcctValue()
        return self # optional return

    @property
    def hasPositions(self):
        return len(self.positions) > 0

    @property
    def has_orders(self):
        return len(self.orderbook) > 0

    def __repr__(self):
        return f"Portfolio: cash: ${self.cash}, # positions: {len(self.positions)}, Acct value: {self.acctValue}"


class Position:
    '''This is just kinda an intermediary between portfolio -> position -> option.
    this allows possibility for stock positions in the future if desired
    orders/trades elsewhere in the portfolio can be linked to positions
    '''
    def __init__(self, option=None, stock=None, is_stock=None, symbol=None, entryTime=None, exitTime=None, qty=1, price=None, posID=0):
        self.option = option
        self.stock = stock
        self.is_stock = is_stock
        self.qty = qty # + indicates long, - indicates short
        self.symbol = symbol
        self.entryTime = entryTime
        self.exitTime = exitTime
        self.price = price # can be bid or ask. value is kept at this level. at Stock or Option level, they are only used to identify
        self.ID = posID # CURRENTLY NOT IN USE position ID and option ID are both self referenced as ID
                        # posID: id number within active positions. an option will be associated with a posID throughout its holding,
                        #        then the posID will be reused by other positions

    @property
    def is_long():
        return (self.qty > 0)

    def __repr__(self):
        return (f"Position(ID={self.ID}, symbol='{self.symbol}', qty={self.qty}, "
                f"entryDate={self.entryDate}, exitDate={self.exitDate}, "
                f"option={self.option}, stock={self.stock})")


class Stock:
    '''
    symbol: symbol (str)
    bid/ask/price data handled by position/portfolio. this class is mostly an identifier
    '''
    def __init__(self, symbol, symID=0):
        self.symbol = symbol
        self.ID = symID # CURRENTLY NOT IN USE

    def __repr__(self):
        return f"Stock: symbol: {self.symbol}, symID: {self.ID}"


class Option:
    '''
    strike: price (float)
    expr: expiration (date, can init as date(time) or str YYYY-MM-DD)
    side: 'call' or 'put' (str)
    underlying: underlying stock symbol (str)
    bid/ask/price data handled by position/portfolio. this class is mostly an identifier'''
    def __init__(self, strike, expr, side, underlying, optID=0):
        self.strike = strike
        self.expr = expr if isinstance(expr, date) else datetime.strptime(expr, "%Y-%m-%d")
        self.side = side # call or put
        self.underlying = underlying
        self.ID = optID # CURRENTLY NOT IN USE optID is different from posID. referenced as either position.ID or option.ID
                        # optID: id number of option, never to be reused throughout a backtest (or lifetime unless reset maybe)
                        # for ex, the 5th option taken by script will have optID of 5, posID of 1, assuming the script holds two at a time, and sells in order

    def __repr__(self):
        return f"Option: strike: ${self.strike}, expr: {self.expr}, side: {self.side}, optID: {self.ID}"


class Order:
    '''
    symbol: symbol - using this, can find link to a position (str)
    is_stock: whether its stock or not (bool)
    qty: qty (float)
    pseudo: whether an order is actually in the broker or it has to be manually entered as a limit at the right time (bool)
    '''
    def __init__(self, symbol, is_stock, qty, pseudo=False, ordID=0):
        self.symbol = symbol
        self.is_stock = is_stock
        self.qty = qty # + indicates long, - indicates short
        # self.conditional = conditional
        # self.minimum = minimum
        self.pseudo = pseudo # bool, whether it's a "pseudo or no"
        self.ID = ordID  # CURRENTLY NOT IN USE

    '''check_condition() all of them need to be moved into like strategy or execution or a standalone function.
    OR leave them here, and just input what is needed into the method?'''
    def check_condition(self):
        return false
        #maybe they should return either an Order or None

    def __repr__(self):
        return f"Order: symbol: ${self.symbol}, is_stock: {self.is_stock}, qty: {self.qty}, conditional: {self.conditional}, minimum: {self.minimum}, ordID: {sef.ordID}"

class MarketOrder(Order):
    '''just a market order'''
    def __init__(self, symbol, is_stock, qty, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, ordID=0)

    def check_condition(self):
        return True

    def __repr__(self):
        return f"MarketOrder: symbol: ${self.symbol}, is_stock: {self.is_stock}, qty: {self.qty}, conditional: True, ordID: {sef.ordID}"

class LimitOrder(Order):
    def __init__(self, symbol, is_stock, qty, limit_price, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=not is_stock, ordID=0)
        self.limit_price = limit_price

    def check_condition(self, price):
        # price is current price. maybe it should be an address so func has no args?
        if qty > 0:
            return price > limit_price
        else:
            return price < limit_price

    def __repr__(self):
        return f"LimitOrder: symbol: ${self.symbol}, is_stock: {self.is_stock}, qty: {self.qty}, conditional: True, ordID: {sef.ordID}"

class StopOrder(Order):
    def __init__(self, symbol, is_stock, qty, stop_price, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=not is_stock, ordID=0)
        self.stop_price = stop_price

    def check_condition(self, price):
        if qty > 0:
            return price < stop_price
        else:
            return price > stop_price

    def __repr__(self):
        pass

class TrailingStopOrder(Order):
    def __init__(self, symbol, is_stock, qty, trail_nom=None, trail_pc=None, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=not is_stock, ordID=0)
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

    def __repr__(self):
        pass

class SLTPOrder(Order):
    def __init__(self, symbol, is_stock, qty, sl=None, tp=None, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=not is_stock, ordID=0)
        self.sl = sl
        self.tp = tp

    def check_condition(self, price):
        if qty > 0:
            return (price > self.tp) or (price > self.sl)
        else:
            return (price < self.tp) or (price < self.sl)

    def __repr__(self):
        pass

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
    def __init__(self, symbol, is_stock, qty, a, b, c, d, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, pseudo=True, ordID=0)
        self.a = a
        self.b = b
        self.c = c
        self.d = d 

    def check_condition(self, price, init_trail_pc, vol, upward_vol, rec_price_velo):
        pass

    def __repr__(self):
        pass
