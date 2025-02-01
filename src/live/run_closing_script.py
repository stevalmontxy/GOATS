'''set this up with cron to run every weekday near market close. it will handle holidays, but not early close.'''
import sys
sys.path.insert(1,'/home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/')
import os
os.chdir('/home/stevalmontxy/Documents/GitHub/Options-Backtesting-Python/src/live')

import goats
from goats.live_funcs import closingScript, recordResults
import requests

if __name__ == "__main__":
    try:
        print('boutta run')
        closingScript()
        print('succesfully ran')
    except Exception as error:
        print(error)
        recordResults('failed to run', func = 'closingScript', error=str(error))
else:
    print('name not main')