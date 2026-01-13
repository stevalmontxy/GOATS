''' These are functions only useful to backtesting '''
from datetime import datetime, timedelta
from .classes import Portfolio

class Backtest:
    '''
    commission, starting val
    include tradelog (dataclass)
    log each: timestamp, realized pnl, unrealized pnl, current equity'''
    # def __init__(self, broker, portfolio, strategy, options_df, underly_df, commission_pct=0, commission_nom=0, initial_cash=100000, margin=1):
    def __init__(self, strategy, options_df, underly_df, commission_pct=0, commission_nom=0, initial_cash=100000, margin=1):
        self.broker = BTBroker(options_df=options_df, underly_df=underly_df, initial_cash=initial_cash)
        self.portfolio = Portfolio(initial_cash=initial_cash) # portfolio class
        self.strat = strategy # Strategy class
        self.commission_pct = commission_pct # percent
        self.commission_nom = commission_nom # or nominal amount
        self.margin = margin
        self.trade_log = [] # logs entries and exits
        self.nav_log = [] # logs NAV at end of each day

    def import_data(options_data, underly_data):
        # change out underly_df or options_df
        self.broker.options_df = options_data
        self.broker.underly_df = underly_data

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

            strat.monitor_trades()
            strat.check_trigger_event()
            # time += 1hr
            self.nav_log.append(self.broker.get_acct_details.nav)         
            date_current += timedelta(days=1)
        # return stats, equity_plot, portfolio, trade_log
    # END OF RUN()
    
    def calculate_commission(self, trade_value):
        """
        Calculate the commission for a trade.
        :param trade_value: The dollar value of the trade.
        :return: The commission as a float.
        """
        if self.commission_pct:
            return trade_value * self.commission_pct
        elif self.commission_nom:
            return self.commission_nom
        else:
            return 0  # Default if no commission is specified    

    def plot_profit(self):
        pass

    def plot_trades(self):
        pass

    def plot_signals(self):
        pass

    # def optimize(self, data, property, market, strategy, params):
        # pass
