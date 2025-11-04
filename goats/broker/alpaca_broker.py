from .broker import Broker
from ..core.core_objects import Portfolio

import requests as rq
from alpaca.data.historical.option import OptionHistoricalDataClient, OptionLatestQuoteRequest
from alpaca.data.historical.stock import StockHistoricalDataClient, StockLatestTradeRequest
from alpaca.trading.client import TradingClient, GetAssetsRequest
from alpaca.trading.enums import AssetStatus, ContractType, OrderSide, OrderType, TimeInForce, QueryOrderStatus, OrderStatus
from alpaca.trading.requests import GetOptionContractsRequest, LimitOrderRequest, MarketOrderRequest, GetOrdersRequest, GetCalendarRequest

trade_client = TradingClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER, paper=True)
stock_data_client = StockHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)
option_data_client = OptionHistoricalDataClient(api_key=ALPACA_API_KEY_PAPER, secret_key=ALPACA_SECRET_KEY_PAPER)

# local imports
from .mysecrets import (
    ALPACA_API_KEY_PAPER, ALPACA_SECRET_KEY_PAPER,
    GMAIL_USER, GMAIL_PASS,
    FMP_KEY )

def AlpacaBroker(Broker):
    # everything currently below will find its way into this class
    pass


### CURRENTLY THIS IS A BIG DUMP FROM now deleted live_funcs.py


def create_underly_df(symbol, data_interval, data_period): 
    '''
    Creates a simple dataframe of candlesticks (OHLC) of live stock data
    symbol: str
    data_interval: str ('1hour')
    data_period: int (number of days desired)'''
    today = date.today().strftime('%Y-%m-%d')
    start_date = date.today() - timedelta(days=data_period)
    start_date_formatted = start_date.strftime('%Y-%m-%d')
    url = f'https://financialmodelingprep.com/api/v3/historical-chart/{data_interval}/{symbol}?from={start_date_formatted}&to={today}&apikey={FMP_KEY}'
    try:
        data = rq.get(url).json()
    except Exception as error:
        print("failed to request candles")
        record_results("failed requesting data from FMP", error=str(error))

    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    data.columns = data.columns.str.capitalize()
    data=data[::-1] # reverse order of FMP candles

    start_date = data.index.strftime('%Y-%m-%d %H:%M:%S')[0] ## Get the latest datetime used in format '2023-12-19 15:30:00'
    end_date = data.index.strftime('%Y-%m-%d %H:%M:%S')[-1] ## Get the latest datetime used in format '2023-12-19 15:30:00'

    # data=data.reset_index(drop=True) # will remove datetime index and create 0-length indices
    # data.drop('Volume', axis = 1, inplace = True) # remove volume
    
    ## Creating Financial Indicators
    # data['signalATR'] = ta.atr(data.High, data.Low, data.Close, length = params.signalATRLength)
    # data['sellATR'] = ta.atr(data.High, data.Low, data.Close, length = params.sellATRLength)
    # YYBandss = ybbands(data.Close, data.signalATR, length = params.BBandsLength, stdConst = params.BBandsStdConst, backcount = params.YBBBackcount, slopeWeight = params.slopeWeight) # using the function defined earlier
    # data = data.join(YYBandss)

    # if data.index.hour[row] == marketOpenHour or data['fullScalar'].iloc[row] > params.scalarCutoff: # if its an open, or slope is too steep
    return data, data.Close.iloc[-1], start_date, end_date


def order_maker_live(orders, underlying_last, port: Portfolio, receipts, time=None):
    '''     orders: List of dictionaries, each containing strike_dist, expr_dist, side, qty;
            example:        orders = [
                                {'strike_dist': 1, 'expr_dist': 2, 'side': 'call', 'qty': 1},
                                {'strike_dist': -1, 'expr_dist': 2, 'side': 'put', 'qty': 1} ]
    '''
    for order in orders:
        goal_strike = underlying_last + order['strike_dist']
        goal_expr = date.today() + timedelta(days=order['expr_dist'])
        option = Option(goal_strike, goal_expr, order['side'])
        # print('option date', option.expr, type(option.expr))
        o = find_closest_option(option)
        try:
            res = options_limit_order(o, order['qty'])
            receipts.append({'side': 'bought', 'name': o.name, 'qty': order['qty'], 'status': res.status})
            exit_date = find_closest_open_day(date.today() + timedelta(days=1))
            port.add_position(o, o.symbol, order['qty'], date.today(), exit_date) # add to portfolio for logging. will be saved and loaded on next code execution
            # print(res.status)
        except Exception as error:
            print("error at order placing")
            record_results("failed to submit buy order", error=str(error))
    record_results("order success", receipts=receipts)
    return port   


