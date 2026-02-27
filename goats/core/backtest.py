# Standard Imports
import datetime as dt

# Third Party Imports
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Local Imports
from .core_objects import Portfolio, Option, Stock, Position
from .core_objects import Order, LimitOrder, ScheduledOrder
# from goats.core.core_objects import Portfolio, Option, Stock, Position
# from goats.core.core_objects import Order, LimitOrder
# from ..broker.bt_broker import BTBroker # try using this as well as .goats.___ , i think it depends on where you execute it from


class Backtest:
    '''
    commission, starting val
    include tradelog (dataclass)
    log each: timestamp, realized pnl, unrealized pnl, current equity'''
    # def __init__(self, broker, portfolio, strategy, options_df, underly_df, commission_pct=0, commission_nom=0, initial_cash=100000, margin=1):
    def __init__(self, strategy, options_df, underly_df, commission_pct=0, commission_nom=0, margin=1):
        self.strat = strategy # Strategy class
        self.options_df = options_df
        self.underly_df = underly_df
        self.commission_pct = commission_pct # percent
        self.commission_nom = commission_nom # or nominal amount
        self.margin = margin
        self.trade_log = [] # logs entries and exits
        self.nav_log = [] # logs NAV at end of each day
        self.cash_log = []
        self.time_log = []
        # date_current var is local to the run method, and held by BTBroker class

    def import_data(options_data, underly_data):
        # can be used to change out underly_df or options_df
        self.broker.options_df = options_data
        self.broker.underly_df = underly_data

    def set_strat(self, strat):
        # can be used to change the strategy
        self.strat = strat

    def run(self, start_date, end_date=None):
        '''
        input dates as string, script will convert to datetime
        number of days is number of BUSINESS DAYS
        days_forward : how many days until expiration (ideally). script will look for longer DTEs if requested in unavailable
        '''
        start = dt.datetime.now() # used to track how long ran took
        current_time = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        end_date += pd.Timedelta(hours=16) # make sure to fully cover range of last day

        while current_time < end_date:  # until we get thru all the data
            # skip any time where market is inactive (weekends and early closes)
            while current_time not in self.underly_df.index:
                current_time += dt.timedelta(minutes=30)

            # make sure start date is business day; skip past weekends and holidays
            # while current_time not in self.options_df["[QUOTE_DATE]"].values:
                # current_time += dt.timedelta(days=1)

            self.strat.broker.set_time(current_time)

            print(f"current time is {current_time}")
            self.strat.monitor_trades()
            self.strat.check_trigger_event()
            self.nav_log.append(self.strat.broker.get_acct_value().portfolio_value)
            self.cash_log.append(self.strat.broker.cash)
            self.time_log.append(current_time)
            current_time += dt.timedelta(minutes=30)
        # print(self.nav_log)
        self.calc_stats()
        print(f'Run time: {dt.datetime.now() - start} seconds')
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

    def plot_nav(self, datetime_x_axis=False):
        ''' plots NAV, cash, and underlying simultaneously vs time
        datetime_x_axis: if True, plot time, else, "flatten" x axis'''
        if datetime_x_axis:
            x = self.time_log    
        else:
            x =  list(range(len(self.time_log)))

        # fig = go.Figure()
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Scatter(
                            x=x, y=self.cash_log,
                            mode='lines', name='Cash', fill='tozeroy'), secondary_y=False)

        fig.add_trace(go.Scatter(
                            x=x, y=self.nav_log,
                            mode='lines', name='NAV', fill='tozeroy'), secondary_y=False)

        underlying_prices = self.underly_df.loc[self.time_log, 'Close']
        fig.add_trace(go.Scatter(
                            x=x, y=underlying_prices,
                            mode='lines', name='Underlying'), secondary_y=True)

        fig.update_layout(title='Portfolio and Underlying Over Time',
        xaxis_title='Time', hovermode='x unified')
        # xaxis_title='Time', yaxis_title='value($)', hovermode='x unified')
        fig.update_yaxes(title_text="Value ($)", secondary_y=False)
        fig.update_yaxes(title_text="Underlying ($)", secondary_y=True)

        fig.show()

    '''
    def plot_underlying(self, datetime_x_axis=False):
        if datetime_x_axis:
            x = self.underly_df.index
        else:
            x =  list(range(len(self.underly_df.index)))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
                        x=x, y=self.underly_df.Close,
                        mode='lines', name='Cash'))

        fig.update_layout(title='Underlying Over Time',
        xaxis_title='time', yaxis_title='value($)', hovermode='x unified')
        fig.show()
        '''

    def calc_stats(self):
        start_time = self.time_log[0]
        end_time = self.time_log[-1]
        total_time = end_time - start_time
        pct_of_yr = total_time / dt.timedelta(days=365)
        net_pl = self.nav_log[-1] - self.nav_log[0]
        rate_return = net_pl / self.nav_log[0]
        underly_return = (self.underly_df["Close"].loc[end_time] - 
                          self.underly_df["Close"].loc[start_time]) / self.underly_df["Close"].loc[start_time]
        self.stats = {
            "Start": start_time,
            "End": end_time,
            "Total Time": total_time, 
            "Net P/L ($)": net_pl, 
            "Total Return (%)": rate_return*100,
            "Annualized Return (%)": ((1 + rate_return) ** (1/pct_of_yr) - 1)*100,
            "Underly Return (%)": underly_return*100,
            # "Max Drawdown (%)": 
            # "Win Rate (%)":
        }

    def show_stats(self):
        # stats_series = pd.Series(self.stats, name="Results")
        print("="*30)
        print('Run Summary')
        # print(stats_series)
        print(pd.Series(self.stats))
        print("="*30)

    def show_trade_log(self):
        # show trade log as table
        pass

    def plot_profit(self):
        pass

    def plot_trades(self):
        pass

    def plot_signals(self):
        pass

    # def optimize(self, data, property, market, strategy, params):
        # pass
