#RUN EVERY HOUR: (handled outside of program)
# market is open 9:30-4pm EST
# premarket opens at 4am, aftermarket lasts till 8pm


import numpy as np
import pandas as pd
import pandas_ta as ta
from pandas_ta.statistics import stdev
from datetime import date, datetime
import requests as rq
import yfinance as yf
from email.message import EmailMessage
import ssl
import smtplib
import pytz
#from plotly.subplots import make_subplots
#import plotly.graph_objects as go
#from backtesting import Backtest, Strategy
import logging

from mysecrets import GMAIL_USER, GMAIL_PASS
from mysecrets import API_KEY, SECRET_KEY


logging.basicConfig(filename='BFTS YBBands Paper.log', level=logging.INFO, #filemode='w', # you can config filename to change based on date or symbol or such
                   format = '%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# The logging levels are: DEBUG < INFO < WARNING < ERROR < CRITICAL


def main():
    '''
    Program Description
    '''
    ##### PARAMS
    DUK = stockParams(symbol='DUK', ATRLength=14, BBandsLength= 30, BBandsStd= 2.0, YBBBackcount= 3, scalarWeight= 1.5, longATRLength= 30, stdevLength= 14, TPCoeff=2.2, SLCoeff=1)
    EXC = stockParams(symbol='EXC', ATRLength=7, BBandsLength= 30, BBandsStd= 2.1, YBBBackcount= 2, scalarWeight= 1.1, longATRLength= 30, stdevLength= 20, TPCoeff=2.2, SLCoeff=1.2)
    NEE = stockParams(symbol='NEE', ATRLength=14, BBandsLength= 20, BBandsStd= 2.0, YBBBackcount= 2, scalarWeight= 1, longATRLength= 30, stdevLength= 20, TPCoeff=2.2, SLCoeff=1)
    XOM = stockParams(symbol='XOM', ATRLength=7, BBandsLength= 40, BBandsStd= 2.0, YBBBackcount= 2, scalarWeight= 1, longATRLength= 30, stdevLength= 20, TPCoeff=2.4, SLCoeff=1.2)
    stocklist = [DUK,EXC, NEE, XOM] # place in order of preference, will run in order

    dataPeriod = '1mo'
    dataInterval = '1h'

    logging.info('~~~~~~~~~~~~~~~~~~~~Main function started.~~~~~~~~~~~~~~~~~~~~')
    positionNum, orderNum, positions, portfolioVal, cash = checkPositions()
    if positionNum + orderNum == 0: # if there are currently no live positions or open orders
        for i in range (0,len(stocklist)):
            positionNum, orderNum, _, _, _ = checkPositions()
            if positionNum + orderNum == 0: # if there are currently no live positions or open orders      
                signal, latestClose, stopLoss, takeProfit, latestTime = createSignal(stocklist[i], dataPeriod = dataPeriod, dataInterval=dataInterval)
                if signal == 1:
                    postOrder(signal, stopLoss, takeProfit, latestClose, stocklist[i].symbol, cash, portfolioVal, latestTime) # create buy order
                    # recordResults will be run through postOrder funct
                elif signal == -1:
                    postOrder(signal, stopLoss, takeProfit, latestClose, stocklist[i].symbol, cash, portfolioVal, latestTime) # create sell (short) order
                    # recordResults will be run through postOrder funct
        positionNum, orderNum,positions,  _, _ = checkPositions()
        if positionNum + orderNum == 0:  # if there are currently no live positions or open orders
            recordResults('no orders made', portfolioVal, latestTime) #pass in orders and positions, and log:
    else: # currently holding a position (no order):
        recordResults('positions already', portfolioVal=portfolioVal, symbol=positions['symbol'], price=float(positions['current_price']), unrealizedPL=float(positions['unrealized_pl']),unrealizedPLPC=float(positions['unrealized_plpc'])*100)
    logging.info('Main function made it to the end :)')


class stockParams:
    '''
    A funny guy that teaches funny things Program Description
    '''
    def __init__(self, symbol, ATRLength, BBandsLength, BBandsStd, YBBBackcount, scalarWeight, longATRLength, stdevLength, TPCoeff, SLCoeff):
        self.symbol = symbol
        self.ATRLength = ATRLength
        self.BBandsLength = BBandsLength
        self. BBandsStd = BBandsStd
        self.YBBBackcount = YBBBackcount
        self.scalarWeight = scalarWeight
        self.longATRLength = longATRLength
        self.stdevLength = stdevLength
        self.TPCoeff = TPCoeff
        self.SLCoeff = SLCoeff


def checkPositions():
    '''
    Checks Alpaca positions and open orders
    positions, orders, positionNum, orderNum = checkPositions()
    Inputs:
    none
    Outputs:
    positions & orders - json files including info
    positionNum & orderNum - number of positions and orders (int)
    '''
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }

    accountUrl = 'https://paper-api.alpaca.markets/v2/account'
    positionsUrl = "https://paper-api.alpaca.markets/v2/positions"
    ordersUrl = "https://paper-api.alpaca.markets/v2/orders?status=open"

    accountResponse = rq.get(accountUrl, headers=headers)
    positionsResponse = rq.get(positionsUrl, headers=headers)
    ordersResponse = rq.get(ordersUrl, headers=headers)

    if positionsResponse.status_code == 200 & ordersResponse.status_code == 200 & accountResponse.status_code == 200:
        positions = positionsResponse.json() # converts to json format
        orders = ordersResponse.json()
        account = accountResponse.json()
        positionNum = len(positions) # number of positions (0 if none)
        orderNum = len(orders)
        portfolioVal = float(account['portfolio_value'])
        cash = float(account['cash'])
        positions = positions[0] # This will make subfunct only return info on the first order
        logging.info(f'Position count: {positionNum} | Order count: {orderNum}')
    else:
        logging.critical('UNABLE TO CHECK POSITION AND ORDER STATUS')
    return positionNum, orderNum,positions, portfolioVal, cash


