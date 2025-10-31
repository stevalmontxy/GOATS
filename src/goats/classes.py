from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd


class Portfolio:
    '''
    this holds the properties of the account.
    '''
    def __init__(self, initialCapital=100000):
        self.cash = initialCapital # this is set at instantiation, and changed over time. don't need to track over time
        self.positions = []
        self.acctValue = initialCapital # acct value over time
        self.orderbook = []
        self.pseudoorderbook = [] # this is like limit option orders, which I don't actually send until market is near price

    # maybe use kwargs to "overload" for options or stock 
    def addPosition(self, option, symbol, qty, entryTime, entryPrice):
        '''the symbol entry helps to locate entries a lot easier
        entryTime should be input of date.today(). if position is being updated, it will be None'''
        pos = Position(option=option, symbol=symbol, entryTime=entryTime, exitTime=exitTime, qty=qty)
        self.positions.append(pos)

    def removePosition(self, symbol):
        '''symbol: string'''
        for i, pos in enumerate(self.positions):
            if pos.symbol == symbol:
                print("symbol found")
                self.positions.pop(i)
                break

    @property
    def hasPositions(self):
        return len(self.positions) > 0
    
    def updateAcctValue(self):
        pass

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
        sefl.underlying = underlying
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
    # conditional: the variable to beat (pointer/reference?)
    # minimum: conditional must beat this (float)
    # conditional and minimum can be manipulated to create all kinds of orders
    '''
    def __init__(self, symbol, is_stock, qty, conditional, minimum, ordID=0):
        self.symbol = symbol
        self.is_stock = is_stock
        self.qty = qty # + indicates long, - indicates short
        # self.conditional = conditional
        # self.minimum = minimum
        self.ID = ordID  # CURRENTLY NOT IN USE

    '''check_conditino() all of them need to be moved into like strategy or execution or a standalone function.
    OR leave them here, and just input what is needed into the method?'''
    def check_condition(self):
        return false
        #maybe they should return either an Order or None

    def __repr__(self):
        return f"Order: symbol: ${self.symbol}, is_stock: {self.is_stock}, qty: {self.qty}, conditional: {self.conditional}, minimum: {self.minimum}, ordID: {sef.ordID}"

class MarketOrder(Order):
    '''since 1>0, the condition to execute order is always true'''
    def __init__(self, symbol, is_stock, qty, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, ordID=0)

    def check_condition(self):
        return True

    def __repr__(self):
        return f"MarketOrder: symbol: ${self.symbol}, is_stock: {self.is_stock}, qty: {self.qty}, conditional: True, ordID: {sef.ordID}"

class LimitOrder(Order):
    def __init__(self, symbol, is_stock, qty, limit_price, ordID=0):
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, ordID=0)
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
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, ordID=0)
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
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, ordID=0)
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
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, ordID=0)
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
        super().__init__(symbol=symbol, is_stock=is_stock, qty=qty, ordID=0)
        self.a = a
        self.b = b
        self.c = c
        self.d = d 

    def check_condition(self, price, init_trail_pc, vol, upward_vol, rec_price_velo):
        pass

    def __repr__(self):
        pass

def my_function(x: int, y: int) -> float:
    pass

class Strategy:
    '''
    this class is a parent class, in actual usage (backtest and live), this will get ovverriden
     by mystrat_x(Strategy)
     monitor_trades(): this gets run constantly when market is open
     the rest: get called sequentially when it's time to enter new positions. 
                this is done step by step by live/BT'''
    def __init__(self, broker: Broker, portfolio: Portfolio):
        self.portfolio = portfolio
        self.portfolio.updatePortfolio()
    
    # this is gonna exist in live and BT not here
    def run(self):
        while true:
            self.monitor_trades()
            self.check_trigger_event()
            # send smth to BT/live to say to wait or increment timestep 

    def check_trigger_event(self):
        if time == '3:45': # or early close day near end
            self.closing_event()
            

    def monitor_trades(self) -> List[Order]:
        '''this one runs at every time step. given live quotes, return any orders that need to be sent'''
        # orderbook = []
        # use self.portfolio.orders, loop through their conditionals
        #this includes querying for quotes of things that would need it
        #if any satisified, add to orders list
        # at end return order list (will usually be empty/None)
        pass

    def create_signals(self, data: pd.Dataframe) -> pd.Dataframe:
        '''this adds signals and returns data to function to use to make orders'''

    def closing_event(self):
        self.create_signals()
        self.signals2sentiment()
        self.sentiment2order()
        self.place_orders()

    def calcSentiment(data, t=None):
        '''
        - `dir` = f(previous day move size+direction, static bias, mean reversion, card count, TA)
        - `vol` = f(previous day move size, significant events, card count, TA, time since last big move)
        For now, this is a bogus function that randomly generates the numbers from a capped normal distribution.
        I will write this critical function after I finish most of the backtesting functions. I decided to vary the returns
        at the moment to give some more variety to the testing, as I do have the live sys running on a demo acct
        '''
        vol, dir = np.random.normal(.5, .2, 2) # gen 2 random values
        vol, dir = np.clip([vol, dir], 0, 1) # cap end values
        return vol, dir

    def sentiment2order(vol, dir):
        ''' converts vol and dir (sentiment) into a relative order'''
        conditions = [
            (0.3, 0.2, lambda: [{'strikeDist': -1.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # vol: 0-.3, dir: 0-.2 # 1 itm call + 2 atm puts
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]),
            (0.3, 0.8, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # vol: 0-.3, dir: .2-.8 # 1 atm call + 1 atm put
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]), 
            (0.3, 1.0, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 1 itm put
                                {'strikeDist': 1.5, 'exprDist': 2, 'side': 'put', 'qty': 1}]), 
            (0.7, 0.15, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # vol: .3-.7, dir: 0-.15 # 1 atm call + 1 otm put + 2 atm puts
                                {'strikeDist': -1.5, 'exprDist': 2, 'side': 'put', 'qty': 1},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]), 
            (0.7, 0.4, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1},  # vol: .3-.7, dir: 0-.4 # 1 atm call + 2 atm puts
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]),
            (0.7, 0.6, lambda: [{'strikeDist': -1.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # 1 itm call + 1 itm put
                                {'strikeDist': 1.5, 'exprDist': 2, 'side': 'put', 'qty': 1}]), 
            (0.7, 0.85, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 1 atm put
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]),
            (0.7, 1.0, lambda: [{'strikeDist': 1.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # 1 OTM call + 2 atm calls + 1 atm put
                                {'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]),
            (1.0, 0.25, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 2 otm puts + 1 atm put
                                {'strikeDist': -1.5, 'exprDist': 1, 'side': 'put', 'qty': 2},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]),
            (1.0, 0.75, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 ATM calls + 2 atm puts
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]),
            (1.0, 1.0, lambda: [{'strikeDist': 1.5, 'exprDist': 1, 'side': 'call', 'qty': 2}, # vol: .7-1, dir: .75-1 # 2 otm calls + 1 atm call + 2 atm puts
                                {'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}])
        ]
        for vol_threshold, dir_threshold, orders in conditions:
            if vol < vol_threshold and dir < dir_threshold:
                return orders()
