# standard imports
from email.message import EmailMessage
import datetime as dt
import time
import pytz

# third party imports
import pandas as pd
import requests as rq
import shelve
import smtplib
import ssl

# local imports
from goats.core.core_objects import Portfolio, Option, Stock, Position, Order, LimitOrder
from goats.broker.alpaca_broker import AlpacaBroker


class Live:
    '''this holds all the stuff to run the live trading system.
     in the run_live file, it's very simply now just basically a live.run()'''
    def __init__(self, strategy, gmail_user, gmail_pass, shelf_path="goats_shelf"):
        self.strat = strategy
        self.gmail_user = gmail_user
        self.gmail_pass= gmail_pass
        self.shelf_path = shelf_path


    def run(self):
        self.strat.portfolio = self.load_shelf_portfolio()
        _, close_time = self.strat.broker.get_open_hours(dt.date.today())

        if close_time is not None:
            while dt.datetime.now() < close_time:
                self.strat.monitor_trades()
                self.strat.check_trigger_event()
                self.save_shelf_portfolio()
                time.sleep(5) # wait 5 seconds
                print(self.strat.portfolio)

        self.save_shelf_portfolio(wipe_broker=True)
        # stuff for debugging
        # print(self.strat.portfolio)
        # self.strat.monitor_trades()
        # self.strat.check_trigger_event()
        # time.sleep(5)


    def load_shelf_portfolio(self):
        '''Looks in shelf to see if portfolio object exists
        if not, creates one.
        DOES NOT sync w broker at all. just syncs with local shelf port
        note: shelf portfolio should not hold broker. it will always be added in this func'''
        with shelve.open(self.shelf_path) as s:
            port: Portfolio = s.get('portfolio') # using db.get will return None if not found instead of error

        if port == None: # make a new port object
            port = Portfolio(self.strat.broker)
            # print("making new port")
        else:
            port.set_broker(self.strat.broker)
            # print("loading preexisting port")

        return port


    def save_shelf_portfolio(self, wipe_broker=False):
        '''wipes broker, then saves current strat's port to shelve'''
        if wipe_broker:
            self.strat.portfolio.set_broker(None)

        with shelve.open(self.shelf_path) as db:
            db.update({'portfolio': self.strat.portfolio})


    def record_results(self, status, receipts=None, func=None, error=None):
        '''
        Takes status of program end, creates a subject and body, and logs it as well as sending out email
        record_results(status, symbol=None, qty=None, signal=None, price=None, SL=None, TP=None, unrealizedPL=None)
        '''
        current_time = dt.datetime.now(pytz.timezone('US/Eastern')) # get the local time of stock exchange
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
        self.send_email(subject, body)


    def send_email(self, subject, body):
        '''
        Sends email to self using user in mysecrets file containing provided info
        send_email(subject, body)
        '''
        sender = self.gmail_user
        receiver = self.gmail_user # set email recipient as self

        em = EmailMessage()
        em['From'] = sender
        em['To'] = receiver
        em['subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, self.gmail_pass)
            smtp.sendmail(sender, receiver, em.as_string())
