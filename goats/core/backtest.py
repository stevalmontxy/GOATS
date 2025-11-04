''' These are functions only useful to backtesting '''
from datetime import datetime, timedelta
from .classes import Portfolio

class Backtest:
    '''
    commission, starting val
    include tradelog (dataclass)
    log each: timestamp, realized pnl, unrealized pnl, current equity'''
    def __init__(self, broker, portfolio, strategy, options_df, underly_df, commission_pct=0, commission_nom=0, initial_cash=100000, margin=1):
        self.broker = broker
        self.portfolio = portfolio
        self.strat = strategy
        self.options_df = options_df
        self.underly_df = underly_df
        self.commission_pct = commission_pct # percent
        self.commission_nom = commission_nom # or nominal amount
        self.initial_cash = initial_cash
        self.margin = margin
        # self.trade_log = []

    def import_data(options_data, underly_data):
        # change out underly_df or options_df
        self.options_df = options_data
        self.underly_df = underly_data

    def set_strat(self, strat):
        self.strat = strat

    def run(self, start_date, days_forward=1, end_date=None, test_length=None):
        '''
        input dates as string, script will convert to datetime
        number of days is number of BUSINESS DAYS
        days_forward : how many days until expiration (ideally). script will look for longer DTEs if requested in unavailable
        '''
        date_current = datetime.strptime(start_date, "%m-%d-%Y")
        if end_date and test_length:
            raise ValueError("Provide either start_date or test_length, not both")
        elif end_date:
            end_date_current = datetime.strptime(end_date, "%m-%d-%Y")
            # timesteps = np.busday_count(start_date.date(), (end_date + timedelta(days=1)).date()) + 1
            # timesteps = 3
        elif test_length:
            raise ValueError("sorry, please use end_date parameter. test_length currently not working")
            # timesteps = test_length
        else:
            raise ValueError("end_date or test_length required")

        portfolio = Portfolio() # initialize
        first_day_init_bt(date_current, portfolio, self.options_df)

        while date_current + timedelta(days=days_forward) < end_date_current:  # until we get thru all the data

            # make sure start date is business day; skip past weekends and holidays
            while date_current not in self.options_df["[QUOTE_DATE]"].values:
                date_current += timedelta(days=1)

            self.Strategy.execute(self, date_current, self.options_df, self.underly_df, portfolio)
            date_current += timedelta(days=1)
        # return stats, equity_plot, portfolio, trade_log

        # for loop through time
            # strat.monitor_trades()
            # strat.check_trigger_event()
            # time += 1hr   

    def plot_profit(self):
        pass

    def plot_trades(self):
        pass

    def plot_signals(self):
        pass

    # def optimize(self,data, property, market, strategy, params):
        # pass
