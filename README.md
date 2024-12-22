# [name of project] Overview
First off, I need to come up with a cool name for this. I'm thinking a name for a firm could be principle axis capital management or something, but there is no tie in of principal axis, eigen value, or anything related. but would be a cool name. ANYWAY, pseudo code.
### Conception and principle
I have been trading options for a while now, and having previously created algorithmic trading systems that use technical analysis. However, my coding has improved and I like options, and wanted to go for something more challenging. Here is the big challenge that i have been thinking up for a while now. Essentially I wanted to build an options trader that will have some disadvantages to a human, but will have many advantages over me. It can't think past some (not so) simple rules, but, it can check the market nonstop, factor in a ton of things evenly, and has no problem and never gets tired of doing sizing calculations. It can hold different positions and make them extend, and do complicated things that would take a good amount of effort for me to personally keep track of while balancing school and life. You could def argue that the time to ponderand write the system is probably huge, and it definitely is. But I have thoroughly enjoyed it. I have built a system that is quite complex, self operating, but also, has room and I have plans to continually upgrade and add depth to the bots systems




### Overall Layout
__4__ different scripts:
- One that runs in morning (buying time)
- one that runs right after buying time (or it could be part of buying time) to confirm successful order fill. or it could keep running until order filled
- one that runs near end of day (selling time)
- one that runs end of week to summarize successful and failed script builds. summarized positions and portfolio status
- one that runs monthly to auto update parameters  
   

Since this is built locally, is there a way to write to log and read that log in future runs? that would be pretty useful




### Insides of strategy
  
#### Vol and Dir functions
- Vol is a function of previous day move size, significant events, card count, TA, time since last big move
    - can be multidimensional (defined using a distribution, not a singular value)
- Dir is a function of previous day move size and direction, static bias, mean reversion, card count, TA
    - for low levels of dir, the static bias is pretty strong, and the ratio call:put is pretty high. actually it should be whatever dir the long MA is (long term trend)

#### Strategy top level
- for low vol, the dir is taken as the call:put ratio. but for higher vol, the ratio gets closer and closer to central.
- when dir conviction is high, size increases notably. Overall, vol is the scalar while dir is the ratio. but when dir is high, scale will be increased.
- if dir belief is high, but vol belief is low, maybe shold buy longer DTE options? for high vol belief, lower DTE. for high dir belief, maybe buy lower DTE in the belief dir and longer DTE in opposing.
- usually, the boy should just buy at open, sell next day close. in the middle time, it buys different options the "next day", and the third day sells those, so there is always overlap. 
- I think likely it will always plan to buy and sell options with at least 1DTE (not holding til expr day).
    - but a deviation case is maybe given a certain condition to hold one fully til expr, but keep buying the others
    - for example, usually, with a regular situation, and a good profit on one side, both positions would close and reset and do the next day. BUT if the new vol and dir is higher, maybe don't TP, hold and go for big profit. or instead of buying call:put ratio, do 1/2*(2call):put. what I mean by that is put the same amt into the call side as usual, but put more OTM to have higher leverage.
- a lighter deviation could be for outlying vol and dir, instead of buying new ones, always buying the same DTE, it can buy the same position (having shorter DTE) the next day if conviction in something is high
- TP can be a thing maybe. if we want the bot to run more frequently.
    - yk maybe I do want that. that wuold be a good benefit of having a bot that can always be checking the stock price n stuff




have a timeline diagram to show the standard procedure and deviations




### Implementation
I am running the code on a linux server setup for CI/CD on a cheap laptop I bought. I write the code on my personal computer, and the linux server runs on the budget laptop at home




### continuous integration and continuous deployment
So evidently there is a ton of stuff I can work on and add to the system. There will always be thing to research and add to the vol and dir calcs, and the strategy may change with its deviations. so it's really important that I make the code be able to be changed in terms of structure and stuff down the line.




### Sources that helped me
systematic trading - overall framework   
leverage space trading model helped in sizing   
trading in the zone - helped my discretionary trading that I incorporated into the system  
bayesian statistics the fun way - helped with analysis and idea testing  
option volatility and pricing - of course  
backtesting.py package. I took a lot of reference from this
