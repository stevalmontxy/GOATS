from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd


class Portfolio:
    '''
    this holds the properties of the account.
    '''
    def __init__(self, timesteps=None, initialCapital=100000):
        self.cash = initialCapital # this is set at instantiation, and changed over time. don't need to track over time
        self.positions = []
        self.acctValue = initialCapital # acct value over time
        self.orderbook = []
        self.pseudoorderbook = [] # this is like limit option orders, which I don't actually send until market is near price

    # maybe use kwargs to "overload" for options or stock 
    def addPosition(self, option, symbol, qty, entryDate, entryPrice):
        '''the symbol entry helps to locate entries a lot easier
        entry date should be input of date.today(). if position is being updated, it will be None'''
        pos = Position(option=option, symbol=symbol, entryDate=entryDate, exitDate=exitDate, qty=qty)
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

    def getAcctValue(self, cash, positions):
        # after opening or closing all positions, check what else hasn't been logged, use checkoption value to add them to sum. add cash
        # acctValue = cash + positions
        pass

    def __repr__(self):
        return f"Portfolio: cash: ${self.cash}, # positions: {len(self.positions)}, Acct value: {self.acctValue}"


class Position:
    '''This is just kinda an intermediary between portfolio -> position -> option.
    this allows possibility for stock positions in the future if desired
    orders/trades elsewhere in the portfolio can be linked to positions
    '''
    def __init__(self, option=None, stock=None, symbol=None, entryDate=None, exitDate=None, qty=1, value=None, posID=0):
        self.option = option
        self.stock = stock
        self.qty = qty
        self.symbol = symbol
        self.entryDate = entryDate # date(NOT datetime)
        self.exitDate = exitDate # date(NOT datetime)
        self.value = value
        self.ID = posID # position ID and option ID are both self referenced as ID
                        # posID: id number within active positions. an option will be associated with a posID throughout its holding,
                        #        then the posID will be reused by other positions

    def __repr__(self):
        return (f"Position(ID={self.ID}, symbol='{self.symbol}', qty={self.qty}, "
                f"entryDate={self.entryDate}, exitDate={self.exitDate}, "
                f"option={self.option}, stock={self.stock})")


class Stock:
    '''
    symbol
    price
    def newprice()
    '''
    pass

class Option:
    '''
    strike: price (float)
    expr: expiration (date, can init as date(time) or str YYYY-MM-DD)
    side: 'call' or 'put' (str)
    current price() '''
    def __init__(self, strike, expr, side, optID=0):
        self.strike = strike
        self.expr = expr if isinstance(expr, date) else datetime.strptime(expr, "%Y-%m-%d")
        self.side = side
        self.ID = optID # optID is different from posID. referenced as either position.ID or option.ID
                        # optID: id number of option, never to be reused throughout a backtest (or lifetime unless reset maybe)
                        # for ex, the 5th option taken by script will have optID of 5, posID of 1, assuming the script holds two at a time, and sells in order

    def __repr__(self):
        return f"Option: strike: ${self.strike}, expr: {self.expr}, side: {self.side}, optID: {self.ID}"


class Order:
    pass

class MarketOrder(Order):
    pass

class LimitOrder(Order):
    pass

class StopOrder(Order):
    pass

class TrailingStopOrder(Order):
    pass

class SLTPOrder(Order):
    pass

class CinchingTrailingOrder(Order):
    '''maybe dynamic trailing order
    cinching trailing order
    honing trailing'''
    pass


