# Standard Imports
import sys
import os
import datetime as dt

# Third Party Imports
import pytest
import pandas as pd
from dotenv import load_dotenv

# Local Imports
from goats.core.core_objects import Portfolio, Option, Stock, Position, Order, LimitOrder
from goats.broker.alpaca_broker import AlpacaBroker

# Environment Setup
load_dotenv()
trading_mode = os.getenv("TRADING_MODE")

paper = (trading_mode == "paper") # set boolean
if paper:
    api_key = os.getenv("ALPACA_API_KEY_PAPER")
    secret_key = os.getenv("ALPACA_SECRET_KEY_PAPER")
else:
    api_key = os.getenv("ALPACA_API_KEY_LIVE")
    secret_key = os.getenv("ALPACA_SECRET_KEY_LIVE")

# Fixtures
@pytest.fixture
def alpaca_broker():
    '''returns an initialized AlpacaBroker object'''
    broker = AlpacaBroker(api_key=api_key, secret_key=secret_key, paper=paper)
    return broker

# Tests

# Test Fetching Data

def test_get_stock_data(alpaca_broker):
    symbol = "SPY"
    timeframe = "1Hour"
    num_days = 6
    df = alpaca_broker.get_stock_data(symbol, timeframe, num_days)
    assert df.size > 0
    assert df.shape[0] < df.size

def test_get_options_contracts(alpaca_broker):
    underly = "SPY"
    side = "call"
    min_expr = dt.date.today() + dt.timedelta(days=2)
    max_expr = min_expr + dt.timedelta(days=8)
    min_strike = 650
    max_strike = 700
    chain = alpaca_broker.get_options_contracts(underlying_symbol=underly, side=side, min_expiration=min_expr, 
                                max_expiration=max_expr, min_strike=min_strike, max_strike=max_strike)
    assert len(chain) > 100

def test_get_closest_option(alpaca_broker):
    option = Option(strike=660, expr=(dt.date.today()+dt.timedelta(days=3)), side="call", underlying="SPY")
    opt = alpaca_broker.get_closest_option(option)
    assert type(opt.symbol) == str 

def test_get_closest_open_date(alpaca_broker):
    later_date = dt.date.today() + dt.timedelta(days = 2)
    alpaca_broker.get_closest_open_date(later_date)
    assert later_date >= dt.date.today() 

# Test Executing Orders

def test_place_stock_limit_order(alpaca_broker):
    order = LimitOrder("SPY", True, 1)
    res = alpaca_broker.place_orders(order)
    assert res[0].failed_at == None

def test_place_option_limit_order(alpaca_broker):
    option = Option(strike=660, expr=(dt.date.today()+dt.timedelta(days=3)), side="call", underlying="SPY")
    closest_option = alpaca_broker.get_closest_option(option)
    order = LimitOrder(closest_option.symbol, False, 1)
    res = alpaca_broker.place_orders(order)
    assert res[0].failed_at == None
    # assert res[0].status == 'pending_new'

# def test_delta_order_to_order(alpaca_broker):

def test_cancel_order(alpaca_broker):
    order = LimitOrder("SPY", True, 1, limit_price=500)
    res = alpaca_broker.place_orders(order) 
    res_cancel = alpaca_broker.cancel_order(res[0].id)
    assert True # if no errors it worked

def test_cancel_all_orders(alpaca_broker):
    #place test limit orders that won't fill
    order = LimitOrder("SPY", True, 1, limit_price=500)
    alpaca_broker.place_orders(order) 
    order2 = LimitOrder("SPY", True, 1, limit_price=530)
    alpaca_broker.place_orders(order2)
    res = alpaca_broker.cancel_all_orders()
    for r in res:
        assert r.status == 200

# def test_close_positions(alpaca_broker):
#     order = LimitOrder("SPY", True, 1)
#     alpaca_broker.place_orders(order)

#     res =  alpaca_broker.close_positions("SPY")
#     print(res)
#     for r in res:
#         assert r.status == 200

# Test Querying Portfolio

def test_get_open_orders(alpaca_broker):
    orders = alpaca_broker.get_open_orders()
    assert True

def test_get_positions(alpaca_broker):
    positions = alpaca_broker.get_positions()
    assert True

def test_get_acct_value(alpaca_broker):
    acct = alpaca_broker.get_acct_value()
    assert acct.cash > 0
    assert acct.portfolio_value >= acct.cash
