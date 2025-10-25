'''
classes
APART FROM LIVE AND BT, ALL CLASSES USED IN BOTH IMPLEMENTATTIONS
livetrader
backtester

portfolio
trade MAYBE NO
Order -> has subclasses for each order type
position
    stock
    option

THINK ABT HOW POSITION, TRADE, ORDER, Stock/option work together
strategy (this is a parent class/can be ovveridden)
MAYBE set a constant LIVE = true, or BACKTEST = true
if (LIVE), elif (BACKTEST) else throw error
just in the regular
live methods not static, live class also has broker attribute

I/O
stock and option
data both PD Dateframe
timeseries
can be parsed into uniform format from itnernet or excel/csv
output trade log
if backtest, output overall results

BT
-init
-setup portfolio
-declare time
-loop
(see below)
-end log, make plots

live
-init
-get portfolio state everytime
-maybe compare w expected?
-get time
perform (see below)

the "see below" part
-get price data
-evaluate
-make trades
-log

strat
-init setup
-next/updates

Backtest
-constructor -data, strat, starting amts, comissions
'''

#notes from vidieso
#from 13 min vid
#import time, threading, from datetime import datetime
from typing import Dict, Optional
import pandas as pd
import warnings
warnings.filterwarnings("igonre")
#interactive broker is like a specific thing
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import contract
from ibapi.order ipmort order
from ibapi.common import bardata

#dual inheriting?!
class tradingapp(EClient, EWrapper):
    def __init__(self) ->None:
        ECLient.__init__(self, self)
        self.data: Dict(int, pd.dataframe) = {}
    
    #parent overload
    def error:
        pass

    def get_historical_data()
        self.data[reqID] = pd.dataframe(columns = open high low close time
        set index = time)
        
        self.reqHistoricalData(
            # this is a method from eclient i think
            #lots of options here
            )
        time.sleep(3)
        return self.data[reqID]

def historicalData(redID)
    #this is another overload that gets thedata from t he reqhistoricadata into the 
    self.data[reqid]

@staticmethod
get_contract(symbol: str)
    #this just turna a stock symbol str into a contract objecty
    contract = contract
    contract.symbol = sytmbol
    contact.type = :"Stock"
    contract.currency = "usd"
    return contract



app = tradingApp()

app.connect("127.0.0.1", 7489, clientId=5)

#this lets the app run on a thread and you can run other code. he was doing it in ipyrnb
threading.thread(target=app.run, raemon=True).start()

#this is static method
nvda = tradingapp.get_contact("nvda)")


app.gethistoricaldata(99, nvda)

### other video, more abt the ip async library
#uses mroe async def, await

# for example it can start by getting current high and low, subscribe, 
# #check every 5 second candles, take action for breakouts 
# learn to use async: send out your requests all at once,
#  then you don't have to wait for each to return sequentially
# this could be useful in dual orders - or just can yhou pair them as one order?

# next video: he uses ib.reqRealTimeBars() with async
# https://www.youtube.com/watch?v=a1813iCcsWQ