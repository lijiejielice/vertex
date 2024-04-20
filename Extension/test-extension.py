from vertexai.preview import extensions

import vertexai
from vertexai.preview import extensions

PROJECT_ID = "283176491096"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}

vertexai.init(project=PROJECT_ID,location=LOCATION)

def create_extension() -> extensions.Extension:
    """Creates a new extension.

    Args:
        display_name: The display name of the extension.
        description: The description of the extension.
        manifest: The manifest of the extension.

    Returns:
        The created extension.

    This is the output for the function:
    Creating Extension
    Create Extension backing LRO: projects/283176491096/locations/us-central1/extensions/8135119408147202048/operations/4031406696600436736
    Extension created. Resource name: projects/283176491096/locations/us-central1/extensions/8135119408147202048
    To use this Extension in another session:
    extension = vertexai.preview.extensions.Extension('projects/283176491096/locations/us-central1/extensions/8135119408147202048')
    <vertexai.extensions._extensions.Extension object at 0x7c4154431f10> 
    resource name: projects/283176491096/locations/us-central1/extensions/8135119408147202048
    """

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


EXTENSION_ID="8135119408147202048"
extension_code_interpreter = extensions.Extension(EXTENSION_ID)
print(extension_code_interpreter.execute(
    operation_id = "generate_and_execute",
    operation_params = {"query": "Tell me if abdofhkabdfb is a Palindrome"},
))