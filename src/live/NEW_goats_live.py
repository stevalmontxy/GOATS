'''
This is a new live implementation. its made to run on a set interval'''
import all the objects

live = LiveTrader()

# define strat or this can be an import from a file full of strats
def customstrat(Strategy):
  pass

live.setstrat(customstrat)
live.updateportfoliofromscratch # also update time
live.getandformatpricedata

strat.run decisions
while (true)
  live.waitinterval
  live.updateportfolio
  strat.use_portfoliotocheckstuff
