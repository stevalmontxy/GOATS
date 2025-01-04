from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class SentimentV1:
    '''
    here i hold the values for vol and bias beliefs
    they are calculated using methods (or functions?)
    '''
    # elsewhere, an f will be defined, but that is a strategy parameter, not a sentiment parameter
    def __init__(self, timesteps):
        self.vol = [.5] * (timesteps+1) # volatility; value from 0 to 1, 0 being absolutely no belief in motion(100% sideways), 1 being expecting huge move
        self.dir = [.5] * (timesteps+1) # direction; value from 0 to 1, .5 being even, 1, being fully upside
        # a .5 dir doesn't mean a belief in sideways market, it means a neutral belief in terms of direction. vol decides how sideways

    # def calcVol(self, t, data) -> None: 
    #     '''
    #     - `vol` = f(previous day move size, significant events, card count, TA, time since last big move)
    #     - if vol belief has multiple dimensions, maybe that can be factored in for ideal position DTE
    #     '''
    #     self.vol[t] =  .6
        
    # def calcDir(self, t, data):
    def calcSentiment(self, t, data):
        '''
         - `dir` = f(previous day move size+direction, static bias, mean reversion, card count, TA)
         '''
        self.vol[t] =  .6
        self.dir[t] =  .6

    @staticmethod
    def sentiment2order1(vol, dir):
        conditions = [
            (0.3, 0.2, lambda: SentimentV1.orderMaker('1itmcall', '2atmput')), #vol: 0-.3, dir: 0-.2
            (0.3, 0.8, lambda: SentimentV1.orderMaker('1atmcall', '1atmput')), # vol: 0-.3, dir: .2-.8
            (0.3, 1.0, lambda: SentimentV1.orderMaker('2atncall', '1itmput')),
            (0.7, 0.15, lambda: SentimentV1.orderMaker('1atmcall', '1otmcall+2atmcall')), # vol: .3-.7, dir: 0-.15
            (0.7, 0.4, lambda: SentimentV1.orderMaker('1atmcall', '2atmput')), # vol: .3-.7, dir: 0-.4
            (0.7, 0.6, lambda: SentimentV1.orderMaker('1itmcall', '1itmput')),
            (0.7, 0.85, lambda: SentimentV1.orderMaker('2atmcall', '1atmput')),
            (0.7, 1.0, lambda: SentimentV1.orderMaker('1OTMcall+2atmcall', '1atmput')),
            (1.0, 0.25, lambda: SentimentV1.orderMaker('2atmcall', '2otmput+1atmput')), 
            (1.0, 0.75, lambda: SentimentV1.orderMaker('2ATMcall', '2atmput')),
            (1.0, 1.0, lambda: SentimentV1.orderMaker('2otmcall+1atmcall', '2atmput')), # vol: .7-1, dir: .75-1
        ]
        '''strike, expr, side, qty
           strike(distance), expr(distance), side, qty '''
        for vol_threshold, dir_threshold, action in conditions:
            if vol < vol_threshold and dir < dir_threshold:
                action() # this calls the lambda func which calls the orderMaker method
                # return

    @staticmethod
    def orderMakerBt(time, strikeDist, exprDist, side, qty):
        underlyingLast = df["[UNDERLYING_LAST]"]
        goalStrike = underlyingLast+strikeDist
        goalExpr = time + timedelta(days=exprDist)
        # find closest strike
        # find closest expr
        # if side == 'call': not needed, same process for call or put. strike dist is properly set to acct for either case
        option = Option(strike, expr, side)
        Portfolio.openPosition(port, ti me, qty, option)

    @staticmethod
    def orderMakerLive(time, strikeDist, exprDist, side, qty):
        underlyingLast = df["[UNDERLYING_LAST]"]
        goalStrike = underlyingLast+strikeDist
        goalExpr = time + timedelta(days=exprDist)
        # find closest strike
        # find closest expr
        # if side == 'call': not needed, same process for call or put. strike dist is properly set to acct for either case
        option = Option(strike, expr, side)
        Portfolio.openPosition(port, ti me, qty, option)


    def __repr__(self):
        # Format summary statistics or show partial data for readability.
        vol_summary = f"First 5 values: {self.vol[:5]}" if len(self.vol) > 5 else f"Values: {self.vol}"
        dir_summary = f"First 5 values: {self.dir[:5]}" if len(self.dir) > 5 else f"Values: {self.dir}"
        
        # Build the string representation.
        return (
            f"Sentiment Object:\n"
            f"- Volatility Beliefs (vol): {vol_summary}\n"
            f"- Directional Beliefs (dir): {dir_summary}\n"
            f"- Total Time Steps: {len(self.vol)}"
            )


class Position:
    '''This is just kinda an intermediary between portfolio -> trade -> position -> option.
    this allows possibility for stock positions in the future if desired
    
    I think I will put a stoploss/TP point in this area if I do add that to script'''
    def __init__(self, option=None, stock=None, quantity=1, posID=0):
        self.option = option
        self.stock = stock
        self.quantity = quantity
        self.ID = posID # position ID and option ID are both self referenced as ID
                        # posID: id number within active positions. an option will be associated with a posID throughout its holding,
                        #        then the posID will be reused by other positions


