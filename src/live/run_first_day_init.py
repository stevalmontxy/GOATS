'''run this script manually'''
import sys
sys.path.insert(1,'/home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/')
import os
os.chdir('/home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/live')

import goats
from goats.live_funcs import firstDayInit, recordResults
import requests

if __name__ == "__main__":
    try:
        print('boutta run')
        firstDayInit()
        print('succesfully ran')
    # except requests.exceptions.ConnectionError:
        # print("connection refused")
    except Exception as error:
        print(error)
        recordResults('failed to run', func = 'firstDayInit', error=str(error))
else:
    print('name not main')
# python /home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/core/livefuncs/run_first_day_init.py