'''
here are all the functions associated with sentiment. I am using the v1 so when I decide in the future
to derive order sizing differently i can keep this original
'''
# from goats import Position, Option, Portfolio, Strategy, Backtest


def calcSentiment(data, t=None):
    '''
    - `dir` = f(previous day move size+direction, static bias, mean reversion, card count, TA)
    - `vol` = f(previous day move size, significant events, card count, TA, time since last big move)
    '''
    vol = .6 # I did some math
    dir = .6 # I did some DIFFERENT math
    return vol, dir

def sentiment2order(vol, dir):
    '''
    backtest: bool
    latestPrice is expected if bt=true
    time: None if bt=true'''

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
        (1.0, 0.25, lambda: [{'strikeDist': -.5, 'exprDist': 2, 'side': 'call', 'qty': 2}, # THESE MAYBE EXP A DAY EARLY SOME # 2 atm calls + 2 otm puts + 1 atm put
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
