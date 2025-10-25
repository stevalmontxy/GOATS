from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd


class Position:
    '''This is just kinda an intermediary between portfolio -> trade -> position -> option.
    this allows possibility for stock positions in the future if desired
    
    I think I will put a stoploss/TP point in this area if I do add that to script'''
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
        for i, pos in enumerate(self.positions):
            if pos.symbol == symbol:
                print("symbol found")
                self.positions.pop(i)
                break

    @property
    def hasPositions(self):
        return len(self.positions) > 0
    
    def checkAcctValue(self, cash, positions):
        # after opening or closing all positions, check what else hasn't been logged, use checkoption value to add them to sum. add cash
        # acctValue = cash + positions
        pass

    def __repr__(self):
        return f"Portfolio: cash: ${self.cash}, # positions: {len(self.positions)}, Acct value: {self.acctValue}"
            

class Market: 
    '''this does NOT store data. I am currently not sure what would belong in this class'''
    pass
