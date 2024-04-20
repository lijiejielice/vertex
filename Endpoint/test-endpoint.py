import base64
from PIL import Image
from io import BytesIO
import google.auth
from google.cloud import aiplatform 

# Configuration
project = "283176491096"
endpoint_id = "6236212249443172352"
location = "us-central1"

# Authentication (if necessary)
#credentials, project_id = google.auth.default() 

# Initialize Vertex AI client
aiplatform.init(project=project, location=location)
endpoint = aiplatform.Endpoint(f"projects/{project}/locations/{location}/endpoints/{endpoint_id}")

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

# Example usage  
if __name__ == "__main__":    
    instances = [
        {"prompt": "female google employee who is a software engineer working on GCP product"},
    ]

    # Send prediction request to the endpoint
    response = endpoint.predict(instances=instances)

   # images = [base64_to_image(image) for image in response.predictions]
   # image_grid(images).show()
    for i, image_str in enumerate(response.predictions):
        image = base64_to_image(image_str)
        image_filename = f"2nd_generated_image_{i+1}.jpg"  # Or ".png" if appropriate
        image.save(image_filename) 