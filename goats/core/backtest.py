''' These are functions only useful to backtesting '''
from datetime import datetime, timedelta
from .classes import Portfolio

class Backtest:
    '''
    comision, starting val
    include tradelog (dataclass)
    log each: timestamp, realized pnl, unrealized pnl, current equity'''
    def __init__(self, broker: Broker, portfolio: Portfolio, strategy: Strategy, optionsdf, underlydf, comissionpct=0, comissionnom=0, initialCash=100000, margin=1):
        self.broker = broker
        self.portfolio = portfolio
        self.strat = strategy
        self.optionsdf = optionsdf
        self.underlydf = underlydf
        self.comissionpct = comissionpct # percent
        self.comissionnom = comissionnom # or nominal amount
        self.initialCash = initialCash
        self.margin = margin
        # self.trade_log = []

    def importdata(options_data, underly_data):
        # change out underlydf or optionsdf
        self.optionsdf = options_data
        self.underlydf = underly_data
        pass

    def set_strat(self, strat):
        self.strat = strat

    def run(self, startDate, daysForward=1, endDate=None, testLength=None):
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

        # for loop through time
            # strat.monitor_trades()
            # strat.check_trigger_event()
            # time += 1hr   
        
    def plotprofit(self):
        pass

    def plottrades(self):
        pass
    
    def plotsignals(self):
        pass

    # def optimize(self,data, property, market, strategy, params):
        # pass

