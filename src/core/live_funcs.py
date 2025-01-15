'''These are functions only relevant to live execution'''

import shelve

from mysecrets import FMP_KEY
from datetime import date, datetime, timedelta
import requests as rq
import pandas as pd

# import sys
from goats import Position, Option, Portfolio, Strategy
from sentiment_v1 import calcSentiment, sentiment2order

import alpaca
from alpaca.data.historical.option import OptionHistoricalDataClient, OptionLatestQuoteRequest
from alpaca.data.historical.stock import StockHistoricalDataClient, StockLatestTradeRequest
from alpaca.trading.client import TradingClient, GetAssetsRequest
from alpaca.trading.requests import GetOptionContractsRequest, LimitOrderRequest, MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import AssetStatus, ContractType, OrderSide, OrderType, TimeInForce, QueryOrderStatus, OrderStatus

from mysecrets import ALPACA_API_KEY_PAPER, ALPACA_SECRET_KEY_PAPER
from mysecrets import GMAIL_USER, GMAIL_PASS

from email.message import EmailMessage
import ssl
import smtplib
import pytz

trade_client = TradingClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER, paper=True)
stock_data_client = StockHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)
option_data_client = OptionHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)


'''
def firstDayInit
    -there are no positions currently. port in db may or may not exist.
    -this script is triggered manually
    calc vol and dir
    enter positions
    update/create port, save

def closingScript
        if today is in the significant days list:
        exit. end of day
    else:
        check if open positions should be closed today or no
        if yes: 
            close them

        calc vol and dir
        enter positions
        update/create port, save
'''
def closingScript():
    '''- this script runs every weekday, the day after firstDayInit'''
    sig_dates = pd.read_excel("significant_dates.xlsx")
    today_timestamp = pd.Timestamp(date.today())

    if today_timestamp in sig_dates.date.values:
        index = sig_dates.index[sig_dates.date == today_timestamp][0]
        vol_calend = sig_dates.loc[index, 'vol']
        dir_calend = sig_dates.loc[index, 'dir']
    else:
        vol_calend = 0
        dir_calend = 0

    if vol_calend != -1:
        with shelve.open("goatsDB") as db:
            port: Portfolio = db.get('portfolio') #using db.get will return None if not found, instead of error
            print('dict at start of program:', dict(db))

        if port == None:# assume there are no positions, and no portfolio. so make a port object
            print('no port, making new one')
            port = Portfolio()
            with shelve.open("goatsDB") as db:
                db['portfolio'] = port
        else:
            # read current positions in port
            # close if needed
            if port.hasPositions:
                print("port has positions:")
                for p in port.positions:
                    print(p)
            else:
                print('port exisrts, no positions')

        # either way, continue and place new orders
        # data, latestPrice, _, _ = createUnderlydf("SPY", '1hour', 30)
        # vol, dir = calcSentiment(data)
        # orders = sentiment2order(vol, dir)
        # orderMakerLive(orders, latestPrice, port)
        with shelve.open("goatsDB") as db:
            db.update({'portfolio': port})
            print('dict at end of program:', dict(db))
    # else: market closed today or just do nothing today


def updatePortfolio():
    '''if you know the stored portfolio object is not in sync w the real portfolio status, run this'''
    with shelve.open("goatsDB") as db:
        port: Portfolio = db.get('portfolio') # using db.get will return None if not found, instead of error
        print('dict at start of program:', dict(db))

    if port == None: # make a new port object
        print('no port, making new one')
        port = Portfolio()
    
    positions_broker = trade_client.get_all_positions()
    if port.hasPositions:
        print("port has positions:")
        symbols_broker = [p.symbol for p in positions_broker]
        for p in port.positions:
            if p.symbol not in symbols_broker:
                port.removePosition(p.symbol)
    
    if len(positions_broker) > 0:
        symbols_port = [p.symbol for p in port.positions]
        for p in positions_broker:
            if p.symbol not in symbols_port:
                port.addPosition(p, p.symbol, p.qty, None)

    with shelve.open("goatsDB") as db:
        db.update({'portfolio': port})
        print('dict at end of program:', dict(db))


