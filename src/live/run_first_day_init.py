import sys
sys.path.insert(1,'/home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/')
# import goats
# print(goats)
# print("sys path::", sys.path)
# print('sys modules', sys.modules)
import requests

from goats.classes import Position, Option, Portfolio, Strategy
from goats.sentiment_v1 import calcSentiment, sentiment2order
from goats.live_funcs import createUnderlydf, orderMakerLive, updatePortfolio, firstDayInit, closePosition

from goats.mysecrets import ALPACA_API_KEY_PAPER, ALPACA_SECRET_KEY_PAPER
from goats.mysecrets import GMAIL_USER, GMAIL_PASS

print(sys.path)

if __name__ == "__main__":
    try:
        print('boutta run')
        firstDayInit()
        # updatePortfolio()
        print('succesfully ran')
    except requests.exceptions.ConnectionError:
        print("connection refused")
        sleep(5)
        firstDayInit()
else:
    print('name not main')
# python /home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/core/livefuncs/run_first_day_init.py