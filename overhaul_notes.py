#this has been renamed from new_start.py
'''
classes
APART FROM LIVE AND BT, ALL CLASSES USED IN BOTH IMPLEMENTATTIONS
livetrader
-houses live trading infrastructure + brokerage
backtester
-constructor -data, strat, starting amts, commissions

Portfolio
Order -> has subclasses for each order type.
 - new pseudo attribute flags if an order is actually in brokerage or not, and if needs to be monitored
Position
    Stock
    Option
Broker
 - this class handles interactions between strategy, portfolio, and the outside environment (bt or live)
 - btbroker and alpacabroker subclass override to handle their environments
Strategy (this is a parent class/can be ovveridden)
 - init setup
 - next/updates procedures
 - serves as the commander for most things, though the live script and bt class are higher in command

INPUTS
-stock and option data from internet or local both parsed into uniform format (PD Dateframe)
-data handled by broker class and given to strat
OUTPUTS
-broker classes don't handle output, they only handle data input into strat/port
-strat methods can output things up to backtesting class or live script for recording
    -backtesting: trades are stored into a list and outputted at the end, also output to file
    -live script: trades are logged in .log and occasionally emailed

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

BT RESPONSIBILITIES

BT Class roles:
manage pseudo time
run strategy at each time
track positions in portfolio
track entries/exits -> trade log
handle commisions -> log final trade PL

BT broker roles:
get data for signals and order prices
keep its own 'online' tally of ords & pos for when queried
calculate NAV (get_acct_details)

add ran_today() database var so if it never runs in the day then at anypoint after 3:45 then run it

strat will self.broker = whichever, and can query either one for data as if both are APIs
strat.porfolio will also have self.broker, which is auto passed in for doing its own portfolio updating

trades are handled by strat class. srat.place_order() will call broker.place_order() and 
then call port.add_order() or whatever is needed. So like- strategy handles the calls.

first day init no longer neede it'll just be handled as none case in monitor and event
no more default strat needed. just setup the "default" into the base parent class
if you want to try variations, make new child classes and overwrite parent methods

-api keys and TRADING_MODE constant will be stored in env, switch between modes by changing the const
    - in any needed case you can switch modes by rerunning initialize_clients()

.run() should be parallel funcs/methods in BT notebook and live script, not in strat

refine event functionality

structural tweaks to consider
-base broker should be an abstract class? and define methods as @abstractmethod
-delta_orders can be list of dicts like it previously was, don’t need a class for it

minor changes to make
-make all datetime usage import datetime as dt, and do dt.datetime, dt....
-later go through and convert all single quotes '''''' to dbl quotes """"""
-ensure 2 lines between class defs, 1 line between methods, 2 lines between top level funcs
'''