def createUnderlydf(symbol, dataInterval, dataPeriod): 
    '''
    Creates a simple dataframe of candlesticks (OHLC) of live stock data
    symbol: str
    dataInterval: str ('1hour')
    dataPeriod: int (number of days desired)'''
    today = date.today().strftime('%Y-%m-%d')
    startDate = date.today() - timedelta(days=dataPeriod)
    startDateFormatted = startDate.strftime('%Y-%m-%d')
    url = f'https://financialmodelingprep.com/api/v3/historical-chart/{dataInterval}/{symbol}?from={startDateFormatted}&to={today}&apikey={FMP_KEY}'
    try:
        data = rq.get(url).json()
    except:
        print("failed to request candles")
        recordResults("gettingdatafailed")
        
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


def orderMakerLive(orders, underlyingLast, port: Portfolio, time=None):
    '''     orders: List of dictionaries, each containing strikeDist, exprDist, side, qty;
            example:        orders = [
                                {'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1},
                                {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1} ]
    '''
    receipts = [] # used for email
    for order in orders:
        goalStrike = underlyingLast + order['strikeDist']
        goalExpr = date.today() + timedelta(days=order['exprDist'])
        option = Option(goalStrike, goalExpr, order['side'])
        # print('option date', option.expr, type(option.expr))
        o = findClosestOption(option)
        try:
            res = optionsLimitOrder(o, order['qty'])
            receipts.append({'name': o.name, 'qty': order['qty'], 'status': res.status})
            port.addPosition(o, o.symbol, order['qty'], date.today()) # add to portfolio for logging. will be saved and loaded on next code execution
            # print(res.status==OrderStatus.ACCEPTED)
        except:
            print("error at order placing")
            recordResults("order failed")
    recordResults("order success", receipts)   
    # return o, res # for debugging


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
            if o.expiration_date == Option.expr:
                dayFound = True
                break
        if o.expiration_date != Option.expr:
            Option.expr += timedelta(days=1)

    options_chain_list_reduced = optionsChainReq("SPY", Option.side, Option.expr, None, None,  min_strike, max_strike) # get only on correct day
    # find option closest to desired strike
    priceDiff = 100
    for o in options_chain_list_reduced:
        if  abs(o.strike_price-Option.strike) < priceDiff:
            priceDiff=abs(o.strike_price-Option.strike)
            closestOpt = o

    # print(closestOpt)
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


def optionsLimitOrder(option, qty):
    '''option: just how it is output from alpaca
    qty: float or int'''
    req = LimitOrderRequest(
        symbol=option.symbol,
        qty=qty,
        limit_price = option.close_price,
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        time_in_force = TimeInForce.DAY
        )

    res = trade_client.submit_order(req)
    
    return res


def recordResults(status, receipts=None):
    '''
    Takes status of program end, creates a subject and body, and logs it as well as sending out email
    recordResults(status, symbol=None, qty=None, signal=None, price=None, SL=None, TP=None, unrealizedPL=None)
    '''
    currentTime = datetime.now(pytz.timezone('US/Eastern')) # get the local time of stock exchange
    currentTime = currentTime.strftime('%b %d, %Y %H:%M EST')

    if status == 'order success':
        subject = f'GOATS {currentTime}: Orders placed successfully'
        body = f'Orders successfully placed today :)\n'
        for r in receipts:
            body += f'{r['qty']} shares of {r['name']} -- {r['status']}\n'
    elif status == 'order failed':
        subject = f'GOATS {currentTime}: Order failed to place!'
        body = 'sorry mate I tried. well you tried a while ago. but i slipped thru haha\n'
    # elif status == 'no orders made':
    #     subject = f'{currentTime}: No signals, no orders made'
    #     body = 'The title says it all :):\n'
    #     body += f'Data evaluated using latest data from {latestTime} EST.\n'
    # elif status == 'positions already':
    #     subject = f'{currentTime}: Already holding a position of {symbol} at ${price: .2f}'
    #     body = f'Unrealized P/L: ${unrealizedPL: .2f} ({unrealizedPLPC: .2f}%)\n'
    else:
        subject = 'PROBLEM PROBLEM'
        body = 'BIG PROBLEM HAPPENED'
    # body += f'Current portfolio value: ${portfolioVal: .2f}'

    # logging.info(subject)
    # logging.info(body)
    print(subject, body)
    # sendEmail(subject, body)

def sendEmail(subject, body):
    '''
    Sends email to self using user in mysecrets file containing provided info
    sendEmail(subject, body)
    '''
    GMAIL_RECEIVER = GMAIL_USER # set email recipient as self
    em = EmailMessage()
    em['From'] = GMAIL_USER
    em['To'] = GMAIL_USER
    em['subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.sendmail(GMAIL_USER, GMAIL_RECEIVER, em.as_string())