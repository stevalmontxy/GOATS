'''
classes
APART FROM LIVE AND BT, ALL CLASSES USED IN BOTH IMPLEMENTATTIONS
livetrader
-houses live trading infrastructure + brokerage
backtester
-constructor -data, strat, starting amts, comissions

portfolio
Order -> has subclasses for each order type
position
    stock
    option

strategy (this is a parent class/can be ovveridden)
-init setup
-next/updates procedures

trade is not a class, "trade" can be name for logging purposes
MAYBE set a constant LIVE = true, or BACKTEST = true
if (LIVE), elif (BACKTEST) else throw error
just in the regular
maybe make it a @dataclass (python's "structs"), same w position, option, stock, order

INPUTS
stock and option data both PD Dateframe
can be parsed into uniform format from internet or excel/csv
OUTPUTS
trade log
if backtest, output overall results
if live, send email updates

BT
-init
-setup portfolio
-declare time
-loop
-(see below)
-end log, make plots

live
-init
-get portfolio state everytime
-maybe compare w expected?
-(see below)

the "see below" part
-get price data
-evaluate
-make trades
-log

BT will probably use hourly or so data.
live will update at least every 15min, as low as every 5sec

in more detail:
BT
-init bt
-bt.run(data, starttime, endtime, other stuff)
    -init portfolio, time
    -setup signals/data for ALL at once
    -while(time<endtime)
        -setup current data
        -strat.run(current data) on portfolio
        -increment time

live
-init portfolio and broker connection
-refetch portfolio & positions n stuff
-strat.run()
    -run indefinitely from market open until market close of day

should I make a subclass psuedotrade?

add ran_today() database var so if it never runs in the day then at anypoint after 3:45 then run it

need to create broker class, will have child classes BTbroker and alpacabroker(live)
alpacabroker will be mostly a wrapper over the alpaca preexisting API
bt may need another class just for managing stuff. but for live, maybe it doesn't need its own class
the rest of implementation can just be standalone functions
strat will self self.broker = whichever, and can query either one for data as if both are APIs
strat.porfolio will also have self.broker, which is auto passed in for doing its own portfolio updating

to place a trade, you can either do strat.broker.place_order(), then strat.port.add_order()
or do like strat.port.place_order(), and call broker from internally. but i think that's more hidden
maybe best is strat.broker.place_order(), then strat.port.update_port() at the end of multiple orders

first day init no longer neede it'll just be handled as none case in monitor and event
no more default strat needed. just setup the "default" into the base parent class
if you want to try variations, make new child classes and overwrite parent methods

.run() should be parallel funcs/methods in BT and live, not in strat
they will look very similar to the current strat.run()

refine event functionality
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
from ibapi.order import order
from ibapi.common import bardata

#dual inheriting?!
class tradingapp(EClient, EWrapper):
    def __init__(self) ->None:
        ECLient.__init__(self, self)
        self.data: Dict(int, pd.dataframe) = {}
    
    #parent overload
    def error():
        pass

    def get_historical_data():
        self.data[reqID] = pd.dataframe(columns = [open, high, low, close, time],
                                        set_index = time)
        
        self.reqHistoricalData(
            # this is a method from eclient i think
            #lots of options here
            )
        time.sleep(3)
        return self.data[reqID]

def historicalData(redID):
    #this is another overload that gets thedata from t he reqhistoricadata into the 
    self.data[reqid]

@staticmethod
def get_contract(symbol: str):
    #this just turna a stock symbol str into a contract objecty
    contract = contract
    contract.symbol = sytmbol
    contact.type = "Stock"
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