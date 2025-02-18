''' These are functions only useful to backtesting '''
from datetime import datetime, timedelta
from .classes import Portfolio


def firstDayInitBT():
    pass

def orderMakerBT(orders, time=None):
    '''     orders: List of dictionaries, each containing strikeDist, exprDist, side, qty;
            example:        orders = [
                                {'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1},
                                {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1} ]
    '''
    pass
    # underlyingLast = df["[UNDERLYING_LAST]"]
    # goalStrike = underlyingLast+strikeDist
    # goalExpr = time + timedelta(days=exprDist)
    # # find closest strike
    # # find closest expr
    # # if side == 'call': not needed, same process for call or put. strike dist is properly set to acct for either case
    # option = Option(strike, expr, side)
    # Portfolio.openPosition(port, time, qty, option)

def findClosestOption():
    '''Completed for live, need to do for backtesting'''
    pass

def findClosestOpenDayBT():
    pass

def openPosition(self, time, qty, option=None, stock=None):
    '''THIS IS FOR BACKTESTING. use addPosition for live
    time: datetime YYYY-MM-DD HH:MM
    qty: float
    option: Option object
    Stock: Stock object (not defined)
    '''
    value = getOptionValue(option.expr, option.strike, option.strike, time)
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

def getOptionValue(self, expirDate, strike, side, time):
    '''
    expirDate: datetime
    strike price: float
    side: 'call' or 'put' (string)
    time: datetime day+hr to check quote at
    '''
    print(type(time))
    quoteDate = time.replace(hour=0, minute=0)
    quoteTimeHour = time.hour + time.minute/60
    dfSlice = df[(df["[QUOTE_DATE]"] == quoteDate) & (df["[STRIKE]"]==float(strike)) & (df["[EXPIRE_DATE]"]==expirDate) & (df["[QUOTE_TIME_HOURS]"]==quoteTimeHour) ] # gets a specific quote @ given time

    if side == 'call':
        return float(dfSlice.iloc[0]["[C_LAST]"])
    else:  # for puts
        return float(dfSlice.iloc[0]["[P_LAST]"])     
        



class Backtest:
    '''This package executes the back test. this iterates through the time series.'''
    def __init__(self, strategy, optionsdf, underlydf, comissionpct=0, comissionnom=0, initialCash=100000, margin=1): # FIGURE OUT IF I ISHOULD INIVIALIZE CASH HERE OR LATER
        self.Strategy = strategy
        self.optionsdf = optionsdf
        self.underlydf = underlydf
        self.comissionpct = comissionpct # perfect
        self.comissionnom = comissionnom # or nominal amount
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
        firstDayInitBT(dateCurrent, portfolio, self.optionsdf)
        
        while dateCurrent + timedelta(days=daysForward) < endDateCurrent:  # until we get thru all the data

            # make sure start date is business day; skip past weekends and holidays
            while dateCurrent not in self.optionsdf["[QUOTE_DATE]"].values:
                dateCurrent += timedelta(days=1)

            self.Strategy.execute(self, dateCurrent, self.optionsdf, self.underlydf, portfolio)
            dateCurrent += timedelta(days=1)
        # return stats, equityPlot, portfolio, tradebook
    
    def execute(self):
        '''i suspect I will use this just to call closingScriptBT, but maybe in the future if I want to exit earlier or set up trailing I could do this'''
        pass
      
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


from .sentiment_v1 import calcSentiment, sentiment2order
'''These are the default functions to import into Strategy. 
In the future if sentiment V2 exists, these can be replaced during class initialization'''

class Strategy:
    '''
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