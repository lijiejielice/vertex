import os
import requests
from flask import Flask, request, jsonify, session, redirect, url_for
from vertexai.generative_models import Content, FunctionDeclaration, GenerativeModel, Part, Tool
import vertexai
import markdown

# Initialize Vertex AI
PROJECT_ID = "283176491096"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

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
model = GenerativeModel("gemini-1.0-pro", generation_config={"temperature": 0}, tools=[Tool(function_declarations=[get_current_bitcoin_price])])

app = Flask(__name__)
URL = "https://api.coindesk.com/v1/bpi/currentprice"
app.secret_key = 'joiahjbgalkdbfvihlrhnafnlkfqlh43252498dga!' 

@app.route("/")
def index():
    # Check if user is logged in
    if 'user' in session and session['user']:
        return app.send_static_file('index.html')
    else:
        # If not logged in, show the login page
        return redirect(url_for('login'))

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('user', None)
    return '', 200

@app.route('/login', methods=['GET', 'POST'])
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

@app.route("/predict")
def predict():
    if "user" not in session:
        return jsonify({"error": "Unauthenticated"}), 401
    
    if session["user"] not in user_chat_map:
        user_chat_map[session["user"]] = model.start_chat(response_validation=False)
    
    chat = user_chat_map[session["user"]]
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
    content = response.candidates[0].content.parts[0].text
    print(content)
    markdown_content = markdown.markdown(content)
    return jsonify({
            "message": markdown_content
        }) 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))