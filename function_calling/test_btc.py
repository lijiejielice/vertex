# Initialize Vertex AI
import vertexai
import requests
import google.auth
import os
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
credentials, _ = google.auth.default()
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

get_current_bitcoin_price = FunctionDeclaration(
    name="get_current_bitcoin_price",
    description="Get the latest current bitcoin price in specified currency",
    parameters={
        "type": "object",
        "properties": {"currency": {"type": "string", "description": "Currency type"}},
    },
)
model = GenerativeModel("gemini-1.0-pro", generation_config={
                        "temperature": 0}, tools=[Tool(function_declarations=[get_current_bitcoin_price])])
URL = "https://api.coindesk.com/v1/bpi/currentprice"
bitcoin_tool = Tool(
    function_declarations=[get_current_bitcoin_price],
)
chat = model.start_chat()
# Get the prompt input from the user
while True:
    prompt = input("Enter your question: ")
    response = chat.send_message(prompt)
    if response.candidates[0].content.parts[0].function_call:
        currency = ".json"
        if "currency" in response.candidates[0].content.parts[0].function_call.args:
            currency = f"/{response.candidates[0].content.parts[0].function_call.args['currency']}"
        api_response = requests.get(URL + currency).json()
        response = chat.send_message(
            Part.from_function_response(
                name="get_current_bitcoin_price",
                response={
                    "content": api_response,
                },
            ),
        )

    print(response.candidates[0].content.parts[0].text)
