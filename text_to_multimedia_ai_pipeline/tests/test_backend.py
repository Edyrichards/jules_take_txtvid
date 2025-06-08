import requests
import os
import json # For loading response content
from PIL import Image # For creating a dummy image for the test

# Assuming the backend is running locally on port 8000
BASE_URL = "http://localhost:8000"

# These paths are relative to the project root (e.g., /app/text_to_multimedia_ai_pipeline).
# The test script, when run by pytest, typically has its CWD as the project root.
# So, os.path.join(TEST_IMAGES_DIR_RELATIVE_TO_PROJECT, filename) works for file creation by the test.
# The backend receives these project-relative paths and resolves them against PROJECT_ROOT_DIR.
TEST_IMAGES_DIR_RELATIVE_TO_PROJECT = "data/generated_images"
TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT = "data/generated_videos"


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    # Ensure test directories exist before any tests run.
    # These paths are relative to the project root where pytest is usually run.
    # For the sandbox, this means /app/text_to_multimedia_ai_pipeline/data/generated_images
    project_base_dir = "text_to_multimedia_ai_pipeline" # This assumes tests run from /app

    # Construct paths relative to where the test script itself is (tests/test_backend.py)
    # or more robustly, make them absolute assuming CWD is project root.
    # For the sandbox, CWD is /app.
    # So, we need to create /app/text_to_multimedia_ai_pipeline/data/generated_images

    # Path from /app perspective
    images_dir_abs = os.path.join(project_base_dir, TEST_IMAGES_DIR_RELATIVE_TO_PROJECT)
    videos_dir_abs = os.path.join(project_base_dir, TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT)

    os.makedirs(images_dir_abs, exist_ok=True)
    os.makedirs(videos_dir_abs, exist_ok=True)
    print(f"Ensured directories exist: {images_dir_abs}, {videos_dir_abs}")


def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_image_placeholder():
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
    image_path_from_response = data["image_path"]

    expected_image_filename = "placeholder_image.png"
    assert image_path_from_response.endswith(expected_image_filename)
    # Backend returns path relative to project root: data/generated_images/...
    assert image_path_from_response.startswith(TEST_IMAGES_DIR_RELATIVE_TO_PROJECT)

    assert "resolution" in data
    assert data["resolution"] == "512x512"

    assert "upscaling_status" in data
    assert data["upscaling_status"] == "pending_integration"


def test_generate_video_placeholder():
    # 1. Create a dummy input image for the video generation endpoint
    dummy_image_name = "test_input_for_video.png"
    # This path is relative to the project root, as it will be sent to the backend.
    dummy_image_path_relative_to_project = os.path.join(TEST_IMAGES_DIR_RELATIVE_TO_PROJECT, dummy_image_name)

    # The actual file needs to be saved where the test runner can write it.
    # If CWD for test runner is /app, then this path is /app/text_to_multimedia_ai_pipeline/data/generated_images/test_input_for_video.png
    dummy_image_save_path = os.path.join("text_to_multimedia_ai_pipeline", dummy_image_path_relative_to_project)

    try:
        img = Image.new('RGB', (60, 30), color = 'red')
        img.save(dummy_image_save_path)
        print(f"Dummy image for video test saved to: {os.path.abspath(dummy_image_save_path)}")
    except Exception as e:
        assert False, f"Failed to create dummy image for test at {dummy_image_save_path}: {e}"

    payload = {
        "image_path": dummy_image_path_relative_to_project,
        "motion_type": "Test Motion"
    }
    response = requests.post(f"{BASE_URL}/generate-video", json=payload)

    assert response.status_code == 200, f"Request failed: {response.text}"
    try:
        data = response.json()
    except json.JSONDecodeError:
        assert False, f"Failed to decode JSON response: {response.text}"

    assert "message" in data
    assert data["message"] == "Video generated successfully (placeholder)"

    assert "video_path" in data
    video_path = data["video_path"]
    assert video_path.startswith(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT)
    assert video_path.endswith(".mp4") # Default placeholder is mp4

    assert "base_resolution" in data
    assert data["base_resolution"] == "60x30" # Based on the dummy image created
    assert "fps" in data
    assert data["fps"] == 1
    assert "duration_seconds" in data
    assert data["duration_seconds"] == 1

    assert "frame_interpolation_status" in data
    assert data["frame_interpolation_status"] == "pending_integration"
    assert "video_upscaling_status" in data
    assert data["video_upscaling_status"] == "pending_integration"

    # Clean up the dummy image
    try:
        if os.path.exists(dummy_image_save_path):
            os.remove(dummy_image_save_path)
            print(f"Dummy image for video test removed from: {os.path.abspath(dummy_image_save_path)}")
    except OSError as e:
        # Non-fatal for test outcome, but good to know if cleanup fails.
        print(f"Warning: Error removing test dummy image '{dummy_image_save_path}': {e}")


# if __name__ == "__main__":
#     # Illustrative direct run, not for pytest
#     print("Running backend tests directly...")
#     project_base_dir_for_direct_run = "text_to_multimedia_ai_pipeline"
#     os.makedirs(os.path.join(project_base_dir_for_direct_run, TEST_IMAGES_DIR_RELATIVE_TO_PROJECT), exist_ok=True)
#     os.makedirs(os.path.join(project_base_dir_for_direct_run, TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT), exist_ok=True)
#     print(f"Setup module specific actions (mkdirs) done for direct run.")

#     test_health_check()
#     print("test_health_check PASSED")
#     test_generate_image_placeholder()
#     print("test_generate_image_placeholder PASSED")
#     test_generate_video_placeholder()
#     print("test_generate_video_placeholder PASSED")
#     print("Basic backend tests passed.")
