# Glorious Options Automated Trading System (GOATS) Overview
### Conception and principle
I have been trading options for a while now, and having previously created algorithmic trading systems for stocks and forex that use technical analysis. However, my coding has improved and I like options, and wanted to go for something more challenging. GOATS is a pet project of mine with custom infrastructure to backtest and deploy more complex strategies designed for options. Instead of running once Here is the big challenge that I have been thinking up for a while now. Essentially I wanted to build my personal trading strategy into an auto every hour or 15 minutes, I want this system to run during market hours, subscribing to live quotes and constantly checking its criteria for entry/exit.

In the past I have utilized backtesting packages and created my own more simple trading systems,and I know there are preexisting systems for backtesting on options, but a big motivation for making this is I think it will be a good exercise of making a larger coding project for me, where I can do some OOP.

### Current state of the project
If you're reading this, I am in the middle of a large restructuring. Getting it back to a running system means: running live and backtesting scripts both utilizing the SAME core classes, with only minor differences in how they use the backtesting and live classes. Afterward, my future plans for the project are continual refinement and eventually testing some machine learning stuff.

### Overall Layout
[outdated]
[add architecture diagram and call heirarchy from ipad]
- One that runs in morning (buying time)
- one that runs right after buying time (or it could be part of buying time) to confirm successful order fill. or it could keep running until order filled
- one that runs near end of day (selling time)
- one that runs end of week to summarize successful and failed script builds. summarized positions and portfolio status
- one that runs monthly to auto update parameters  
   


### Insides of strategy
[outdated]
#### Vol and Dir functions (part of sentiment class)
- Volatility is a function of previous day move size, significant events, card count(like from blackjack. I am still working this idea out), technical analysis (TA, though I will try to minimize its use), time since last big move
    - can be multidimensional (defined using a distribution, not a singular value)
- Directional sentiment is a function of previous day move size and direction, static bias, mean reversion, card count, TA
    - for low levels of dir, the static bias is pretty strong, and the ratio call:put is pretty high. actually it should be whatever dir the long MA is (long term trend)

#### Strategy top level
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



### Implementation
Creating new strategies will be as easy as creating a new Strategy child class, and overriding the desired methods. This can easily then run in backtesting, and swapped into the live running setup. For me, my live running setup will be a cheap lightweight linux setup.



### Setup
[still in progress] If you want to run this yourself, you will need some files that I have .gitignored away. for backtesting, you will need your own data. I got mine off of OptionsDX. for live implementation, you will need a .env file with your API keys and project root directory. I think the last thing is just to make sure you keep the significant_dates file kept up to date. for live execution, then only one necessary is the one in /src/live. Should be it.


##### Setup-cron

on archlinux, access with "crontab -e"

```bash
# CRONTAB runs on laptop's timezone
45 15 * * 1-5 python /home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/live/run_closing_script.py
45 15 * * 7 python /home/stevalmontxy/Documents/Programming/tester.py
```

### Sources that helped me
- systematic trading (robert carver) - overall framework   
- the leverage space trading model (ralph vince) - helped in sizing   
- trading in the zone (mark douglas) - helped with my discretionary trading that I incorporated into the system  
- bayesian statistics the fun way (will kurt) - helped with analysis and hypothesis testing  
- option volatility and pricing (sheldon natenberg) - of course  
- backtesting.py package
- alpaca API docs
