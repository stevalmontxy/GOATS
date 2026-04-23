# Glorious Options Automated Trading System (GOATS) Overview
### Conception and Principle
I've been trading options for a couple years now, and have previously created algorithmic trading bots for stocks and forex. As my coding and trading have improved, I've decided it's time to go for something more challenging. GOATS is a pet project I made to backtest and rapidly deploy options trading strategies, and for the fun/challenge of it. Unlike my past technical analysis based trading bots, the focus here is on having a directional/vol hypothesis, and trading off that rather than trying to tailor technical indicators or trade arb.

Here are some core features of the system:
- Rapid deployment
  - To backtest a new strategy, you just have to write a new Strategy child class (like in some other backtesters). To deploy it, all you have to do is swap it into the live running script and make minimal tweaks, rather than writing a whole separate program
- Options capability
  - This system is capable of backtesting and trading stocks and options, while few backtesters can handle options. Having my own system also means no weird workarounds as I can design for what I need and want
- Constant Monitoring
  - Unlike my past systems which set a SL or TP order and let it play out, this system is designed for strategies which actively monitor the market and position and choose exit
- Order "chasing"
  - Due to the large bid/ask spread of options, limit orders are a must. Paired with the constant monitoring, if an order isn't filled on entry/exit, the system will monitor and adjust the limit price (WIP)

### Architecture and Call Heirarchy
[add architecture diagram and call heirarchy]

In both backtesting and live deployment, the system uses:
- Stock/Option: base asset classes
- Position: wrapper that holds a Stock or Option object
- Order - base class for handling execution (contains several child classes)
- Portfolio: holds positions, orders, and "pseudo orders"
- Broker: handles interactions between strategy, portfolio, and the outside environment (bt or live)
  - BtBroker and AlpacaBroker subclass override to handle their environments
- Strategy: parent class meant to be subclassed
  - Serves as the commander for most things, though the live script and bt class are higher in command

These can be initialized and a backtest/live can be run from the backtesting notebook or live script

##### Inputs
- Stock and option data from brokerage or local both parsed into uniform format (PD Dateframe)
- Data handled by broker class and passed to strat
##### Outputs
- Broker classes don't handle output, they only handle data input into strat/port
- Strat methods can output things up to backtesting class or live script for recording
  - Backtesting: trades are stored into a list and outputted at the end, also output to file
  - Live script: trades are logged in .log and occasionally emailed

<!--
running procedure

BT
- init
- setup portfolio
- declare time
- loop
- (see below)
- end log, make plots

live
- init
- get portfolio state everytime
- maybe compare w expected?
- (see below)

the "see below" part
- get price data
- evaluate
- make trades
- log

currently, BT runs on 30 min data. Live updates every 5 seconds rather than using stream

BT Class roles:
- manage pseudo time
- run strategy at each time
- track positions in portfolio
- track entries/exits -> trade log
- handle commisions -> log final trade PL

BT broker roles:
- get data for signals and order prices
- keep its own 'online' tally of ords & pos for when queried
- calculate NAV (get_acct_details)
-->

<!--
### Insides of strategy
[outdated]
#### Vol and Dir functions (part of sentiment class)
- Volatility is a function of previous day move size, significant events, card count(like from blackjack. I am still working this idea out), technical analysis (TA, though I will try to minimize its use), time since last big move
    - can be multidimensional (defined using a distribution, not a singular value)
- Directional sentiment is a function of previous day move size and direction, static bias, mean reversion, card count, TA
    - for low levels of dir, the static bias is pretty strong, and the ratio call:put is pretty high. actually it should be whatever dir the long MA is (long term trend)

#### Strategy top level
[outdated]
- for low vol, the dir is taken as the call:put ratio. but for higher vol, the ratio gets closer and closer to central.
- when dir conviction is high, size increases notably. Overall, vol is the scalar while dir is the ratio. but when dir is high, scale will be increased.
- if dir belief is high, but vol belief is low, maybe shold buy longer DTE options? for high vol belief, lower DTE. for high dir belief, maybe buy lower DTE in the belief dir and longer DTE in opposing.
- usually, the bot should just buy at open, sell next day close. in the middle time, it buys different options the "next day", and the third day sells those, so there is always overlap. 
- I think likely it will always plan to buy and sell options with at least 1DTE (not holding til expr day).
    - but a deviation case is maybe given a certain condition to hold one fully til expr, but keep buying the others
    - for example, usually, with a regular situation, and a good profit on one side, both positions would close and reset and do the next day. BUT if the new vol and dir is higher, maybe don't TP, hold and go for big profit. or instead of buying call:put ratio, do 1/2*(2call):put. what I mean by that is put the same amt into the call side as usual, but put more OTM to have higher leverage.
- a lighter deviation could be for outlying vol and dir, instead of buying new ones, always buying the same DTE, it can buy the same position (having shorter DTE) the next day if conviction in something is high
- TP can be a thing maybe. if we want the bot to run more frequently.
    - yk maybe I do want that. that would be a good benefit of having a bot that can always be checking the stock price n stuff
-->

### Implementation
Creating new strategies will be as easy as creating a new Strategy child class, and overriding the desired methods. This can easily then run in backtesting, and swapped into the live running setup. For me, my live running setup is a cheap lightweight linux setup.

### Setup and Installation
- Historic data: OptionsDX
- Live running: put api keys in .env
- Run the following:
```bash
chmod +x /home/stevalmontxy/Documents/Github/GOATS/scripts/run_live.sh
```
##### Setup-cron
On archlinux, access with "crontab -e"
```bash
# CRONTAB runs on laptop's timezone
30 09 * * 1-5 /[filepath]GOATS/scripts/run_goats.sh >> /home/stevalmontxy/.../goats_live.log 2>&1
```

<!--
### Sources that helped me
- systematic trading (robert carver) - overall framework   
- the leverage space trading model (ralph vince) - helped in sizing   
- trading in the zone (mark douglas) - helped with my discretionary trading that I incorporated into the system  
- bayesian statistics the fun way (will kurt) - helped with analysis and hypothesis testing  
- option volatility and pricing (sheldon natenberg) - of course  
- backtesting.py package
- alpaca API docs
-->

### Current state of the project
As of April 2026, the core infrastructure for both backtesting and live execution are fully built. A live paper trading account is actively running a demo strat.

My next steps right now are writing up a strategy -> backtesting -> live testing -> put money in. I expect to continue to refining and developing strategies. Afterward, my future plans for the project are continual refinement and eventually testing some reinforcement learning (PPO) since I think that's interesting.
