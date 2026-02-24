# Standard Imports
import sys
import os
import datetime as dt

# Third Party Imports
import pytest
import pandas as pd
# from dotenv import load_dotenv

# Local Imports
# print(sys.path)
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.append(PROJECT_ROOT)
# sys.path.append(os.path.abspath(".."))
from goats.core.core_objects import Portfolio, Option, Stock, Position
from goats.core.core_objects import Order, LimitOrder
from goats.broker.bt_broker import BTBroker

# Data Setup
options_df = pd.read_csv("data/aapl_30x_202307.txt", delimiter=", ")
options_df = options_df.drop(options_df.columns[[0, 6, 8,9,10,11,12, 13,14, 16,17,18, 20,21,22, 24,25,26,27,28, 29]], axis=1) # dont forget to acct for 0 ind
options_df["[QUOTE_DATE]"] = pd.to_datetime(options_df["[QUOTE_DATE]"])
options_df["[EXPIRE_DATE]"] = pd.to_datetime(options_df["[EXPIRE_DATE]"])

file_dir = "data/AAPL.USUSD_Candlestick_30_M_BID_02.01.2023-29.12.2023FORMATTED.csv"
underly_df = pd.read_csv(file_dir, parse_dates=['Datetime'], index_col='Datetime')
initial_cash=100000

# Fixtures
@pytest.fixture
def bt_broker():
    bt_broker = BTBroker(options_df, underly_df, initial_cash)
    bt_broker.set_time(dt.datetime(2023, 7, 12, 12, 30))
    return bt_broker

# Tests

# Test Fetching Data

def test_get_stock_data(bt_broker):
    symbol = "AAPL"
    timeframe = "30Min"
    num_days = 6
    df = bt_broker.get_stock_data(symbol, timeframe, num_days)
    assert df.size > 0
    assert df.shape[0] < df.size

def test_get_options_contracts(bt_broker):
    underly = "AAPL"
    side = "C"
    min_expr = bt_broker.now().date() + pd.Timedelta(days=2)
    max_expr = min_expr + pd.Timedelta(days=8)
    min_strike = 130
    max_strike = 190
    chain = bt_broker.get_options_contracts(underlying_symbol=underly, side=side, min_expiration=min_expr, 
                                max_expiration=max_expr, min_strike=min_strike, max_strike=max_strike)
    assert len(chain) > 100

def test_get_closest_option(bt_broker):
    option = Option(strike=160, expr=(bt_broker.now().date()+dt.timedelta(days=3)), side="C", underlying="AAPL")
    opt = bt_broker.get_closest_option(option)
    assert type(opt.strike) == int

def test_get_closest_open_date(bt_broker):
    later_date = bt_broker.now().date() + dt.timedelta(days = 2)
    bt_broker.get_closest_open_date(later_date)
    assert later_date >= bt_broker.now().date() 

# Test Executing Orders

def test_place_stock_limit_order(bt_broker):
    order = LimitOrder(asset=Stock(symbol="AAPL"))
    res = bt_broker.place_order(order)
    assert res == True

def test_place_option_limit_order(bt_broker):
    option = Option(strike=160, expr=(bt_broker.now().date()+dt.timedelta(days=3)), side="C", underlying="AAPL")
    closest_option = bt_broker.get_closest_option(option)
    order = LimitOrder(asset=closest_option)
    res = bt_broker.place_order(order)
    assert res == True
    # assert res[0].status == 'pending_new'

# def test_delta_order_to_order(bt_broker):
'''
def test_cancel_order(bt_broker):
    order = LimitOrder(symbol="AAPL")
    res = bt_broker.place_orders(order) 
    res_cancel = bt_broker.cancel_order(res[0].id)
    assert res == True
    assert res_cancel == True # if no errors it worked
    '''
'''
def test_cancel_all_orders(bt_broker):
    #place test limit orders that won't fill
    order = LimitOrder("AAPL", True, 1, limit_price=500)
    bt_broker.place_orders(order) 
    order = LimitOrder(Stock(symbol="AAPL"))
    bt_broker.place_orders(order2)
    res = bt_broker.cancel_all_orders()
    for r in res:
        assert r.status == 200
        '''

def test_close_position(bt_broker):
    order = LimitOrder("AAPL", True, 1)
    bt_broker.place_orders(order)

    res =  bt_broker.close_position(asset=Stock("AAPL"))
    assert res == True

# Test Querying Portfolio

def test_get_open_orders(bt_broker):
    orders = bt_broker.get_open_orders()
    assert True

def test_get_positions(bt_broker):
    positions = bt_broker.get_positions()
    assert True

def test_get_acct_value(bt_broker):
    acct = bt_broker.get_acct_value()
    assert acct.cash > 0
    assert acct.portfolio_value >= acct.cash

# Misc Test

def test_change_time(bt_broker):
    bt_broker.set_time(dt.date(2023, 7, 15))
    assert bt_broker.now().month == 7
    assert bt_broker.now().day == 15
