import os
import json
# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide, TimeInForce
import logging
import time
import requests

MONITORED_STOCKS = ["SPY"]
ALERT_THRESHOLDS = {"SPY": 530}
STOCK_URL_FORMAT = "https://data.alpaca.markets/v2/stocks/trades/latest"

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    # Format of the log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log messages to the console
    ]
)




def maybe_notify(api_response):
    """Inspects the API response for stock data and provides detailed information."""

    if "trades" not in api_response:
        raise ValueError(
            "Unexpected API response format: 'trades' key not found")

    # Basic summary
    print("\n--- Stock Data Summary ---")
    print(f"Number of symbols: {len(api_response['trades'])}")

    for symbol, trade_data in api_response['trades'].items():
        print(f"\nSymbol: {symbol}")

        # Check for missing data
        if not trade_data:
            print("No trade data available.")
            continue

        # Essential details
        print(f"  Price: {trade_data['p']}")
        print(f"  Timestamp: {trade_data['t']}")

        # More in-depth analysis (optional)
        print("  Additional Details:")
        for key, value in trade_data.items():
            if key not in ["p", "t"]:  # Exclude already printed data
                print(f"    {key}: {value}")

    # Raw response for debugging (optional)
    print("\n--- Raw API Response ---")
    print(json.dumps(api_response, indent=2))

while True:
    # Headers for authentication
    headers = {
        'APCA-API-KEY-ID': os.environ["API_KEY_ID"],
        'APCA-API-SECRET-KEY': os.environ["API_KEY_SECRET"]
    }
    params = {"symbols": ",".join(MONITORED_STOCKS)}
    api_response = requests.get(
        STOCK_URL_FORMAT, headers=headers, params=params).json()
    maybe_notify(api_response)
    time.sleep(3)

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
