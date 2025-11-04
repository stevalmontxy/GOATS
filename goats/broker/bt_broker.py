class BTBroker(Broker):
    pass

# currently this is a big dump from backtest.py
# will need these to be modified to match broker.py

def order_maker_bt(orders, time=None):
    '''     orders: List of dictionaries, each containing strike_dist, expr_dist, side, qty;
            example:        orders = [
                                {'strike_dist': 1, 'expr_dist': 2, 'side': 'call', 'qty': 1},
                                {'strike_dist': -1, 'expr_dist': 2, 'side': 'put', 'qty': 1} ]
    '''
    pass
    # underlying_last = df["[UNDERLYING_LAST]"]
    # goal_strike = underlying_last+strike_dist
    # goal_expr = time + timedelta(days=expr_dist)
    # # find closest strike
    # # find closest expr
    # # if side == 'call': not needed, same process for call or put. strike dist is properly set to acct for either case
    # option = Option(strike, expr, side)

def find_closest_option():
    '''Completed for live, need to do for backtesting'''
    pass

def find_closest_open_day_bt():
    pass

def open_position(self, time, qty, option=None, stock=None):
    # for backtesting only to capture its value
    '''
    time: datetime YYYY-MM-DD HH:MM
    qty: float
    option: Option object
    Stock: Stock object (not defined)
    '''
    value = get_option_value(option.expr, option.strike, option.strike, time)
    self.positions[option.ID] = {"option": option, "open_time": time, "initial_value": value}
    self.cash -= 100*value
    self.trade_log.append(f"Opened position ID: {option.ID} at time: {time} at ${value}")

def close_position(self, option, time):
    '''THIS IS FOR BACKTESTING. use removePosition for live'''
    # remove an option from positions list, find value at close time, add to trade log
    value = self.get_option_value(option.expr, option.strike, option.strike, time)
    self.positions[option.ID].delete #or whatever ~~~~~~~~~~~
    '''
                        
    FIGURE THIS OUT    
        
    '''
    cash += 100*value
    self.trade_log.append(f"closed position ID: {option.ID} at time: {time} at ${value}")
    pass

def get_option_value(self, expr_date, strike, side, time):
    '''
    expr_date: datetime
    strike price: float
    side: 'call' or 'put' (string)
    time: datetime day+hr to check quote at
    '''
    print(type(time))
    quote_date = time.replace(hour=0, minute=0)
    quote_time_hour = time.hour + time.minute/60
    df_slice = df[(df["[QUOTE_DATE]"] == quote_date) & (df["[STRIKE]"]==float(strike)) & (df["[EXPIRE_DATE]"]==expr_date) & (df["[QUOTE_TIME_HOURS]"]==quote_time_hour) ] # gets a specific quote @ given time

    if side == 'call':
        return float(df_slice.iloc[0]["[C_LAST]"])
    else:  # for puts
        return float(df_slice.iloc[0]["[P_LAST]"])

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