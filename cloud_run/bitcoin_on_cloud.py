import os
import requests
from flask import Flask, request, jsonify
from vertexai.generative_models import Content, FunctionDeclaration, GenerativeModel, Part, Tool
import vertexai

# Initialize Vertex AI
PROJECT_ID = "283176491096"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Declare the function and model
get_current_bitcoin_price = FunctionDeclaration(
    name="get_current_bitcoin_price",
    description="Get the latest current bitcoin price in specified currency or in all available currencies",
    parameters={
        "type": "object",
        "properties": {"currency": {"type": "string", "description": "Currency type"}},
    },
)
model = GenerativeModel("gemini-1.0-pro", generation_config={"temperature": 0}, tools=[Tool(function_declarations=[get_current_bitcoin_price])])
chat = model.start_chat()

app = Flask(__name__)
URL = "https://api.coindesk.com/v1/bpi/currentprice"

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/predict")
def predict():
    user_query = request.args.get('query')  # Get the user's query from URL parameters
    response = chat.send_message(user_query)  # Send the query to the Vertex AI model

    if response.candidates[0].content.parts[0].function_call:
        currency = ".json"
        if "currency" in response.candidates[0].content.parts[0].function_call.args:
            currency = f"/{response.candidates[0].content.parts[0].function_call.args['currency']}" 
        api_response = requests.get(URL+currency).json()
        response = chat.send_message(
            Part.from_function_response(
                name="get_current_bitcoin_price",
                response={
                    "content": api_response,
                },
            ),
        )
    print(user_query)
    print("Response from Vertex AI:")
    print(response.candidates[0].content.parts[0].text)
    return jsonify({
            "message": response.candidates[0].content.parts[0].text
        }) 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))