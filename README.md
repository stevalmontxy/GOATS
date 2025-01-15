# Glorious Options Automated Trading Strategy (GOATS) Overview
### Conception and principle
I have been trading options for a while now, and having previously created algorithmic trading systems that use technical analysis. However, my coding has improved and I like options, and wanted to go for something more challenging. Here is the big challenge that I have been thinking up for a while now. Essentially I wanted to build my personal trading strategy into an automated system, with a few tweaks. Being automated will give it some disadvantages to a human, but will have many advantages also. It can't "think" past some (not so) simple rules, but, it can check the market nonstop, factor in a ton of things evenly, and has no problem and never gets tired of doing sizing calculations. It can hold many positions and keep track of each ones exit, and do complicated things that would take a good amount of effort for me to personally keep track of while balancing school and life. You could def argue that the time to ponder and write the system is probably huge, and it definitely is. But I have been thoroughly enjoying it. I have built a system that is quite complex, self operating, but also, has room and I have plans to continually upgrade and add depth to the bot's systems.




### Overall Layout
__4__ different scripts:
- One that runs in morning (buying time)
- one that runs right after buying time (or it could be part of buying time) to confirm successful order fill. or it could keep running until order filled
- one that runs near end of day (selling time)
- one that runs end of week to summarize successful and failed script builds. summarized positions and portfolio status
- one that runs monthly to auto update parameters  
   


### Insides of strategy
  
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




[have a timeline diagram to show the standard procedure and deviations]




### Implementation
Once up and running, I plan to run the code on a linux machine setup for CI/CD on a cheap laptop I bought.



### continuous integration and continuous deployment
So evidently there is a ton of stuff I can work on and add to the system. There will always be things to research and add to the vol and dir calcs, and the strategy may change with its deviations. so it's really important that I make the code be able to be changed in terms of structure and stuff down the line.




### Sources that helped me
systematic trading (robert carver) - overall framework   
the leverage space trading model (ralph vince) - helped in sizing   
trading in the zone (mark douglas) - helped with my discretionary trading that I incorporated into the system  
bayesian statistics the fun way (will kurt) - helped with analysis and hypothesis testing  
option volatility and pricing (sheldon natenberg) - of course  
backtesting.py package - I took a lot of reference from this
