import dateutil
from requests import Response

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


def chat_warning(api_response: Response):
    notify_data = []
    notify_data.append({
        "Error Message": api_response.text,
        "Error Code": api_response.status_code,
    })

    payload = {
        "cards": [
            {
                "header": {
                    "title": "Application Error Alert",
                    "subtitle": "Detailed Error Information"
                },
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
                ]
            }
            for data in notify_data
        ]
    }
    
    return payload

