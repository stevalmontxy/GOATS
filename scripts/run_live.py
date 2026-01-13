# standard imports
import os
import smtplib
import ssl
from datetime import date, datetime, timedelta
from email.message import EmailMessage
import time

# third party imports
import pandas as pd
import requests as rq

# local imports
from goats.core.core_objects import Portfolio, Option, Stock, Position, Order, LimitOrder
from goats.broker.alpaca_broker import AlpacaBroker

from dotenv import load_dotenv

# Load API keys
load_dotenv()
trading_mode = os.getenv("TRADING_MODE")
# trading_mode = "paper" # manual override

paper = (trading_mode == "paper") # set boolean
if paper:
    api_key = os.getenv("ALPACA_API_KEY_PAPER")
    secret_key = os.getenv("ALPACA_SECRET_KEY_PAPER")
else:
    api_key = os.getenv("ALPACA_API_KEY_LIVE")
    secret_key = os.getenv("ALPACA_SECRET_KEY_LIVE")
    secret_key = os.getenv("ALPACA_SECRET_KEY_PAPER")

# define strat or this can be an import from a file full of strats
def CustomStrat(Strategy):
    pass


def main():
    broker = AlpacaBroker()
    port = update_shelf_portfolio(broker)
    strat = Strategy(broker, port)

    while true:
        strat.monitor_trades()
        strat.check_trigger_event()
        time.sleep(5)

    update_shelf_portfolio() # store current portfolio to shelf


def update_shelf_portfolio(broker, update_DB=True):
    '''Looks in shelf to see if portfolio object exists
    if not, creates one. Then updates it
    update_DB: if true, will resave the updated portfolio to shelf'''
    with shelve.open("goatsDB") as db:
        port: Portfolio = db.get('portfolio') # using db.get will return None if not found instead of error
        # print('dict at start of program:', dict(db))

    if port == None: # make a new port object
        port = Portfolio(broker)

    port.update_portfolio()

    if update_DB:
        with shelve.open("goatsDB") as db:
            db.update({'portfolio': port})
    return port # optional return

def record_results(status, receipts=None, func=None, error=None):
    '''
    Takes status of program end, creates a subject and body, and logs it as well as sending out email
    record_results(status, symbol=None, qty=None, signal=None, price=None, SL=None, TP=None, unrealizedPL=None)
    '''
    current_time = datetime.now(pytz.timezone('US/Eastern')) # get the local time of stock exchange
    current_time = current_time.strftime('%b %d, %Y %H:%M EST')

    if status == 'order success':
        subject = f'GOATS {current_time}: Successfully executed closingScript today!'
        body = f'Orders placed today:\n'
        for r in receipts:
            body += f'{r['side']} {r['qty']} shares of {r['name']} -- {r['status']}\n'
    elif status == 'order failed':
        subject = f'GOATS {current_time}: Order failed to place!'
        body = 'sorry mate I tried. well you tried a while ago. but i slipped thru haha\n'
    elif status == 'failed to run':
        subject = f'GOATS {current_time}: failed to run!'
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
    send_email(subject, body)


def send_email(subject, body):
    '''
    Sends email to self using user in mysecrets file containing provided info
    send_email(subject, body)
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
    try:
        main()
    except Exception as error:
        record_results('failed to run', func = 'closingScript', error=str(error))




# if I want to do async later
# async def on_bar(bar):
#     # update bars in broker.bars or something
#     pass

# async def trading_loop():
#     while True:
#         # do your shits
#         strat.monitor_trades(listen to updated global var)
#         # handle market closing check
#         strat.check_trigger_event()
#             # check_trigger_event handles buying near EOD, uses historic data to do so
#             # also checks time, if near market close, then break
#         # sleep(5 sec)

# async def main():
#     # init shits

#     subscribe_quotes
#     await asyncio.gather(
#         stream_run_foerever(),
#         tradingloop()
#     )
#     # after loop ends, handle some end stuff
