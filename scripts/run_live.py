# This file will hold the live deployment of goats

#import all the objects

live = LiveTrader()

# define strat or this can be an import from a file full of strats
def customstrat(Strategy):
  pass

live.setstrat(customstrat)
live.updateportfoliofromscratch # also update time
live.getandformatpricedata

# strat.run decisions
while (true):
  live.waitinterval
  live.updateportfolio
  strat.use_portfoliotocheckstuff


## BIG DUMP OF THINGS FROM now deleted live_funcs.py

# standard imports
import pytz
import shelve
import smtplib
import ssl
from datetime import date, datetime, timedelta
from email.message import EmailMessage

# third party imports
import pandas as pd
import requests as rq
from alpaca.data.historical.option import OptionHistoricalDataClient, OptionLatestQuoteRequest
from alpaca.data.historical.stock import StockHistoricalDataClient, StockLatestTradeRequest
from alpaca.trading.client import TradingClient, GetAssetsRequest
from alpaca.trading.enums import AssetStatus, ContractType, OrderSide, OrderType, TimeInForce, QueryOrderStatus, OrderStatus
from alpaca.trading.requests import GetOptionContractsRequest, LimitOrderRequest, MarketOrderRequest, GetOrdersRequest, GetCalendarRequest

# local imports
from .mysecrets import (
    ALPACA_API_KEY_PAPER, ALPACA_SECRET_KEY_PAPER,
    GMAIL_USER, GMAIL_PASS,
    FMP_KEY )
from .classes import Position, Option, Portfolio
from .sentiment_v1 import calcSentiment, sentiment2order

trade_client = TradingClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER, paper=True)
stock_data_client = StockHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)
option_data_client = OptionHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)

def firstDayInit():
    '''run this script when GOATS has never ran from a given directory before.
    this script: creates/syncs portfolio object
    places orders for the day
    the system needs it to have a correct portfolio object.
    in its current state, running updatePortfolio() alone would suffice 
    and this script is unnecessary, but in the future initialization may require more'''
    port = updatePortfolio()

    data, latestPrice, _, _ = createUnderlydf("SPY", '1hour', 30)
    vol, dir = calcSentiment(data)
    orders = sentiment2order(vol, dir)
    receipts = []
    port = orderMakerLive(orders, latestPrice, port, receipts)
    with shelve.open("goatsDB") as db:
        db.update({'portfolio': port}) # store changes to port object

def closingScript():
    '''This script runs every weekday, starting the day after firstDayInit. 
    assuming port object exists (setup by firstDayInit)'''
    sig_dates = pd.read_excel("significant_dates.xlsx")
    today_timestamp = pd.Timestamp(date.today())

    if today_timestamp in sig_dates.date.values: # check spreadsheet for market close or special events
        index = sig_dates.index[sig_dates.date == today_timestamp][0]
        vol_calend = sig_dates.loc[index, 'vol']
        dir_calend = sig_dates.loc[index, 'dir']
    else:
        vol_calend = 0
        dir_calend = 0

    if vol_calend != -1: # -1 = market closed / manual stay out signal
        with shelve.open("goatsDB") as db:
            port: Portfolio = db.get('portfolio') # using db.get will return None if not found instead of error
        
        receipts = []
        if port == None:
            recordResults('no shelve obj')
        # read current positions in port, close any if needed
        if port.hasPositions:
            for p in port.positions[:]: # iterate over a copy of port.positions to avoid issue after removing position(s)
                if p.exitDate == date.today():
                    receipts = closePosition(p, orderType='limit', receipts=receipts) # place exit order on brokerage
                    port.removePosition(p.symbol) # remove from port object
                    print(f'getting out of {p.symbol} position')
                    # exit the position, remove from port

        # either way, continue and place new orders
        data, latestPrice, _, _ = createUnderlydf("SPY", '1hour', 30)
        vol, dir = calcSentiment(data)
        orders = sentiment2order(vol, dir)
        port = orderMakerLive(orders, latestPrice, port, receipts)
        with shelve.open("goatsDB") as db:
            db.update({'portfolio': port}) # store changes to port object
    else:
        print('market out day')


def recordResults(status, receipts=None, func=None, error=None):
    '''
    Takes status of program end, creates a subject and body, and logs it as well as sending out email
    recordResults(status, symbol=None, qty=None, signal=None, price=None, SL=None, TP=None, unrealizedPL=None)
    '''
    currentTime = datetime.now(pytz.timezone('US/Eastern')) # get the local time of stock exchange
    currentTime = currentTime.strftime('%b %d, %Y %H:%M EST')

    if status == 'order success':
        subject = f'GOATS {currentTime}: Successfully executed closingScript today!'
        body = f'Orders placed today:\n'
        for r in receipts:
            body += f'{r['side']} {r['qty']} shares of {r['name']} -- {r['status']}\n'
    elif status == 'order failed':
        subject = f'GOATS {currentTime}: Order failed to place!'
        body = 'sorry mate I tried. well you tried a while ago. but i slipped thru haha\n'
    elif status == 'failed to run':
        subject = f'GOATS {currentTime}: failed to run!'
        body = f'ran into error at {func}:\n'
        body += error
    elif status == 'no shelve obj':
        subject = 'no shelf object'
        body = ''
    else:
        subject = 'Miscellaneous Error Occured'
        body = f'Internal error. Status code: {status}\n'
        body += error
    # body += f'Current portfolio value: ${portfolioVal: .2f}'

    # logging.info(subject)
    # logging.info(body)
    # print(subject,'\n', body)
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