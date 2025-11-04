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
from .sentiment_v1 import calc_sentiment, sentiment2order

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
        if time > market_close:
            break

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
