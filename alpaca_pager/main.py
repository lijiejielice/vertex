import os
import json
# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide, TimeInForce
import logging
import time
import requests
from dotenv import load_dotenv
from .notify_template import chat_payload


# Load environment variables from .env file
load_dotenv()


MONITORED_STOCKS = ["SPY"]
ALERT_THRESHOLDS = {"SPY": [520, 530]}
STOCK_URL = "https://data.alpaca.markets/v2/stocks/trades/latest"
POLL_INTERVAL = 3  # in seconds
CHAT_WEBHOOK_URL = os.environ["CHAT_WEBHOOK_URL"]
LOG_FILE = "alpaca_pager.log"  # Name of the log file


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

def maybe_notify(api_response: dict):
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
        
        lower_band, upper_band = ALERT_THRESHOLDS[symbol]
        if trade_data["p"] <= lower_band or trade_data["p"] >= upper_band:
            notify_stocks[symbol] = trade_data

    # Send notification to webhook
    # TODO: Add notify reason: belong/beyond threshold 
    logging.info("Notifying stocks: %s", notify_stocks)
    response = requests.post(CHAT_WEBHOOK_URL, json=chat_payload(notify_stocks))


def main():
    while True:
        # Headers for authentication
        headers = {
            'APCA-API-KEY-ID': os.environ["API_KEY_ID"],
            'APCA-API-SECRET-KEY': os.environ["API_KEY_SECRET"]
        }
        params = {
            "symbols": ",".join(MONITORED_STOCKS)
        }
        api_response = requests.get(
            STOCK_URL, headers=headers, params=params).json()
        maybe_notify(api_response)
        time.sleep(POLL_INTERVAL)

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

