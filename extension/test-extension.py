from vertexai.preview import extensions

import vertexai
from vertexai.preview import extensions

PROJECT_ID = "283176491096"
LOCATION = "us-central1"

""" Run this function once to create a new extension. 

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
    extension_code_interpreter = extensions.Extension.create(
    display_name = "Code Interpreter",
    description = "This extension generates and executes code in the specified language",
    manifest = {
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

EXTENSION_ID="8135119408147202048" # See README
vertexai.init(project=PROJECT_ID,location=LOCATION)
extension_code_interpreter = extensions.Extension(EXTENSION_ID)

print(extension_code_interpreter.execute(
    operation_id = "generate_and_execute",
    operation_params = {"query": "Tell me if abdofhkabdfb is a Palindrome"},
))