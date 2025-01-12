'''These are functions only relevant to live execution'''

from mysecrets import FMP_KEY
from datetime import date, datetime, timedelta
import requests as rq
import pandas as pd

# import sys
from goats import Position, Option, Portfolio, Strategy
# from sentiment_v1 import calcSentiment, sentiment2order


def createUnderlydf(symbol, dataInterval, dataPeriod): 
    '''
    Creates a simple dataframe of candlesticks (OHLC) of live stock data
    symbol: str
    dataInterval: str ('1hour')
    dataPeriod: int (number of days desired)'''
    today = datetime.today().strftime('%Y-%m-%d')
    startDate = datetime.today() - timedelta(days=dataPeriod)
    startDateFormatted = startDate.strftime('%Y-%m-%d')
    url = f'https://financialmodelingprep.com/api/v3/historical-chart/{dataInterval}/{symbol}?from={startDateFormatted}&to={today}&apikey={FMP_KEY}'
    data = rq.get(url).json()
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    data.columns = data.columns.str.capitalize()
    data=data[::-1] # reverse order of FMP candles

    startDate = data.index.strftime('%Y-%m-%d %H:%M:%S')[0] ## Get the latest datetime used in format '2023-12-19 15:30:00'
    endDate = data.index.strftime('%Y-%m-%d %H:%M:%S')[-1] ## Get the latest datetime used in format '2023-12-19 15:30:00'
   
    # data=data.reset_index(drop=True) # will remove datetime index and create 0-length indices
    # data.drop('Volume', axis = 1, inplace = True) # remove volume
    
    ## Creating Financial Indicators
    # data['signalATR'] = ta.atr(data.High, data.Low, data.Close, length = params.signalATRLength)
    # data['sellATR'] = ta.atr(data.High, data.Low, data.Close, length = params.sellATRLength)
    # YYBandss = ybbands(data.Close, data.signalATR, length = params.BBandsLength, stdConst = params.BBandsStdConst, backcount = params.YBBBackcount, slopeWeight = params.slopeWeight) # using the function defined earlier
    # data = data.join(YYBandss)

    # if data.index.hour[row] == marketOpenHour or data['fullScalar'].iloc[row] > params.scalarCutoff: # if its an open, or slope is too steep
    return data, data.Close.iloc[-1], startDate, endDate


def orderMakerLive(orders, underlyingLast, time=None):
    '''     orders: List of dictionaries, each containing strikeDist, exprDist, side, qty;
            example:        orders = [
                                {'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1},
                                {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1} ]
    '''
    for order in orders:
        goalStrike = underlyingLast + order['strikeDist']
        goalExpr = datetime.today() + timedelta(days=order['exprDist'])
        option = Option(goalStrike, goalExpr, order['side'])
        findClosestOption(option)
            

import alpaca
from alpaca.data.historical.option import OptionHistoricalDataClient, OptionLatestQuoteRequest
from alpaca.data.historical.stock import StockHistoricalDataClient, StockLatestTradeRequest
from alpaca.trading.client import TradingClient, GetAssetsRequest
from alpaca.trading.requests import GetOptionContractsRequest, LimitOrderRequest, MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import AssetStatus, ContractType, OrderSide, OrderType, TimeInForce, QueryOrderStatus

from mysecrets import ALPACA_API_KEY_PAPER, ALPACA_SECRET_KEY_PAPER

# from alpaca.trading.stream import TradingStream
trade_client = TradingClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER, paper=True)
stock_data_client = StockHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)
option_data_client = OptionHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)

def findClosestOption(Option: Option):
    '''
    finds live option that best matches desired strike and expiration
    Option: an object from the Option class'''
    min_expiration = Option.expr
    max_expiration = Option.expr + timedelta(days=5)

    min_strike = str(round(Option.strike*.97,2))
    max_strike = str(round(Option.strike*1.03,2))

    options_chain_list = optionsChainReq("SPY", Option.side, None, min_expiration, max_expiration,  min_strike, max_strike) # get a lot of em

    # find market day closest to desired expiration
    dayFound = False
    while not dayFound:
        for o in options_chain_list:
            # print(o.expiration_date, Option.expr.date(), o.expiration_date == Option.expr.date(), type(o.expiration_date), type(Option.expr.date()))
            if o.expiration_date == Option.expr.date():
                dayFound = True
                break
        if o.expiration_date != Option.expr.date():
            Option.expr += timedelta(days=1)

    options_chain_list_reduced = optionsChainReq("SPY", Option.side, Option.expr, None, None,  min_strike, max_strike) # get only on correct day
    # find option closest to desired strike
    priceDiff = 100
    for o in options_chain_list_reduced:
        if  abs(o.strike_price-Option.strike) < priceDiff:
            priceDiff=abs(o.strike_price-Option.strike)
            closestOpt = o

    return closestOpt


def optionsChainReq(underlying_symbol, side, expiration_date=None, min_expiration=None, max_expiration=None, min_strike=None, max_strike=None):
    '''
    Get an options chain that satisifies given criteria.
    This function can handle if the chain is over 1 page (100 options) long
    underlying symbol: str
    side: str 'call' or 'put'
    all dates in datetime
    min strike, max strike: float or int'''
    type = ContractType.CALL if side == 'call' else ContractType.PUT

    req = GetOptionContractsRequest(
        underlying_symbols=[underlying_symbol], # specify symbol(s)
        status=AssetStatus.ACTIVE, # specify asset status: active (default)
        expiration_date=expiration_date, # specify expr date (specified date + 1 day range)
        expiration_date_gte=min_expiration, # can pass date obj or string (YYYY-MM-DD)
        expiration_date_lte=max_expiration,
        root_symbol=underlying_symbol, # specify root symbol
        type=type, # either ContractType.CALL or ContractType.PUT
        # style=None, # either american or european
        strike_price_gte=min_strike, # strike price range
        strike_price_lte=max_strike,
        # limit=None, # specifiy limit
        page_token=None
    )
    res = trade_client.get_option_contracts(req)
    options_chain_list = res.option_contracts

    while res.next_page_token is not None: # if its multiple pages
        req = GetOptionContractsRequest(
            underlying_symbols=[underlying_symbol], # specify symbol(s)
            status=AssetStatus.ACTIVE, # specify asset status: active (default)
            expiration_date=expiration_date, # specify expr date (specified date + 1 day range)
            expiration_date_gte=min_expiration, # can pass date obj or string (YYYY-MM-DD)
            expiration_date_lte=max_expiration,
            root_symbol=underlying_symbol, # specify root symbol
            type=type, # either call or put
            # style=None, # either american or european
            strike_price_gte=min_strike, # strike price range
            strike_price_lte=max_strike,
            # limit=None, # specifiy limit
            page_token=res.next_page_token
        )
        res = trade_client.get_option_contracts(req)
        options_chain_list.extend(res.option_contracts)

    # print(f"number of options retreived: {len(options_chain_list)}")
    return options_chain_list
