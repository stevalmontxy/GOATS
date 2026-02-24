import datetime as dt

import pandas as pd
import numpy as np

from .core_objects import Portfolio, Option, Stock, Position
from .core_objects import Order, LimitOrder, ScheduledOrder

class Strategy:
    '''
    this class is a parent class, in actual usage (backtest and live), this will get ovverriden
    by mystrat_x(Strategy)
    monitor_trades(): this gets run constantly when market is open
    the rest: get called sequentially when it's time to enter new positions.
              this is done step by step by live/BT'''
    def __init__(self, broker, portfolio):
        self.broker = broker
        self.portfolio = portfolio
        # self.portfolio.updatePortfolio() #assume its initialized with an up to date portfolio

    def monitor_trades(self) -> list[Order]:
        '''this one runs at every time step.
        given live quotes, check current trades.
        place any orders necessary.
        output orders or whatever for logging purposes'''
        self.portfolio.update_portfolio()
        
        for o in self.portfolio.pseudo_orders[:]: # iterate over copy
            if isinstance(o, ScheduledOrder):
                if (o.check_condition(self.broker.now())): #if condition is met, place the order as regular
                    self.place_order(o)
                    self.portfolio.pseudo_orders.remove(o) 
                    print("SCHEDULED ORDER EXECUTED")
            else:
                price = self.broker.get_asset_value(o.asset) # maybe this is bid, ask
                if (o.check_condition(price)):
                    self.place_order(o)
                    self.portfolio.pseudo_orders.remove(o) 
                    print("PSUEDO ORDER EXECUTED")

        for o in self.portfolio.open_orders:
            # see if any real orders have been open for over a minute,
        #   if they have, "chase" the price (resubmit but at current bid/ask range)
            pass

    def place_order(self, ord):
        self.broker.place_order(ord)
        self.portfolio.add_order(ord)

    def cancel_order(self, ord):
        self.broker.cancel_order(ord)
        self.portfolio.remove_order(ord)
    
    def place_pseudo_order(self, ord):
        self.portfolio.add_pseudo_order(ord)
        #pseduo orders not seen on broker side

# overrite the following methods and create more events as fitting
    def check_trigger_event(self):
        # add more trigger conditions as fitting for strat
        print("Parent strat check trigger")
        if self.broker.now().time() == dt.time(15,30): # or early close day near end
            self.closing_event()
        # if time >= '4:00':
            # consider putting this logic in the live script
            # also use check open time for early clsoe days

    def closing_event(self):
        print("CLOSING EVENT TRIGGERED")
        # signals = self.create_signals() # uses historic data
        # sentiment = self.signals2sentiment(signals)
        # orders = self.sentiment2order(sentiment)
        # self.place_orders(orders)
        # return any necessary outputs up to check_trigger_event() for logging

    def create_signals(self) -> pd.DataFrame:
        '''this adds signals and returns data to function to use to make orders'''

    def calc_sentiment(self, data):
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

# If I want to keep it like this, we can convert delta orders to real orders within strat since strat has its own broker. 
# so delta orders won't be seen on the outside
    '''
        orders = self.broker.delta_order_to_orders(deltas)
    def sentiment2order(self, vol, dir):
        '''''' converts vol and dir (sentiment) into a relative order''''''
        conditions = [
            (0.3, 0.2, lambda: [{'strike_dist': -1.5, 'expr_dist': 2, 'side': 'call', 'qty': 1}, # vol: 0-.3, dir: 0-.2 # 1 itm call + 2 atm puts
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 2}]),
            (0.3, 0.8, lambda: [{'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 1}, # vol: 0-.3, dir: .2-.8 # 1 atm call + 1 atm put
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 1}]), 
            (0.3, 1.0, lambda: [{'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 1 itm put
                                {'strike_dist': 1.5, 'expr_dist': 2, 'side': 'put', 'qty': 1}]), 
            (0.7, 0.15, lambda: [{'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 1}, # vol: .3-.7, dir: 0-.15 # 1 atm call + 1 otm put + 2 atm puts
                                {'strike_dist': -1.5, 'expr_dist': 2, 'side': 'put', 'qty': 1},
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 2}]), 
            (0.7, 0.4, lambda: [{'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 1},  # vol: .3-.7, dir: 0-.4 # 1 atm call + 2 atm puts
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 2}]),
            (0.7, 0.6, lambda: [{'strike_dist': -1.5, 'expr_dist': 2, 'side': 'call', 'qty': 1}, # 1 itm call + 1 itm put
                                {'strike_dist': 1.5, 'expr_dist': 2, 'side': 'put', 'qty': 1}]), 
            (0.7, 0.85, lambda: [{'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 1 atm put
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 1}]),
            (0.7, 1.0, lambda: [{'strike_dist': 1.5, 'expr_dist': 2, 'side': 'call', 'qty': 1}, # 1 OTM call + 2 atm calls + 1 atm put
                                {'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 2},
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 1}]),
            (1.0, 0.25, lambda: [{'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 2 otm puts + 1 atm put
                                {'strike_dist': -1.5, 'expr_dist': 1, 'side': 'put', 'qty': 2},
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 1}]),
            (1.0, 0.75, lambda: [{'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 2}, # 2 ATM calls + 2 atm puts
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 2}]),
            (1.0, 1.0, lambda: [{'strike_dist': 1.5, 'expr_dist': 1, 'side': 'call', 'qty': 2}, # vol: .7-1, dir: .75-1 # 2 otm calls + 1 atm call + 2 atm puts
                                {'strike_dist': -.5, 'expr_dist': 2, 'side': 'call', 'qty': 1},
                                {'strike_dist': .5, 'expr_dist': 2, 'side': 'put', 'qty': 2}])
        ]
        for vol_threshold, dir_threshold, orders in conditions:
            if vol < vol_threshold and dir < dir_threshold:
                return orders()
'''

class DemoStrat(Strategy):
    # inherit everything from Strategy
    def check_trigger_event(self):
        # add more trigger conditions as fitting for strat
        if self.broker.now().time() == dt.time(15,30): # or early close day near end
            self.closing_event()

    def closing_event(self):
        print("DEMO CLOSING EVENT TRIGGERED")
        print("positions rn:")
        print(self.portfolio.positions)
        print("orders rn:")
        print(self.portfolio.open_orders)
        print("pseudo orders rn:")
        print(self.portfolio.pseudo_orders)
        print("BROKER positions")
        print(self.broker.positions)
        print("BROKER orders")
        print(self.broker.orders)

        stock_order = self.stock_helper_funct()
        self.place_order(stock_order)

        opt_order = self.opt_helper_funct()
        self.place_order(opt_order)

        pseudo_order = self.opt_helper_funct2(opt_order)
        self.place_pseudo_order(pseudo_order)

    def stock_helper_funct(self):
        return LimitOrder(symbol="AAPL", asset=Stock("AAPL"), qty=1)
    
    def opt_helper_funct(self):
        val = self.broker.get_asset_value(asset=Stock("AAPL"))
        opt = self.broker.get_closest_option(Option(strike=val-3,
                                            expr=self.broker.now()+dt.timedelta(days=4),
                                            side='C', underlying="AAPL"))
        return LimitOrder(symbol=opt.symbol, asset=opt, qty=1)

    def opt_helper_funct2(self, original_ord):
        place_time = self.broker.get_closest_open_date(self.broker.now() + dt.timedelta(days=2))
        place_time += dt.timedelta(hours=15, minutes=15)
        return ScheduledOrder(symbol=original_ord.symbol, asset=original_ord.asset, qty=-original_ord.qty, place_time=place_time)
