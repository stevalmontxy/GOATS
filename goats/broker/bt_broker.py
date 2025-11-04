class BTBroker(Broker):
    pass

# currently this is a big dump from backtest.py
# will need these to be modified to match broker.py

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