class Option:
    '''
    this holds option information
    '''
    def __init__(self, strike, expr, side, optID=0):
        self.strike = strike
        self.expr = expr # expiration date (str, YYYY-MM-DD)
        self.side = side # call or put
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
        self.positions = {}
        self.thisRound = {} # ID: n, value: $x, add opened or clsoed when checked, use this to calc acct value
        self.trade_log = []
        self.acctValue = [initialCapital] # acct value over time

    def openPosition(self, time, qty, option=None, stock=None):
        '''Add to positions
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
        # remove an option from positions list, find value at close time, add to trade log
        value = self.getOptionValue(option.expr, option.strike, option.strike, time)
        self.positions[option.ID].delete #or whatever ~~~~~~~~~~~
        '''
        
        
        
        
        FIGURE THIS OUT
        
        
        
        
        '''
        cash += 100*value
        self.trade_log.append(f"closed position ID: {option.ID} at time: {time} at ${value}")
        pass

    def getOptionValue(self, expirDate, strike, side, time):#:datetime):
        '''
        expirDate- datetime
        strike price- float
        side- 'call' or 'put' (string)
        time- datetime day+hr to check quote at
        '''
        print(type(time))
        quoteDate = time.replace(hour=0, minute=0)
        quoteTimeHour = time.hour + time.minute/60
        dfSlice = df[(df["[QUOTE_DATE]"] == quoteDate) & (df["[STRIKE]"]==float(strike)) & (df["[EXPIRE_DATE]"]==expirDate) & (df["[QUOTE_TIME_HOURS]"]==quoteTimeHour) ] # gets a specific quote @ given time

        if side == 'call':
            return float(dfSlice.iloc[0]["[C_LAST]"])
        else:  # for puts
            return float(dfSlice.iloc[0]["[P_LAST]"])     

    @property
    def hasPositions(self):
        return len(self.positions) > 0
    
    def checkAcctValue(self, cash, positions):
        # after opening or closing all positions, check what else hasn't been logged, use checkoption value to add them to sum. add cash
        # acctValue = cash + positions
        pass


class Strategy:
    '''
    sentiment is an object of the sentiment class. this way I can swap between sentimentv1 or sentimentv2 n stuff. MAYBE I SHOULD MAKE EACH ONE BE A SUBCLASS!!!!
    f is a float
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
            I will def want to put another func here to find the right positinos n stuff
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
        '''script that executes near close of the day, granted theose positions have been held for more than a day (to not trigger PDT rule)'''
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
    '''
    this does NOT store data. it only helps to fetch good options that fit what Strategy wants
    '''
    def findClosestOption():
        pass # OR I could ahve it find a list of the closest, and let the strategy decide. or I could feed in what strat is looking for, and let it make a decision here


class Backtest:
    '''This package executes the back test. this iterates through the time series.'''
    def __init__(self, strategy, optionsdf, underlydf, comissionpct=0, comissionnom=0, initialCash=100000, margin=1): # FIGURE OUT IF I ISHOULD INIVIALIZE CASH HERE OR LATER
        self.Strategy = strategy
        self.optionsdf = optionsdf
        self.underlydf = underlydf
        self.comissionpct = comissionpct
        self.comissionnom = comissionnom
        self.initialCash = initialCash
        self.margin = margin

        if self.comissionpct and self.comissionnom:
                    raise ValueError("You can specify either a percentage commission or a nominal commission, not both.")

    def run(self, startDate, daysForward=1, endDate=None, testLength=None): # market
        '''
        input dates as string, script will convert to datetime
        number of days is number of BUSINESS DAYS
        daysForward : how many days until expiration (ideally). script will look for longer DTEs if requested in unavailable
        '''
        dateCurrent = datetime.strptime(startDate, "%m-%d-%Y")
        if endDate and testLength:
            raise ValueError("Provide either startDate or testLength, not both")
        elif endDate:
            endDateCurrent = datetime.strptime(endDate, "%m-%d-%Y")
            # timesteps = np.busday_count(startDate.date(), (endDate + timedelta(days=1)).date()) + 1
            # timesteps = 3
        elif testLength:
            raise ValueError("sorry, please use endDate parameter. testLength currently not working")
            # timesteps = testLength
        else:
            raise ValueError("endDate or testLength required")
        
        portfolio = Portfolio() # initialize
        self.Strategy.firstDayInit(dateCurrent, portfolio, self.optionsdf)
        
        # for t in range(1,4+1):
        while dateCurrent + dt.timedelta(days=daysForward) < endDateCurrent:  # until we get thru all the data

            # make sure start date is business day; skip past weekends and holidays
            while dateCurrent not in self.optionsdf["[QUOTE_DATE]"].values:
                dateCurrent += pd.Timedelta(days=1)

            self.Strategy.execute(self, dateCurrent, self.optionsdf, self.underlydf, portfolio)
        # return stats, equityPlot, portfolio, tradebook
        return True
      
    def calculate_comission(self, trade_value):
        """
        Calculate the commission for a trade.
        :param trade_value: The dollar value of the trade.
        :return: The commission as a float.
        """
        if self.comissionpct:
            return trade_value * self.comissionpct
        elif self.comissionnom:
            return self.comissionnom
        else:
            return 0  # Default if no commission is specified        
        
    def optimize(self,data, property, market, strategy, params):
        pass

    def plot(self):
        pass