class Strategy:
    '''
    this class is a parent class, in actual usage (backtest and live), this will get ovverriden by mystrat_x and that will be used
    Strategy() is a class that is used for the backtester. while the BT class handles things related to data and time,
    the Strategy class houses the backtesting equivalents of the primary functions, and the execute() method handles the scheduler part
    calcSentiment: function from sentiment script. designed to be be swappable
    sentiment2order: function from sentiment script
    morningSchedRun: time to run morning script (currently none) in 24hr str
    closingSchedRun: time to run closing script in 24hr str
            '''
    def __init__(self, calcSentiment=calcSentiment, sentiment2order=sentiment2order, morningSchedRun=None, closingSchedRun="15:30"):
        # self.f = f not yet
        self.calcSentiment = calcSentiment
        self.sentiment2order = sentiment2order
        self.morningSchedRun = morningSchedRun
        self.closingSchedRun = closingSchedRun
    
    '''
here are all the functions associated with sentiment. I am using the v1 so when I decide in the future
to derive order sizing differently i can keep this original
'''
# import numpy as np

    def execute(self, dateCurrent, optionsdf, underlydf, portfolio):
        '''this script acts the same as crontab on the live running system. it executes the scheduled scripts as their scheduled times. Assu
        After I finish basic setup, the script will start doing things like monitoring price throughout day, selling before close, holding longer,
        adding "deviations"



        I WAS WORKING HERE
        BASICALLY, I think first daya init is done and I need to do clsoing scirpt. I am staying in strategy class, and will worry abt backtesting class next
        datecurrent: datetime: to get the right data
        '''
        # get morning data
        # currentOptionsdf, currentUnderlydf = self.selectData(dateCurrent, self.morningSchedrun, optionsdf, underlydf)
        # self.morningScript(currentOptionsdf, currentUnderlydf)
        # get closeing data
        currentOptionsdf, currentUnderlydf = self.selectData(dateCurrent, self.closingSchedRun, optionsdf, underlydf)
        self.closingScript(currentOptionsdf, currentUnderlydf)  

    def firstDayInit(self, dateCurrent, optionsdf, underlydf, portfolio):
        '''This is a script for when there are no positions. runs in place of morning script, no closing script that day'''
        # calc vol and dir
        # since no positions,
        # buy positions
        # log to trade list in portfolio
        underlydfCurrent, latestPrice = self.selectData()
        vol, dir = self.calcSentiment(underlydfCurrent)
        orders = sentiment2order(vol, dir)
        trade_log = []
        port, trade_log = orderMakerBT(orders, latestPrice, port, trade_log)
        return port, trade_log
        
    def closingScript(self, dateCurrent, optionsdf, underlydf, portfolio):
        '''script that executes near close of the day, granted those positions have been held for more than a day (to not trigger PDT rule)'''
        # at EOD, sell the ones from previous day. ye. or hold.  ye.
        if portfolio.hasPositions:
            # check current positions-> calc implied sentiment from portfolio
            # calc new vol and dir
            vol = self.Sentiment.calcVol(1,1)
            dir = self.Sentiment.calcDir(1,1)
            
            morningTimeObj = datetime.strptime(self.morningSchedrun, "%H:%M").time()
            time = datetime.combine(dateCurrent.date(), morningTimeObj)

            call = vol*dir
            put  = vol*(1-dir)
            callqty = 1
            putqty=1
            '''
            I will def want to put another func here to find the right positinos n stuff
            '''
            ID = 1
            ID2 = 2
            call = Option(12,12,12,ID)
            put= Option(13,13,13,ID2)
            portfolio.openPosition(time, callqty, call)
            portfolio.openPosition(time, putqty, put)
            #  based on differences, decied how to modify and close n shit
        pass
   
    def selectData():
        pass

    '''
    def morningScript(self, dateCurrent, optionsdf, underlydf, portfolio):
        '''         '''
        datecurrent: for logging pursposes
        optionsdf: is ONLY for the current time. options data
        underlydf: is OHLC data for the last while of underlying stock
        portfolio: holds the current positions, capital, trade log, ye
        '''         '''
        if portfolio.hasPositions:
            # check current positions-> calc implied sentiment from portfolio
            # calc new vol and dir
            vol = self.Sentiment.calcVol(1,1)
            dir = self.Sentiment.calcDir(1,1)
            
            morningTimeObj = datetime.strptime(self.morningSchedrun, "%H:%M").time()
            time = datetime.combine(dateCurrent.date(), morningTimeObj)

            call = vol*dir
            put  = vol*(1-dir)
            callqty = 1
            putqty=1
            #I will def want to put another func here to find the right positions n stuff
            ID = 1
            ID2 = 2
            call = Option(12,12,12,ID)
            put= Option(13,13,13,ID2)
            portfolio.openPosition(time, callqty, call)
            portfolio.openPosition(time, putqty, put)
            #  based on differences, decied how to modify and close n shit
        else:
            self.firstDayInit(dateCurrent, optionsdf, underlydf, portfolio) '''


class defaultStrat(Strategy):
    '''this is the ideal implementation of it
    vol and dir are defined here. and how to get thema re defined here. but the basic funcs are defined in parent class
    def make signals()
    def choose what to buy()
    then these act on portfolio via order -> trade
    '''

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

from dataclasses import dataclass

@dataclass
class Trade:
    '''
    only used for backtest logging
    symbol, qty, price, side, timestamp, order, pnl
    after bt finish running, convert to pd dataframe'''
    pass

class Backtest:
    '''
    comision, starting val
    include tradelog (dataclass)
    log each: timestamp, realized pnl, unrealized pnl, current equity'''
    pass
        # self.trade_log = []
