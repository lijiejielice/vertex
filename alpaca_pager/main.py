import os
import json
# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide, TimeInForce
import logging
from time import sleep
from datetime import datetime, time
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv
from .notify_template import chat_payload, chat_warning
import yaml

POLL_INTERVAL = 3600  # in seconds

# Load environment variables from .env file
load_dotenv()

CHAT_WEBHOOK_URL = os.environ["CHAT_WEBHOOK_URL"]
LOG_FILE = "alpaca_pager.log"  # Name of the log file
STOCK_URL = "https://data.alpaca.markets/v2/stocks/trades/latest"

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    # Format of the log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log messages to a file
        logging.StreamHandler()  # Log messages to the console
    ]
)

def maybe_notify(api_response: dict, trading_config: requests.Response):
    """Inspects the API response for stock data and provides detailed information."""

    # TODO: send webhook notification that server crashes
    if "trades" not in api_response:
        raise ValueError(
            "Unexpected API response format: 'trades' key not found")

    notify_stocks = {}

    for symbol, trade_data in api_response['trades'].items():
        # Check for missing data
        if not trade_data:
            logging.warning("Missing trade data for stock: %s. Skipping.", symbol)
            continue
        
        lower_bound, upper_bound = trading_config["alert_thresholds"][symbol]["lower_bound"], trading_config["alert_thresholds"][symbol]["upper_bound"]
        if trade_data["p"] <= lower_bound or trade_data["p"] >= upper_bound:
            notify_stocks[symbol] = trade_data

    # Send notification to webhook
    # TODO: Add notify reason: belong/beyond threshold 
    logging.info("Notifying stocks: %s", notify_stocks)
    response = requests.post(CHAT_WEBHOOK_URL, json=chat_payload(notify_stocks))

def notify_error(api_response: dict):
    logging.warning("Failed to fetch stock data, got %s.", api_response)
    response = requests.post(CHAT_WEBHOOK_URL, json=chat_warning(api_response))

def is_nyse_open():
    # Get the current time in the NYC timezone 
    nyc_tz = ZoneInfo('America/New_York')
    now = datetime.now(nyc_tz)

    # Check if today is a weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
        return False

    # NYSE trading hours
    market_open = time(9, 30)
    market_close = time(16, 0)

    # Check if the current time is within market hours
    if market_open <= now.time() <= market_close:
        return True
    else:
        return False

def fetch_price_maybe_notify():
    # Fetch the raw content of the YAML file from the Gist URL
    trading_config = requests.get(os.environ["TRADING_CONFIG_URL"])
    if not trading_config.ok:
        notify_error(trading_config)
        return

    # Parse the YAML content
    trading_config = yaml.safe_load(trading_config.text)
    
    # Headers for authentication
    headers = {
        'APCA-API-KEY-ID': os.environ["API_KEY_ID"],
        'APCA-API-SECRET-KEY': os.environ["API_KEY_SECRET"]
    }
    params = {
        "symbols": ",".join(trading_config["monitored_stocks"])
    }
    api_response = requests.get(STOCK_URL, headers=headers, params=params)
    if api_response.ok:
        api_response = api_response.json()
        maybe_notify(api_response, trading_config)
    else:
        notify_error(api_response)
        
def main():
    while True:
        if is_nyse_open():
            fetch_price_maybe_notify()
        else:
            logging.info("NYSE is closed, skipping.")
        sleep(POLL_INTERVAL)

# trading_client = TradingClient(os.environ["API_KEY_ID"], os.environ["API_KEY_SECRET"], paper=True)
# # preparing market order
# market_order_data = MarketOrderRequest(
#                     symbol="SPY",
#                     qty=0.023,
#                     side=OrderSide.BUY,
#                     time_in_force=TimeInForce.DAY
#                     )

# # Market order
# market_order = trading_client.submit_order(
#                 order_data=market_order_data
#                )

# # preparing limit order
# limit_order_data = LimitOrderRequest(
#                     symbol="BTC/USD",
#                     limit_price=17000,
#                     notional=4000,
#                     side=OrderSide.SELL,
#                     time_in_force=TimeInForce.FOK
#                    )

# # Limit order
# limit_order = trading_client.submit_order(
#                 order_data=limit_order_data
#               )

