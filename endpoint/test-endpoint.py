import base64
import google
import os
from PIL import Image
from io import BytesIO
from google.cloud import aiplatform

# Configuration
PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
credentials, _ = google.auth.default()

# Manually created in Pantheon
ENDPOINT_ID = os.environ["ENDPOINT_ID"]

# Initialize Vertex AI client
aiplatform.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
endpoint = aiplatform.Endpoint(f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}")


# Core image processing functions (same as before)
# **Core image processing functions**
def base64_to_image(image_str):
    image = Image.open(BytesIO(base64.b64decode(image_str)))
    return image


def image_grid(imgs, rows=2, cols=2):
    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


if __name__ == "__main__":
    instances = [
        {"prompt": "female google employee who is a software engineer working on GCP product"},
    ]

    # Send prediction request to the endpoint
    response = endpoint.predict(instances=instances)


for i, image_str in enumerate(response.predictions):
    image = base64_to_image(image_str)
    image_filename = f"generated/generated_image_{i+1}.jpg"  # Check file path
    image.save(image_filename)
