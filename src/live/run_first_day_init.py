'''run this script manually'''
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # load GOATS_ROOT directory variable
project_root = Path(os.getenv('GOATS_ROOT'))
if project_root is None:
    raise ValueError("GOATS_ROOT environment variable not set")

src_path = project_root / "src"
live_path = src_path / "live"

sys.path.insert(1, str(src_path))
os.chdir(str(live_path))

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