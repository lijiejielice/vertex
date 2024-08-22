from vertexai.preview import extensions
import vertexai
import google
import os

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
credentials, _ = google.auth.default()
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

"""
Run this function once to create a new extension.

    Args:
        display_name: The display name of the extension.
        description: The description of the extension.
        manifest: The manifest of the extension.

    Returns:
        The created extension.

    Sample output logs:
    Extension created. Resource name: projects/283176491096/locations/us-central1/extensions/8135119408147202048
"""


def create_extension() -> extensions.Extension:
    extensions.Extension.create(
        display_name="Code Interpreter",
        description="This extension generates and executes code in the specified language",
        manifest={
            "name": "code_interpreter_tool",
            "description": "Google Code Interpreter Extension",
            "api_spec": {
                "open_api_gcs_uri": "gs://vertex-extension-public/code_interpreter.yaml"
            },
            "auth_config": {
                "google_service_account_config": {},
                "auth_type": "GOOGLE_SERVICE_ACCOUNT_AUTH",
            },
        },)


EXTENSION_ID = os.environ["EXTENSION_ID"]
vertexai.init(project=PROJECT_ID, location=LOCATION)
extension_code_interpreter = extensions.Extension(EXTENSION_ID)

print(extension_code_interpreter.execute(
    operation_id="generate_and_execute",
    operation_params={"query": "Tell me if abdofhkabdfb is a Palindrome"},
))
