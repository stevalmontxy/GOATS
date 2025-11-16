
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
from .classes import Position, Option, Portfolio
from .sentiment_v1 import calc_sentiment, sentiment2order

from dotenv import load_dotenv
from goats.broker.alpaca_broker import AlpacaBroker

# Load API keys
load_dotenv()
TRADING_MODE = paper # live # handle this later
trading_mode = os.getenv("TRADING_MODE")
paper = trading_mode == "paper"
if paper:
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
else:
    api_key = os.getenv("ALPACA_API_KEY_PAPER")
    secret_key = os.getenv("ALPACA_SECRET_KEY_PAPER")

import pytest

@pytest.fixture
def alpaca_broker():
    '''returns an initialized AlpacaBroker object'''
    broker = AlpacaBroker(api_key=api_key, secret_key=secret_key, paper=paper)
    return broker

def test_get_acct_details(alpaca_broker):
    details = alpaca_broker.get_acct_details()
    assert details['cash'] > 100000