def find_closest_option(option: Option):
    '''
    finds live option that best matches desired strike and expiration
    option: an object from the Option class'''
    min_expiration = option.expr
    max_expiration = option.expr + timedelta(days=5)

    min_strike = str(round(option.strike*.97,2))
    max_strike = str(round(option.strike*1.03,2))

    options_chain_list = options_chain_req("SPY", option.side, None, min_expiration, max_expiration,  min_strike, max_strike) # get a lot of em

    # find market day closest to desired expiration
    day_found = False
    while not day_found:
        for o in options_chain_list:
            # print(o.expiration_date, Option.expr.date(), o.expiration_date == Option.expr.date(), type(o.expiration_date), type(Option.expr.date()))
            if o.expiration_date == option.expr:
                day_found = True
                break
        if o.expiration_date != option.expr:
            option.expr += timedelta(days=1)

    options_chain_list_reduced = options_chain_req("SPY", option.side, option.expr, None, None,  min_strike, max_strike) # get only on correct day
    # find option closest to desired strike
    price_diff = 100
    for o in options_chain_list_reduced:
        if  abs(o.strike_price-option.strike) < price_diff:
            price_diff=abs(o.strike_price-option.strike)
            closestOpt = o

    # print(closestOpt)
    return closestOpt


def options_chain_req(underlying_symbol, side, expiration_date=None, min_expiration=None, max_expiration=None, min_strike=None, max_strike=None):
    '''
    Get an options chain that satisifies given criteria.
    This function can handle if the chain is over 1 page (100 options) long
    underlying symbol: str
    side: str 'call' or 'put'
    all dates in datetime.date
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


def find_closest_open_day(date):
    '''given a date, it will return the soonest market open date
    date: datetime.date
    note: in the future i might want to make this take an input of how many days timedelta'''
    end_date = date + timedelta(days=4)
    req = GetCalendarRequest(start=date, end=end_date)
    res = trade_client.get_calendar(req)

    open_days = [day.date for day in res]
    while date not in open_days:
        date += timedelta(days=1)
    return date


def options_limit_order(option, qty):
    '''option: just how it is output from alpaca
    qty: float or int    '''
    option_quote_request = OptionLatestQuoteRequest(symbol_or_symbols=option.symbol)
    option_quote = option_data_client.get_option_latest_quote(request_params=option_quote_request)
    mid_price = round((option_quote[option.symbol].bid_price + option_quote[option.symbol].ask_price)/2,2)
    # print('mid price:', mid_price)
    req = LimitOrderRequest(
        symbol=option.symbol,
        qty=qty,
        limit_price = mid_price,
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        time_in_force = TimeInForce.DAY
        )

    # print(req)
    res = trade_client.submit_order(req)
    return res # optional return
    

def close_position(pos: Position, order_type, receipts):
    '''this is a separate function than options_limit_order bc it takes a different type of input'''
    try:
        if order_type == 'limit':
            option_quote_request = OptionLatestQuoteRequest(symbol_or_symbols=pos.symbol)
            option_quote = option_data_client.get_option_latest_quote(request_params=option_quote_request)
            mid_price = round((option_quote[pos.symbol].bid_price + option_quote[pos.symbol].ask_price)/2,2)

            req = LimitOrderRequest(
                symbol=pos.symbol,
                qty=pos.qty,
                limit_price = mid_price,
                side=OrderSide.SELL,
                type=OrderType.LIMIT,
                time_in_force = TimeInForce.DAY )

            res = trade_client.submit_order(req)
        elif order_type=='market':
            res = trade_client.close_position(symbol_or_asset_id=pos.symbol)
        receipts.append({'side': 'sold', 'name': pos.symbol, 'qty': pos.qty, 'status': res.status})
    except Exception as error:
        print('close position failed')
        record_results('failed to place sell order', error=str(error))
    return  receipts #res
