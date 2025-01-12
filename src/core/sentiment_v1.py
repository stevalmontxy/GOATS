'''
here are all the functions associated with sentiment. I am using the v1 so when I decide in the future
to derive order sizing differently i can keep this original
'''
# from goats import Position, Option, Portfolio, Strategy, Backtest
from live_funcs import orderMakerLive
from bt_funcs import orderMakerBt

def calcSentiment(data, t=None):
    '''
        - `dir` = f(previous day move size+direction, static bias, mean reversion, card count, TA)
        - `vol` = f(previous day move size, significant events, card count, TA, time since last big move)
        '''
    vol = .6 # I did some math
    dir = .6 # I did some DIFFERENT math
    return vol, dir

def sentiment2order(vol, dir, latestPrice=None, time=None, backtest=True):
    '''
    backtest: bool
    latestPrice is expected if bt=true
    time: None if bt=true'''
    def execute_order(*args, **kwargs):
        """       A wrapper to handle backtesting and live order execution.  """
        if backtest:
            orderMakerBt(*args, **kwargs)
        else:
            orderMakerLive(*args, **kwargs)

    conditions = [
        (0.3, 0.2, lambda: execute_order('1itmcall', '2atmput')), #vol: 0-.3, dir: 0-.2
        (0.3, 0.8, lambda: execute_order('1atmcall', '1atmput')), # vol: 0-.3, dir: .2-.8
        (0.3, 1.0, lambda: execute_order('2atncall', '1itmput')),
        (0.7, 0.15, lambda: execute_order('1atmcall', '1otmcall+2atmcall')), # vol: .3-.7, dir: 0-.15
        (0.7, 0.4, lambda: execute_order('1atmcall', '2atmput')), # vol: .3-.7, dir: 0-.4
        # (0.7, 0.6, lambda: SentimentV1.orderMaker('1itmcall', '1itmput')),
        (0.7, 0.6, lambda: execute_order([{'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1},
                                        {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1}], latestPrice, time)), #'1itmcall', '1itmput'
        (0.7, 0.85, lambda: execute_order('2atmcall', '1atmput')),
        (0.7, 1.0, lambda: execute_order('1OTMcall+2atmcall', '1atmput')),
        (1.0, 0.25, lambda: execute_order('2atmcall', '2otmput+1atmput')),  # THESE MAYBE EXP A DAY EARLY SOME
        (1.0, 0.75, lambda: execute_order('2ATMcall', '2atmput')),
        (1.0, 1.0, lambda: execute_order('2otmcall+1atmcall', '2atmput')), # vol: .7-1, dir: .75-1
    ]
    '''strike, expr, side, qty
        strike(distance), expr(distance), side, qty '''
    for vol_threshold, dir_threshold, action in conditions:
        if vol < vol_threshold and dir < dir_threshold:
            action() # this calls the lambda func which calls the orderMaker method
