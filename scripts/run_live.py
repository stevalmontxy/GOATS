"""This script is like parallel to run_backtest, 
    here you choose strat, init broker, then pass it to the Live engine
    unlike the backtest, live will fetch the port from shelve
    so you pass in strat(alpaca_broker, None)
    it'll detect the None and get its port"""

# Standard Imports
import os
import sys
import dotenv
import traceback

# Third Party Imports
# none

# Prepare for Local Imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
os.chdir(current_dir) # for using shelve
sys.path.insert(1,root_dir) # for imports

# Local Imports
from goats.core.live import Live
from goats.core.strategy import Strategy, DemoStrat
from goats.broker.alpaca_broker import AlpacaBroker
 

# Load API keys
dotenv.load_dotenv()

trading_mode = os.getenv("TRADING_MODE")
paper = (trading_mode == "paper") # set boolean
if paper:
    api_key = os.getenv("ALPACA_API_KEY_PAPER")
    secret_key = os.getenv("ALPACA_SECRET_KEY_PAPER")
else:
    api_key = os.getenv("ALPACA_API_KEY_LIVE")
    secret_key = os.getenv("ALPACA_SECRET_KEY_LIVE")
gmail_user = os.getenv("GMAIL_USER")
gmail_pass = os.getenv("GMAIL_PASS")


if __name__ == "__main__":
    try:
        alpaca_broker = AlpacaBroker(api_key=api_key, secret_key=secret_key, paper=paper)
        strat = DemoStrat(alpaca_broker, None)

        live = Live(strat, gmail_user, gmail_pass)
        live.run()
    except Exception as error:
        full_traceback = traceback.format_exc()
        print("~~~~~~~~~~~~~~~Error ocurred!~~~~~~~~~~~~~~~\n", full_traceback)
        live.record_results('misc', error=str(full_traceback))