def createSignal(params, dataPeriod, dataInterval):
    '''
    Retrieves stock ticker data, creates indicators, evalualtes signal, sets SL and TP if signal
    signal, latestClose, stoploss, takeProfit = createSignal(stockParams, dataPeriod = dataperiod, dataInterval = dataInterval)
    '''
    ## Downloading Data
    data = yf.download(tickers=f'{params.symbol}', period=dataPeriod, interval=dataInterval)
    data.drop('Adj Close', axis = 1, inplace = True) # remove Adj Close column

    ## Filtering out Empty Data
    origLength = len(data)
    data = data[data['High']!=data['Low']] # remove data without price movement
    dataWPriceChange = len(data)
    data = data[data['Volume']!=0] # remove data with zero-volume
    dataWVolume = len(data)
    logging.info(f'{params.symbol}: original data length: {origLength} | data with change: {dataWPriceChange} | data with volume: {dataWVolume}')

    ## Creating Financial Indicators
    data['ATR'] = ta.atr(data.High, data.Low, data.Close, length = params.ATRLength)
    data['longATR'] = ta.atr(data.High, data.Low, data.Close, length = params.longATRLength)
    data['Stdev'] = stdev(close = data.Close, length = params.stdevLength)
    YYBandss = ybbands(data.Close, data.ATR, length = params.BBandsLength, std = params.BBandsStd, backcount = params.YBBBackcount, scalarWeight = params.scalarWeight) # using the function defined earlier
    data = data.join(YYBandss)

    ## Creating the Signal
    # 1 = buy, -1 = short, 0 = no signal
    # .iloc[-1] gives the last value in the colummn
    signal = 0
    if (max(data.Open.iloc[-1], data.Close.iloc[-1]) > data[f'YBBU_{params.BBandsLength}_{params.BBandsStd}'].iloc[-1] and 
        min(data.Open.iloc[-1], data.Close.iloc[-1]) < data[f'YBBU_{params.BBandsLength}_{params.BBandsStd}'].iloc[-1]):
        signal = 0 # if there is a double signal, disregard it
    elif max(data['Open'].iloc[-1], data['Close'].iloc[-1]) > data[f'YBBU_{params.BBandsLength}_{params.BBandsStd}'].iloc[-1]:
        signal = -1 # above BBands, so short
    elif min(data['Open'].iloc[-1], data['Close'].iloc[-1]) < data[f'YBBL_{params.BBandsLength}_{params.BBandsStd}'].iloc[-1]:
        signal = 1 # below bbands, so buy
    # else, signal remains 0

    if signal != 0: # if there is a buy or short signal
        SLLength = params.SLCoeff * data.longATR.iloc[-1]
        TPLength = params.TPCoeff * data.longATR.iloc[-1]
        # set SL and TP
        if signal == 1:
            stopLoss = round(data.Close.iloc[-1] - SLLength,2)
            takeProfit = round(data.Close.iloc[-1] + TPLength,2)
            logging.info(f'{params.symbol}: Signal: {signal} | Price: ${round(data.Close.iloc[-1],2)} | SL: ${stopLoss} | TP: ${takeProfit}')
        elif signal == -1:
            stopLoss = round(data.Close.iloc[-1] + SLLength,2)
            takeProfit = round(data.Close.iloc[-1] - TPLength,2)
            logging.info(f'{params.symbol}: Signal: {signal} | Price: ${round(data.Close.iloc[-1],2)} | SL: ${stopLoss} | TP: ${takeProfit}')
    else:
        stopLoss = 0
        takeProfit = 0
        logging.info(f'{params.symbol}: Signal: {signal}; No signal generated.')
    return signal, round(data.Close.iloc[-1],2), stopLoss, takeProfit, data.index.strftime('%Y-%m-%d %H:%M:%S')[-1]


