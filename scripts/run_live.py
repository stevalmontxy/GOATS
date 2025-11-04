# standard imports
import pytz
import shelve
import smtplib
import ssl
from datetime import date, datetime, timedelta
from email.message import EmailMessage

# third party imports
import pandas as pd

# local imports
from .classes import Position, Option, Portfolio
from .sentiment_v1 import calcSentiment, sentiment2order

# define strat or this can be an import from a file full of strats
def customstrat(Strategy):
    pass

def main():
    broker = AlpacaBroker()
    port = update_shelf_portfolio(broker)
    strat = Strategy(broker, port)

    while true:
        strat.monitor_trades()
        strat.check_trigger_event()
        if time > market_close:
            break

def update_shelf_portfolio(broker, updateDB=True):
    '''Looks in shelf to see if portfolio object exists
    if not, creates one. Then updates it
    updateDB: if true, will resave the updated portfolio to shelf'''
    with shelve.open("goatsDB") as db:
        port: Portfolio = db.get('portfolio') # using db.get will return None if not found instead of error
        # print('dict at start of program:', dict(db))

    if port == None: # make a new port object
        port = Portfolio(broker)

    port.update_portfolio()

    if updateDB:
        with shelve.open("goatsDB") as db:
            db.update({'portfolio': port})
    return port # optional return

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

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        recordResults('failed to run', func = 'closingScript', error=str(error))
