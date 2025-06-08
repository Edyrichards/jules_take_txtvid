import requests
import os
import json # For loading response content
from PIL import Image # For creating a dummy image for the test
import cv2 # For creating dummy video
import wave # For creating dummy audio
import numpy as np # For image to OpenCV frame conversion

# Assuming the backend is running locally on port 8000
BASE_URL = "http://localhost:8000"

# These paths are relative to the project root (e.g., /app/text_to_multimedia_ai_pipeline).
TEST_IMAGES_DIR_RELATIVE_TO_PROJECT = "data/generated_images"
TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT = "data/generated_videos"
TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT, "lipsynced")
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
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT), # Base video dir
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT), # Lipsynced subdir
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
    assert video_path.startswith(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT) # Not TEST_LIPSYNCED_VIDEOS
    assert not video_path.startswith(TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT)
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

def test_sync_lips_placeholder():
    # 1. Create dummy input video
    dummy_video_name = "dummy_video_for_lipsync.mp4"
    # Path relative to project root (e.g., data/generated_videos/dummy_video_for_lipsync.mp4)
    dummy_video_path_relative = os.path.join(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT, dummy_video_name)
    # Absolute path for file creation by the test (e.g., /app/text_to_multimedia_ai_pipeline/data/generated_videos/dummy_video_for_lipsync.mp4)
    dummy_video_path_abs = os.path.join(PROJECT_ROOT_FOR_TESTS, dummy_video_path_relative)

    try:
        pil_frame = Image.new('RGB', (10, 10), color='green')
        cv_frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
        height, width, _ = cv_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(dummy_video_path_abs, fourcc, 1, (width, height))
        if not video_writer.isOpened(): # Check if VideoWriter was opened successfully
             assert False, f"Failed to open VideoWriter for path: {dummy_video_path_abs}"
        video_writer.write(cv_frame)
        video_writer.release()
    except Exception as e:
        assert False, f"Failed to create dummy video for test at {dummy_video_path_abs}: {e}"

    # 2. Create dummy input audio
    dummy_audio_name = "dummy_audio_for_lipsync.wav"
    dummy_audio_path_relative = os.path.join(TEST_SPEECH_DIR_RELATIVE_TO_PROJECT, dummy_audio_name)
    dummy_audio_path_abs = os.path.join(PROJECT_ROOT_FOR_TESTS, dummy_audio_path_relative)

    try:
        with wave.open(dummy_audio_path_abs, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(44100)
            wf.writeframes(b'\x00\x00' * 44100 * 1) # 1 second silence
    except Exception as e:
        if os.path.exists(dummy_video_path_abs): os.remove(dummy_video_path_abs) # Cleanup video
        assert False, f"Failed to create dummy audio for test at {dummy_audio_path_abs}: {e}"

    # 3. API Call
    payload = {
        "video_path": dummy_video_path_relative,
        "audio_path": dummy_audio_path_relative
    }
    response = requests.post(f"{BASE_URL}/sync-lips", json=payload)

    # 4. Assertions
    assert response.status_code == 200, f"API call failed: {response.text}"
    try:
        data = response.json()
    except json.JSONDecodeError:
         assert False, f"Failed to decode JSON response: {response.text}"

    assert data["message"] == "Lip sync applied successfully (placeholder)"
    assert "lipsynced_video_path" in data
    lipsynced_path = data["lipsynced_video_path"]
    assert lipsynced_path.startswith(TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT) # e.g. data/generated_videos/lipsynced/

    expected_synced_filename_part = os.path.splitext(dummy_video_name)[0] + "_lipsynced" + os.path.splitext(dummy_video_name)[1]
    assert expected_synced_filename_part in lipsynced_path, f"Expected '{expected_synced_filename_part}' in '{lipsynced_path}'"

    # 5. Cleanup
    if os.path.exists(dummy_video_path_abs):
        os.remove(dummy_video_path_abs)
    if os.path.exists(dummy_audio_path_abs):
        os.remove(dummy_audio_path_abs)
    # Note: The actual generated lipsynced video (a copy in this placeholder) is on the server side.
    # We don't attempt to clean it from here as part of this specific unit/integration test of the API contract.
    # Its existence could be checked if the test had access to the server's data folder directly after the call.
