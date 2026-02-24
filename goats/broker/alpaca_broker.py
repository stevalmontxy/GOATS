# Standard Imports
import datetime as dt

# Third Party Imports
import pandas as pd
import requests as rq

from alpaca.data.historical.stock import StockHistoricalDataClient, StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.historical.option import OptionHistoricalDataClient, OptionLatestQuoteRequest
from alpaca.data.timeframe import TimeFrameUnit, TimeFrame
from alpaca.trading.client import TradingClient 
from alpaca.trading.enums import AssetStatus, ContractType, OrderSide, OrderType, TimeInForce
from alpaca.trading.requests import GetOptionContractsRequest, LimitOrderRequest, GetCalendarRequest

# Local Imports
from .broker import Broker
from ..core.core_objects import Account, Stock, Option, Order, LimitOrder, Position

# shelve is handled fully in live script
# api keys are imported in the live script/testing script
# emailing/recording/logging results is handled in the live script

class AlpacaBroker(Broker):
    '''AlpacaBroker is how the strategy/portfolio classes interact 
    with market data or account orders and positions. Once initialized,
    its methods can be called without reauthenticating. it only stores 1 set
    of api keys, and the paper var has no defaults, ensuring the user sets the 
    api keys and paper var carefully. '''
    def __init__(self, api_key, secret_key, paper):
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper # bool
        self.initialize_clients(api_key, secret_key, paper)

    def initialize_clients(self, api_key, secret_key, paper):
        '''AlpacaBroker ONLY METHOD
        it is automatically called in init but you can recall it if you need to switch clients
        defining this as its own function in case it makes sense to call it to change the mode the broker is in 
        between paper and live'''
        self.trade_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)
        self.stock_data_client = StockHistoricalDataClient(api_key=api_key, secret_key=secret_key)
        self.option_data_client = OptionHistoricalDataClient(api_key=api_key, secret_key=secret_key)

    # === Fetching Data ===

    def get_stock_data(self, symbol, timeframe, num_days) -> pd.DataFrame:
        '''
        This gets historic stock data, used for signals n stuff
        TAKING OVER FOR createUnderlydf(symbol, dataInterval, dataPeriod)
        Creates a simple dataframe of candlesticks (OHLC) of live stock data
        symbol: str
        timeframe: str ('1hour')
        num_days: int (number of days desired)'''
        start_date = dt.date.today() - dt.timedelta(days=num_days)
        if timeframe == "1Hour":
            timeframe = TimeFrame(1, TimeFrameUnit.Hour)
        elif timeframe == "1Min":
            timeframe = TimeFrame(1, TimeFrameUnit.Minute)
        else:
            raise NotImplementedError
    
        req = StockBarsRequest(symbol_or_symbols=symbol, start=start_date, end=None, timeframe=timeframe)
        barset = self.stock_data_client.get_stock_bars(req)
        df = self.barset_to_df(barset, symbol)
        return df # type: pd.Dataframe

    def get_latest_quote(self, symbol=None, asset=None):
        '''returns latest quote (bid ask, etc), intake is very flexible
        for now this function is not in use or fully written'''
        # if self.quote_source != 'alpaca_rest':
        raise NotImplementedError # not needed yet, may write later

    def get_options_chain(self, underlying_symbol, side, expiration_date=None, 
        min_expiration=None, max_expiration=None, min_strike=None, max_strike=None):
        '''skipping for now, just use get_options_contracts()'''
        raise NotImplementedError # not needed yet, may write later

    def get_options_contracts(self, underlying_symbol, side, expiration_date=None, 
        min_expiration=None, max_expiration=None, min_strike=None, max_strike=None): # return is not pd.dateframe
        '''
        This gets the list of possible options without price data
        Get an options chain that satisifies given criteria.
        underlying symbol: str
        side: str 'call' or 'put'
        all dates in datetime.date
        min strike, max strike: float or int'''
        type = ContractType.CALL if side == 'C' else ContractType.PUT

        req = GetOptionContractsRequest(
            underlying_symbols=[underlying_symbol], # specify symbol(s)
            status=AssetStatus.ACTIVE, # specify asset status: active (default)
            expiration_date=expiration_date, # specify expr date (specified date + 1 day range)
            expiration_date_gte=min_expiration, # can pass date obj or string (YYYY-MM-DD)
            expiration_date_lte=max_expiration,
            root_symbol=underlying_symbol, # specify root symbol
            type=type, # either ContractType.CALL or ContractType.PUT
            # style=None, # either american or european
            strike_price_gte=str(min_strike), # strike price range
            strike_price_lte=str(max_strike),
            limit=1000, # specifiy limit
            # next is switching to get options_chainriequest in optionsclient not trading client
            # and make a return one that has pd.dataframe
            page_token=None
        )
        res = self.trade_client.get_option_contracts(req)
        options_contract_list = res.option_contracts

        return options_contract_list

    def get_closest_option(self, option: Option) -> Option:
        ''' finds live option that best matches desired strike and expiration'''
        min_expiration = option.expr
        max_expiration = option.expr + dt.timedelta(days=5)

        min_strike = str(round(option.strike*.97,2))
        max_strike = str(round(option.strike*1.03,2))

        options_chain_list = self.get_options_contracts(option.underlying, option.side, None, min_expiration, max_expiration,  min_strike, max_strike) # get a lot of em

        # find market day closest to desired expiration
        day_found = False
        while not day_found:
            for o in options_chain_list:
                # print(o.expiration_date, Option.expr.date(), o.expiration_date == Option.expr.date(), type(o.expiration_date), type(Option.expr.date()))
                if o.expiration_date == option.expr:
                    day_found = True
                    break
            if o.expiration_date != option.expr:
                option.expr += dt.timedelta(days=1)

        options_chain_list_reduced = self.get_options_contracts(option.underlying, option.side, option.expr, None, None,  min_strike, max_strike) # get only on correct day
        # find option closest to desired strike
        price_diff = 100
        for o in options_chain_list_reduced:
            if  abs(o.strike_price-option.strike) < price_diff:
                price_diff=abs(o.strike_price-option.strike)
                closest = o

        return Option(closest.strike_price, closest.expiration_date, option.side, option.underlying, closest.symbol) 

    def get_closest_open_date(self, date) -> dt.date:
        '''given a date, it will return the soonest market open date
        date: dt.datetime.date'''
        end_date = date + dt.timedelta(days=4)
        req = GetCalendarRequest(start=date, end=end_date)
        res = self.trade_client.get_calendar(req)

        open_dates = [day.date for day in res]
        while date not in open_dates:
            date += dt.timedelta(days=1)
        return date

    def now(self):
        now = dt.datetime.now()
        return now.replace(second=0, microsecond=0) 

    def get_open_hours(self):
        # will get market open and close time to know if ends early
        pass

    def barset_to_df(self, barset, symbol) -> pd.DataFrame:
        '''AlpacaBroker ONLY METHOD'''
        bars = barset[symbol]
        df = pd.DataFrame([b.model_dump() for b in bars])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df

    def option_sym_to_object(self, symbol) -> Option:
        '''AlpacaBroker ONLY METHOD'''
        opt = self.trade_client.get_option_contract(symbol)
        return Option(opt.strike_price, opt.expiration_date, opt.type, opt.underlying_symbol, symbol)

    # === Executing Orders ===

    def place_order(self, order): # returns res
        # '''works for single order or multiple orders'''
        # if isinstance(orders, Order): # if single order
        #     orders = [orders]
        
        # res = []
        # for order in orders:
        if order.qty > 0:
            side = OrderSide.BUY
        else:
            side = OrderSide.SELL
            order.qty *= -1
        
        if type(order) == LimitOrder and order.is_stock: # limit stock order
            if order.limit_price is None:
                stock_quote_request = StockLatestQuoteRequest(symbol_or_symbols=order.symbol)
                stock_quote = self.stock_data_client.get_stock_latest_quote(request_params = stock_quote_request)
                order.limit_price = round((stock_quote[order.symbol].bid_price + stock_quote[order.symbol].ask_price)/2,2) # mid price
            req = LimitOrderRequest(
                symbol=order.symbol,
                qty=order.qty,
                limit_price = order.limit_price,
                side=side,
                type=OrderType.LIMIT,
                time_in_force = TimeInForce.DAY
                )
            res = self.trade_client.submit_order(req)

        elif type(order) == LimitOrder and not order.is_stock: # limit option order
            if order.limit_price is None:
                option_quote_request = OptionLatestQuoteRequest(symbol_or_symbols=order.symbol)
                option_quote = self.option_data_client.get_option_latest_quote(request_params=option_quote_request)
                order.limit_price = round((option_quote[order.symbol].bid_price + option_quote[order.symbol].ask_price)/2,2) # mid price 
            req = LimitOrderRequest(
                symbol=order.symbol,
                qty=order.qty,
                limit_price = order.limit_price,
                side=side,
                type=OrderType.LIMIT,
                time_in_force = TimeInForce.DAY
                )
            res = self.trade_client.submit_order(req)

        elif type(order) == ScheduledOrder and not order.is_stock: # scheduled option order
            option_quote_request = OptionLatestQuoteRequest(symbol_or_symbols=order.symbol)
            option_quote = self.option_data_client.get_option_latest_quote(request_params=option_quote_request)
            order.limit_price = round((option_quote[order.symbol].bid_price + option_quote[order.symbol].ask_price)/2,2) # mid price 
            req = LimitOrderRequest(
                symbol=order.symbol,
                qty=order.qty,
                limit_price = order.limit_price,
                side=side,
                type=OrderType.LIMIT,
                time_in_force = TimeInForce.DAY
                )
            res = self.trade_client.submit_order(req)

        elif type == other:
            raise NotImplementedError("Only doing limit orders for now")

        return res

    def delta_order_to_orders(self, delta_orders): # returns res
        '''takes over for order_maker_live(orders, underlying_last, port: Portfolio, receipts, time=None):
        works for single order or multiple orders on same
        example:    delta_orders = [
                        {'strikeDist': 1, 'exprDist': 2, 'side': 'call', 'qty': 1, underlying: "SPY"},
                        {'strikeDist': -1, 'exprDist': 2, 'side': 'put', 'qty': 1, underlying: "SPY"} ]
        '''
        for order in orders:
            goal_strike = underlying_last + order['strike_dist']
            goal_expr = dt.date.today() + dt.timedelta(days=order['expr_dist'])
            option = Option(goal_strike, goal_expr, order['side'])
            # print('option date', option.expr, type(option.expr))
            o = find_closest_option(option)
            try:
                res = options_limit_order(o, order['qty'])
                receipts.append({'side': 'bought', 'name': o.name, 'qty': order['qty'], 'status': res.status})
                exit_date = find_closest_open_date(dt.date.today() + dt.timedelta(days=1))
                port.add_position(o, o.symbol, order['qty'], dt.date.today(), exit_date) # add to portfolio for logging. will be saved and loaded on next code execution
                # print(res.status)
            except Exception as error:
                print("error at order placing")
                record_results("failed to submit buy order", error=str(error))
        record_results("order success", receipts=receipts)
        return res

    def cancel_order(self, order_id): # returns res
        '''works for single order or multiple orders'''
        res = self.trade_client.cancel_order_by_id(order_id) 
        return res

    def cancel_all_orders(self): # returns res
        res = self.trade_client.cancel_orders()
        return res

    def close_position(self, symbols=None, asset=None, order_type='market'): # returns res
        '''works for single order or multiple orders
        this is a separate function than options_limit_order bc it takes a different type of input
        note: currently don't know what to do with this function, since can just use place_order to sell, 
        so for now this method will just do market close type '''
        
        if isinstance(symbols, str): # if single order
            symbols = [symbols]
        
        res = []
        for symbol in symbols:
            if order_type=='market':
                res.append(self.trade_client.close_position(symbol_or_asset_id=symbol))
            elif order_type == 'limit':
                res.append(self.place_orders(LimitOrder(symbol=symbol, qty=-qty)))
        return res

    def close_all_positions(self): # returns res
        res = self.trade_client.close_all_positions()
        return res

    # === Querying Portfolio ===

    def get_open_orders(self) -> list[Order]:
        orders = self.trade_client.get_orders()
        ord = []
        for o in orders:
            if o.symbol.startswith("$"): # idk why it does this
                o.symbol = o.symbol[1:]

            if o.limit_price is not None:
                if o.asset_class == 'us_option':
                    ord.append(LimitOrder(symbol=o.symbol, qty=o.qty, limit_price=o.limit_price)) 
                elif o.asset_class == 'us_equity':
                    ord.append(LimitOrder(symbol=o.symbol, qty=o.qty, limit_price=o.limit_price))
            else:
                raise NotImplementedError("Only handling LimitOrders for now")
        return ord

    def get_positions(self) -> list[Position]:
        positions = self.trade_client.get_all_positions()
        pos = []
        for p in positions:
            if p.asset_class == 'us_option':
                pos.append(Position(symbol=p.symbol, asset=self.option_sym_to_object(p.symbol), qty=p.qty, price=p.current_price))
            elif p.asset_class == 'us_equity':
                pos.append(Position(symbol=p.symbol, asset=Stock(p.symbol), qty=p.qty, price=p.current_price))
        return pos

    def get_acct_value(self) -> Account:
        account = self.trade_client.get_account()
        return Account(float(account.cash), float(account.buying_power), float(account.portfolio_value))
