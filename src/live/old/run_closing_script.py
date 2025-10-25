'''set this up with cron to run every weekday near market close. it will handle holidays, but not early close.
I have set it up so that it will chdir into the /src/live folder, so goatsDB will store there, and significant_dates should be kept there
make sure your .env has GOATS_ROOT='\your_repo_root_directory' '''
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