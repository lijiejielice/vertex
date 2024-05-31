import dateutil


def chat_payload(trades_data):
    notify_data = []
    for symbol, trade_data in trades_data.items():
        timestamp = trade_data['t']
        # Parse and format the timestamp
        formatted_timestamp = dateutil.parser.isoparse(timestamp).strftime("%Y-%m-%d %H:%M")

        notify_data.append({
            "Symbol": symbol,
            "Price": trade_data['p'],
            "Timestamp": formatted_timestamp
        })

    payload = {
        "cards": [
            {
                "sections": [
                    {
                        "widgets": [
                            {
                                "textParagraph": {
                                    "text": "\n".join(f"{key}: {value}" for key, value in data.items())
                                }
                            }
                        ]
                    }
                ],
                "header": {
                    "title": "Stock Alert",
                    "subtitle": "Current Prices"
                }
            }
            for data in notify_data
        ]
    }
    return payload