class Strategy:
    '''
    this class is a parent class, in actual usage (backtest and live), this will get ovverriden
     by mystrat_x(Strategy)
     monitor_trades(): this gets run constantly when market is open
     the rest: get called sequentially when it's time to enter new positions. 
                this is done step by step by live/BT'''
    def __init__(self, broker: Broker, portfolio: Portfolio):
        self.portfolio = portfolio
        self.portfolio.updatePortfolio()
    
    # this is gonna exist in live and BT not here
    def run(self):
        while true:
            self.monitor_trades()
            self.check_trigger_event()
            # send smth to BT/live to say to wait or increment timestep 

    def check_trigger_event(self):
        if time == '3:45': # or early close day near end
            self.closing_event()
            

    def monitor_trades(self) -> List[Order]:
        '''this one runs at every time step. given live quotes, return any orders that need to be sent'''
        # orderbook = []
        # use self.portfolio.orders, loop through their conditionals
        #this includes querying for quotes of things that would need it
        #if any satisified, add to orders list
        # at end return order list (will usually be empty/None)
        pass

    def create_signals(self, data: pd.Dataframe) -> pd.Dataframe:
        '''this adds signals and returns data to function to use to make orders'''

    def closing_event(self):
        self.create_signals()
        self.signals2sentiment()
        self.sentiment2order()
        self.place_orders()

    def calcSentiment(data, t=None):
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

    def sentiment2order(vol, dir):
        ''' converts vol and dir (sentiment) into a relative order'''
        conditions = [
            (0.3, 0.2, lambda: [{'strikeDist': -1.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # vol: 0-.3, dir: 0-.2 # 1 itm call + 2 atm puts
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]),
            (0.3, 0.8, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # vol: 0-.3, dir: .2-.8 # 1 atm call + 1 atm put
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]), 
            (0.3, 1.0, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 1 itm put
                                {'strikeDist': 1.5, 'exprDist': 2, 'side': 'put', 'qty': 1}]), 
            (0.7, 0.15, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # vol: .3-.7, dir: 0-.15 # 1 atm call + 1 otm put + 2 atm puts
                                {'strikeDist': -1.5, 'exprDist': 2, 'side': 'put', 'qty': 1},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]), 
            (0.7, 0.4, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1},  # vol: .3-.7, dir: 0-.4 # 1 atm call + 2 atm puts
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]),
            (0.7, 0.6, lambda: [{'strikeDist': -1.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # 1 itm call + 1 itm put
                                {'strikeDist': 1.5, 'exprDist': 2, 'side': 'put', 'qty': 1}]), 
            (0.7, 0.85, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 1 atm put
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]),
            (0.7, 1.0, lambda: [{'strikeDist': 1.5, 'exprDist': 2, 'side': 'call', 'qty': 1}, # 1 OTM call + 2 atm calls + 1 atm put
                                {'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]),
            (1.0, 0.25, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 atm calls + 2 otm puts + 1 atm put
                                {'strikeDist': -1.5, 'exprDist': 1, 'side': 'put', 'qty': 2},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 1}]),
            (1.0, 0.75, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # 2 ATM calls + 2 atm puts
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}]),
            (1.0, 1.0, lambda: [{'strikeDist': 1.5, 'exprDist': 1, 'side': 'call', 'qty': 2}, # vol: .7-1, dir: .75-1 # 2 otm calls + 1 atm call + 2 atm puts
                                {'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 1},
                                {'strikeDist': .5, 'exprDist': 2, 'side': 'put', 'qty': 2}])
        ]
        for vol_threshold, dir_threshold, orders in conditions:
            if vol < vol_threshold and dir < dir_threshold:
                return orders()