def ybbands(close, ATR, length, std, backcount, scalarWeight):
    '''
    Creates "Yang Bollinger Bands" technical indicator. Kinda like a Bollinger Bands
    that has Stand Dev scaled by the slope of the central MA
    ybbandsdf = ybbands(close, ATR, length, std, backcount, scalarWeight)
    '''
    mid = ta.sma(close, length = length)
    standdev = stdev(close = close, length = length)
    slope = inaccurateSlope(mid, backcount = backcount)
    stdScalar = abs(slope/ATR)
    fullScalar = (.95 + scalarWeight * stdScalar)**2

    lower = mid - fullScalar * standdev * std
    upper = mid + fullScalar * standdev * std

    # Name and Categorize it
    lower.name = f"YBBL_{length}_{std}"
    mid.name = f"YBBM_{length}_{std}"
    upper.name = f"YBBU_{length}_{std}"
    stdScalar.name = 'stdScalar' # not useful in function, good for program analysis
    
    data = {lower.name: lower, mid.name: mid, upper.name: upper, stdScalar.name: stdScalar}

    ybbandsdf = pd.DataFrame(data)
    ybbandsdf.name = f"YBBANDS_{length}_{std}"
    return ybbandsdf # no logging neccessary   


def inaccurateSlope(x, backcount):
    '''
    Calculates the slope at  any given point in the function, not super accurate
    slope = inaccurateSlope(x, backcount)
    '''
    slope = [0]*len(x)

    for i in range(1,len(x)):
        if np.isnan(x.iloc[i - backcount]):
            slope[i] = np.nan
        else:
            slope[i] = (x.iloc[i] - x.iloc[i - backcount]) / backcount
    return slope # no logging necessary


def postOrder(signal, SL, TP, price, symbol, cash, portfolioVal, latestTime):
    '''
    Post order to Alpaca through requests (not through their API)
    postOrder(signal, SL, TP, price, symbol)
    '''
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY
    }

    ordersUrl = 'https://paper-api.alpaca.markets/v2/orders'
    
    orderSize = int(cash * .98 * .05 - 1)
    qty = int(orderSize / price)
    logging.info(f'Order size: ${orderSize} | Quantity of {symbol} shares: {qty}')

    if signal == 1:
        side = 'buy'
        stopPrice = price # * +.10 # add 10 cents; may want to add this later for additional safety, but it kinda cuts into profits
    elif signal == -1:
        side = 'sell'
        stopPrice = price # * .98 # - .10
    
    payload = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        #'notional': orderSize, #can't do notional with a stop order type
        'type': 'stop', # 'market',
        'time_in_force': 'day',  # day orders placed after close are submitted the next day, or can be filled in after hours
        'stop_price': stopPrice,
        'order_class': 'bracket',
        'take_profit': {'limit_price': TP},
        'stop_loss': {'stop_price': SL}
    }
    orderResponse = rq.post(ordersUrl, json=payload, headers=headers) # Attempt to submit order
    if orderResponse.status_code == 200:
        recordResults('order success', portfolioVal, latestTime, symbol, qty, signal, stopPrice, SL, TP) # record order succeeded
    else:
        recordResults('order failed', portfolioVal, latestTime, symbol) # record order failed


def recordResults(status, portfolioVal, latestTime=None, symbol=None, qty=None, signal=None, price=None, SL=None, TP=None, unrealizedPL=None,unrealizedPLPC=None):
    '''
    Takes status of program end, creates a subject and body, and logs it as well as sending out email
    recordResults(status, symbol=None, qty=None, signal=None, price=None, SL=None, TP=None, unrealizedPL=None)
    '''
    currentTime = datetime.now(pytz.timezone('US/Eastern')) # get the local time of stock exchange
    currentTime = currentTime.strftime('%b %d, %Y %H:%M EST')

    side = 'long' if signal == 1 else 'short'
    if status == 'order success':
        subject = f'{currentTime}: Order placed on {symbol}'
        body = f'Order placed on {symbol} for {side} position at ${price}\n'
        body += f'{qty} shares totalling order size of ${qty*price}\n'
        body += f'Stop loss set at ${SL} | TP set at ${TP}\n'
        body += f'Data evaluated using latest data from {latestTime} EST.\n'
    elif status == 'order failed':
        subject = f'{currentTime}: Order failed to place on {symbol}!'
        body = 'sorry mate I tried. well you tried a while ago. but i slipped thru haha\n'
        body += f'Data evaluated using latest data from {latestTime} EST.\n'
    # elif status == 'data retrieval failed':
    #     subject = f'{currentTime}: Account data retreival failed!'
    #     body = 'bro this is kind of a let down I thought you could do better than this.\n'
    elif status == 'no orders made':
        subject = f'{currentTime}: No signals, no orders made'
        body = 'The title says it all :):\n'
        body += f'Data evaluated using latest data from {latestTime} EST.\n'
    elif status == 'positions already':
        subject = f'{currentTime}: Already holding a position of {symbol} at ${price: .2f}'
        body = f'Unrealized P/L: ${unrealizedPL: .2f} ({unrealizedPLPC: .2f}%)\n'
    else:
        subject = 'PROBLEM PROBLEM'
        body = 'BIG PROBLEM HAPPENED'
        logging.critical('~~~~~~~~~~~~~~~~~~~~BAD BAD BAD~~~~~~~~~~~~~~~~~~~~')
    body += f'Current portfolio value: ${portfolioVal: .2f}'

    logging.info(subject)
    logging.info(body)
    sendEmail(subject, body)


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


if __name__ == "__main__":
    main()