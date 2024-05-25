## Release Notes
### Version 2.0
Added support for getting latest stock prices

#### Known Issues
- **Invalid Stock Symbol Handling**: Gemini does not handle error response from an endpoint as of 05/25/2024.

- **Message Sequence Enforcement**: Message sequence is not enforced. It's possible your second prompt is responded first.

- **API Dependency**: The application's performance and availability are highly dependent on the external API from Coindesk and GitHub's OAuth service.

### Version 1.0

#### Overview
This release introduces a new Flask web application designed to provide users with the latest Bitcoin prices upon request, leveraging Vertex AI's capabilities to handle user queries dynamically. The application also integrates GitHub for user authentication, enhancing security and personalization.

#### New Features

- **Vertex AI Integration**: Utilize the `gemini-1.0-pro` generative model to process and respond to user queries regarding Bitcoin prices.
- **Dynamic Bitcoin Price Retrieval**: Fetch the latest Bitcoin prices in real-time from the Coindesk API, allowing users to request prices in different currencies.
- **GitHub Authentication**: Users can log in using their GitHub accounts, ensuring that access is secure and personalized.
- **Markdown Rendering**: Responses regarding Bitcoin prices are now rendered in HTML via Markdown processing, improving the visual presentation of data within the application interface.

#### Enhancements

- **Session Management**: Improved session handling to ensure that user logins are maintained securely throughout their interaction with the application.
- **Security**: Application secret key has been set for Flask session management to increase the security of user data.

#### Fixes

- **Error Handling**: Enhanced error handling for login processes, including clear responses when an invalid GitHub token is provided or required parameters are missing.

#### Technical Details

- **Flask Routes**:
  - `/`: Main index that checks user login status.
  - `/login`: Handles user login requests both via GET (returning login page) and POST (processing GitHub access tokens).
  - `/logout`: Allows users to log out, clearing the session.
  - `/predict`: Processes user queries and returns Bitcoin prices as formatted Markdown content.

- **Dependencies**:
  - `Flask` for the web framework.
  - `requests` for HTTP requests to external APIs.
  - `vertexai` for integrating with Vertex AI models.
  - `markdown` for converting text to HTML.

#### Known Issues

- **Message Sequence Enforcement**: Message sequence is not enforced. It's possible your second prompt is responded first.

- **API Dependency**: The application's performance and availability are highly dependent on the external API from Coindesk and GitHub's OAuth service.

#### Deployment Notes

- Local: python bitcoin_on_cloud.py
- GCP Cloud Run: gcloud run deploy
