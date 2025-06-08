import requests
import os
import json # For loading response content
from PIL import Image # For creating a dummy image for the test

# Assuming the backend is running locally on port 8000
BASE_URL = "http://localhost:8000"

# These paths are relative to the project root (e.g., /app/text_to_multimedia_ai_pipeline).
TEST_IMAGES_DIR_RELATIVE_TO_PROJECT = "data/generated_images"
TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT = "data/generated_videos"
TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT = "data/generated_audio"
TEST_SPEECH_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT, "speech")
TEST_MUSIC_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT, "music")
TEST_SFX_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT, "sfx")

PROJECT_ROOT_FOR_TESTS = "text_to_multimedia_ai_pipeline" # Assumes tests run from /app

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    # Ensure test directories exist before any tests run.
    # These paths are constructed from the perspective of being in /app

    dirs_to_create = [
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_IMAGES_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_SPEECH_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_MUSIC_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_SFX_DIR_RELATIVE_TO_PROJECT),
    ]

    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
        print(f"Ensured directory exists: {d}")

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
    assert image_path_from_response.startswith(TEST_IMAGES_DIR_RELATIVE_TO_PROJECT)
    assert "resolution" in data
    assert data["resolution"] == "512x512"
    assert "upscaling_status" in data
    assert data["upscaling_status"] == "pending_integration"

def test_generate_video_placeholder():
    dummy_image_name = "test_input_for_video.png"
    dummy_image_path_relative_to_project = os.path.join(TEST_IMAGES_DIR_RELATIVE_TO_PROJECT, dummy_image_name)
    dummy_image_save_path = os.path.join(PROJECT_ROOT_FOR_TESTS, dummy_image_path_relative_to_project)
    try:
        img = Image.new('RGB', (60, 30), color = 'red')
        img.save(dummy_image_save_path)
    except Exception as e:
        assert False, f"Failed to create dummy image for test at {dummy_image_save_path}: {e}"

    payload = {"image_path": dummy_image_path_relative_to_project, "motion_type": "Test Motion"}
    response = requests.post(f"{BASE_URL}/generate-video", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    try:
        data = response.json()
    except json.JSONDecodeError:
        assert False, f"Failed to decode JSON response: {response.text}"

    assert data["message"] == "Video generated successfully (placeholder)"
    assert "video_path" in data
    video_path = data["video_path"]
    assert video_path.startswith(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT)
    assert video_path.endswith(".mp4")
    assert data["base_resolution"] == "60x30"
    assert data["fps"] == 1
    assert data["duration_seconds"] == 1
    assert data["frame_interpolation_status"] == "pending_integration"
    assert data["video_upscaling_status"] == "pending_integration"
    try:
        if os.path.exists(dummy_image_save_path):
            os.remove(dummy_image_save_path)
    except OSError as e:
        print(f"Warning: Error removing test dummy image '{dummy_image_save_path}': {e}")

def test_generate_speech_placeholder():
    payload = {"text": "Hello world testing speech", "voice": "Test Voice", "emotion": "Test Emotion"}
    response = requests.post(f"{BASE_URL}/generate-speech", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()
    assert data["message"] == "Speech generated successfully (placeholder)"
    assert "audio_path" in data
    assert data["audio_path"].startswith(TEST_SPEECH_DIR_RELATIVE_TO_PROJECT)
    assert data["audio_path"].endswith(".wav")
    assert data["voice_used"] == payload["voice"]
    assert data["emotion_used"] == payload["emotion"]

def test_generate_music_placeholder():
    payload = {"style": "Test Style", "duration_seconds": 7}
    response = requests.post(f"{BASE_URL}/generate-music", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()
    assert data["message"] == "Music generated successfully (placeholder)"
    assert "audio_path" in data
    assert data["audio_path"].startswith(TEST_MUSIC_DIR_RELATIVE_TO_PROJECT)
    assert data["audio_path"].endswith(".wav")
    assert data["style_used"] == payload["style"]
    assert data["duration_seconds"] == payload["duration_seconds"]

def test_generate_sfx_placeholder():
    payload = {"category": "Test Category", "description": "A specific test sound"}
    response = requests.post(f"{BASE_URL}/generate-sfx", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()
    assert data["message"] == "SFX generated successfully (placeholder)"
    assert "audio_path" in data
    assert data["audio_path"].startswith(TEST_SFX_DIR_RELATIVE_TO_PROJECT)
    assert data["audio_path"].endswith(".wav")
    assert data["category_used"] == payload["category"]
    assert data["description_logged"] == payload["description"]
