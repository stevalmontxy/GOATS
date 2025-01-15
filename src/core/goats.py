from datetime import datetime, timedelta, date
import datetime as dt
import numpy as np
import pandas as pd
# from sentiment_v1 import calcSentiment, sentiment2order


class Position:
    '''This is just kinda an intermediary between portfolio -> trade -> position -> option.
    this allows possibility for stock positions in the future if desired
    
    I think I will put a stoploss/TP point in this area if I do add that to script'''
    def __init__(self, option=None, stock=None, symbol=None, entryDate=None, exitDate=None, qty=1, posID=0):
        self.option = option
        self.stock = stock
        self.qty = qty
        self.symbol = symbol
        self.entryDate = entryDate # date(NOT datetime)
        self.exitDate = exitDate # date(NOT datetime)
        self.ID = posID # position ID and option ID are both self referenced as ID
                        # posID: id number within active positions. an option will be associated with a posID throughout its holding,
                        #        then the posID will be reused by other positions

    def __repr__(self):
        return (f"Position(ID={self.ID}, symbol='{self.symbol}', qty={self.qty}, "
                f"entryDate={self.entryDate}, exitDate={self.exitDate}, "
                f"option={self.option}, stock={self.stock})")


class Option:
    '''
    strike: price (float)
    expr: expiration (date, can init as date(time) or str YYYY-MM-DD)
    side: 'call' or 'put' (str)
    '''
    def __init__(self, strike, expr, side, optID=0):
        self.strike = strike
        self.expr = expr if isinstance(expr, date) else datetime.strptime(expr, "%Y-%m-%d")
        self.side = side
        self.ID = optID # optID is different from posID. referenced as either position.ID or option.ID
                        # optID: id number of option, never to be reused throughout a backtest (or lifetime unless reset maybe)
                        # for ex, the 5th option taken by script will have optID of 5, posID of 1, assuming the script holds two at a time, and sells in order

    def __repr__(self):
        return f"Option: strike: ${self.strike}, expr: {self.expr}, side: {self.side}, optID: {self.ID}"


class Portfolio:
    '''
    this holds the properties of the account.
    '''
    def __init__(self, timesteps=None, initialCapital=100000):
        self.cash = initialCapital # this is set at instantiation, and changed over time. don't need to track over time
        self.positions = []
        # self.thisRound = {} # ID: n, value: $x, add opened or clsoed when checked, use this to calc acct value
        # self.trade_log = []
        self.acctValue = initialCapital # acct value over time

    def addPosition(self, option, symbol, qty, entryDate, exitDate):
        '''entry date should be input of date.today(). if position is being updated, it will be None'''
        pos = Position(option=option, symbol=symbol, entryDate=entryDate, exitDate=exitDate, qty=qty)
        self.positions.append(pos)

    def removePosition(self, symbol):
        '''symbol: string'''
        for i in range(0,len(self.positions)): 
            if self.positions[i].symbol == symbol:
                self.positions.pop(i)
                break

    def openPosition(self, time, qty, option=None, stock=None):
        '''THIS IS FOR BACKTESTING. use addPosition for live
        time: datetime YYYY-MM-DD HH:MM
        qty: float
        option: Option object
        Stock: Stock object (not defined)
        '''
        value = self.getOptionValue(option.expr, option.strike, option.strike, time)
        self.positions[option.ID] = {"option": option, "open_time": time, "initial_value": value}
        self.cash -= 100*value
        self.trade_log.append(f"Opened position ID: {option.ID} at time: {time} at ${value}")

    def closePosition(self, option, time):
        '''THIS IS FOR BACKTESTING. use removePosition for live'''
        # remove an option from positions list, find value at close time, add to trade log
        value = self.getOptionValue(option.expr, option.strike, option.strike, time)
        self.positions[option.ID].delete #or whatever ~~~~~~~~~~~
        '''
        
                     
        FIGURE THIS OUT    
        
        
        '''
        cash += 100*value
        self.trade_log.append(f"closed position ID: {option.ID} at time: {time} at ${value}")
        pass

    @property
    def hasPositions(self):
        return len(self.positions) > 0
    
    def checkAcctValue(self, cash, positions):
        # after opening or closing all positions, check what else hasn't been logged, use checkoption value to add them to sum. add cash
        # acctValue = cash + positions
        pass

    def __repr__(self):
        return f"Portfolio: cash: ${self.cash}, # positions: {len(self.positions)}, Acct value: {self.acctValue}"

class Strategy:
    '''
    sentiment: object of the sentiment class. this way I can swap between sentimentv1 or sentimentv2 n stuff.
    f: fraction of assets to trade (float)
    '''
    def __init__(self, Sentiment, f, morningSchedRun='10:00', closingSchedRun="15:30"):
        self.f = f
        self.Sentiment = Sentiment
        self.morningSchedrun = morningSchedRun # this is time, in 24hr
        self.closingSchedRun = closingSchedRun # this is time, in 24hr
        # also need a lot more of course

    def morningScript(self, dateCurrent, optionsdf, underlydf, portfolio):
        '''
        datecurrent: for logging pursposes
        optionsdf: is ONLY for the current time. options data
        underlydf: is OHLC data for the last while of underlying stock
        portfolio: holds the current positions, capital, trade log, ye
        '''
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
            I will def want to put another func here to find the right positions n stuff
            '''
            ID = 1
            ID2 = 2
            call = Option(12,12,12,ID)
            put= Option(13,13,13,ID2)
            portfolio.openPosition(time, callqty, call)
            portfolio.openPosition(time, putqty, put)
            #  based on differences, decied how to modify and close n shit
        else:
            self.firstDayInit(dateCurrent, optionsdf, underlydf, portfolio)

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

    def firstDayInit(self, dateCurrent, optionsdf, underlydf, portfolio):
        '''This is a script for when there are no positions. runs in place of morning script, no closing script that day'''
        # calc vol and dir
        # since no positions,
        # buy positions
        # log to trade list in portfolio
        pass

    def execute(self, dateCurrent, optionsdf, underlydf, portfolio):
        '''This script is only for backtesting implementation. It runs on a day where there are already positions held.
        It will open new ones and close old ones
        After I finish bacis setup, the script will start doing things like monitoring price throughout day, selling before close, holding longer,
        adding "deviations" 
        datecurrent: datetime: to get the right data
        '''
        # get morning data
        currentOptionsdf, currentUnderlydf = self.selectData(dateCurrent, self.morningSchedrun, optionsdf, underlydf)
        self.morningScript(currentOptionsdf, currentUnderlydf)
        # get closeing data
        currentOptionsdf, currentUnderlydf = self.selectData(dateCurrent, self.closingSchedRun, optionsdf, underlydf)
        self.closingScript(currentOptionsdf, currentUnderlydf)

    def selectData(self, schedRunTime, optionsdf, underlydf):
        '''
        this is a script for backtesting implementation
        this script will return the options data at the given time and underlying data up to the given time
        inputs: scheduled runtime, optionsdf underlyingdf
        outputs: currentOptionsdf, currentUnderlydf
        '''
        return 1,1
        

class Market: 
    '''this does NOT store data. I am currently not sure what would belong in this class'''
    pass
