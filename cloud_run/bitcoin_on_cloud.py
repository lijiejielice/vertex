import os
import requests
from flask import Flask, request, jsonify, session, redirect, url_for
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
import vertexai
import markdown
import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    # Format of the log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log messages to the console
    ]
)

# Initialize Vertex AI
vertexai.init(project=os.environ["PROJECT_ID"],
              location=os.environ["LOCATION"])

# Initialize user, chat session map
user_chat_map = {}

# Declare the function and model
get_current_bitcoin_price = FunctionDeclaration(
    name="get_current_bitcoin_price",
    description="Get the latest current bitcoin price in specified currency or in all available currencies",
    parameters={
        "type": "object",
        "properties": {"currency": {"type": "string", "description": "Currency type"}},
    },
)
get_current_stock_price = FunctionDeclaration(
    name="get_latest_stock_price",
    description="Get the latest stock price with given stock symbol",
    parameters={
        "type": "object",
        "properties": {"stock_symbol": {"type": "string", "description": "Stock symbol"}},
    },
)
model = GenerativeModel("gemini-1.0-pro", generation_config={"temperature": 0}, tools=[
                        Tool(function_declarations=[get_current_bitcoin_price, get_current_stock_price])])

app = Flask(__name__)
# Used by session lib, to encrypt user cookie which is stored at client browser
app.secret_key = os.environ["APP_SECRET_KEY"]


BITCOIN_URL = "https://api.coindesk.com/v1/bpi/currentprice"
STOCK_URL_FORMAT = "https://data.alpaca.markets/v2/stocks/{stock_symbol}/trades/latest"


@ app.route("/")
def index():
    # Check if user is logged in
    if 'user' in session and session['user']:
        return app.send_static_file('index.html')
    else:
        # If not logged in, show the login page
        return redirect(url_for('login'))


@ app.route("/logout", methods=['POST'])
def logout():
    session.pop('user', None)
    return '', 200


@ app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Handle GET request
        return app.send_static_file('login.html')

    # Retrieve the access token from the request data
    access_token = request.json.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 400

    # Validate the access token with GitHub
    github_user_api_url = 'https://api.github.com/user'
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get(github_user_api_url, headers=headers)

    if response.status_code == 200:
        # Token is valid, create a session
        user_data = response.json()
        session['user'] = user_data['login']
        session['logged_in'] = True
        return jsonify({"message": "Login successful", "session": session['user']}), 200
    else:
        # Token is invalid
        return jsonify({"error": "Invalid GitHub token"}), 401


@ app.route("/predict")
def predict():
    if "user" not in session:
        return jsonify({"error": "Unauthenticated"}), 401

    if session["user"] not in user_chat_map:
        user_chat_map[session["user"]] = model.start_chat(
            response_validation=False)

    chat = user_chat_map[session["user"]]
    user_query = request.args.get('query')
    response = chat.send_message(user_query)
    logging.info(f"Response from Gemini to user query: {response}")

    function_call_response = None
    # Make registered funciton call if suggested by Gemini
    if response.candidates[0].content.parts[0].function_call:
        if response.candidates[0].content.parts[0].function_call.name == "get_latest_stock_price":
            function_call_response = get_latest_stock_price(chat,
                                                            response.candidates[0].content.parts[0].function_call.args)
        elif response.candidates[0].content.parts[0].function_call.name == "get_current_bitcoin_price":
            function_call_response = get_current_bitcoin_price(
                chat, response.candidates[0].content.parts[0].function_call.args)

    if function_call_response:
        response = function_call_response
        logging.info(f"Response from Gemini after function call: {response}")

    content = response.candidates[0].content.parts[0].text
    markdown_content = markdown.markdown(content)
    return jsonify({
        "message": markdown_content
    })


def get_current_bitcoin_price(chat, gemini_args):
    # URL requires .json suffix when there is no currenct specified
    currency = ".json"
    if "currency" in gemini_args:
        currency = f"/{gemini_args['currency']}"

    api_response = requests.get(BITCOIN_URL+currency).json()
    logging.info(f"API Response: {api_response}")
    response = chat.send_message(
        Part.from_function_response(
            name="get_current_bitcoin_price",
            response={
                "content": api_response,
            },
        ),
    )
    return response


def get_latest_stock_price(chat, gemini_args):
    url = STOCK_URL_FORMAT.format(stock_symbol=gemini_args["stock_symbol"])
    # Headers for authentication
    headers = {
        'APCA-API-KEY-ID': os.environ["APCA_API_KEY_ID"],
        'APCA-API-SECRET-KEY': os.environ["APCA_API_SECRET_KEY"]
    }
    api_response = requests.get(url, headers=headers).json()
    # TODO: error handling for invalid stock symbol
    logging.info(f"API Response: {api_response}")
    response = chat.send_message(
        Part.from_function_response(
            name="get_latest_stock_price",
            response={
                "content": api_response,
            },
        ),
    )
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
