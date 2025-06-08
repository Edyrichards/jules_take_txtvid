import requests
import os
import json # For loading response content

# Assuming the backend is running locally on port 8000
BASE_URL = "http://localhost:8000"
# This path is relative to the project root, where the backend saves images.
# The test will check if the backend *reports* a path within this directory structure.
GENERATED_IMAGES_DIR_RELATIVE = "data/generated_images"

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_image_placeholder():
    # This test assumes the backend server is running and will create
    # the GENERATED_IMAGES_DIR (server-side) if it doesn't exist,
    # as per the os.makedirs call in backend/main.py.

    payload = {"prompt": "A test prompt for placeholder image"}
    response = requests.post(f"{BASE_URL}/generate-image", json=payload)

    assert response.status_code == 200, f"Request failed: {response.text}"

    try:
        data = response.json()
    except json.JSONDecodeError:
        assert False, f"Failed to decode JSON response: {response.text}"

    assert "message" in data
    assert data["message"] == "Image generated successfully (placeholder)"

    assert "image_path" in data
    image_path_from_response = data["image_path"] # This is the client-accessible path

    expected_image_filename = "placeholder_image.png"
    assert image_path_from_response.endswith(expected_image_filename), \
        f"Reported image_path '{image_path_from_response}' does not end with '{expected_image_filename}'"

    # Check if the path starts with the expected directory structure
    # e.g., "data/generated_images/placeholder_image.png"
    assert image_path_from_response.startswith(GENERATED_IMAGES_DIR_RELATIVE), \
        f"Reported image_path '{image_path_from_response}' does not start with '{GENERATED_IMAGES_DIR_RELATIVE}'"

    # Note: We are not testing os.path.exists(full_image_path_on_client_or_test_runner)
    # because the file path 'image_path_from_response' is relative to the *project root*
    # where the *server* operates. The test runner might be anywhere.
    # The backend's responsibility is to create the file on its file system and report a correct relative path.
    # Actual file existence would be checked by an integration test that can access the server's file system
    # or by the frontend when it tries to display the image.

    assert "resolution" in data
    assert data["resolution"] == "512x512"

    assert "upscaling_status" in data
    assert data["upscaling_status"] == "pending_integration"

# Example of how you might run this if it were a script (for illustration):
# if __name__ == "__main__":
#     # This is not how pytest tests are typically run, but useful for direct execution.
#     print("Running backend tests...")
#     # Ensure GENERATED_IMAGES_DIR exists from the perspective of where this script might run
#     # if it were to try and access files directly (which these tests currently don't).
#     # For these tests, only the running backend needs to access its paths.
#     test_health_check()
#     print("test_health_check PASSED")
#     test_generate_image_placeholder()
#     print("test_generate_image_placeholder PASSED")
#     print("Basic backend tests passed.")
