''' These are functions only useful to backtesting '''
from datetime import datetime, timedelta
from .classes import Portfolio

class Backtest:
    '''
    comision, starting val
    include tradelog (dataclass)
    log each: timestamp, realized pnl, unrealized pnl, current equity'''
    pass
        # self.trade_log = []

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
