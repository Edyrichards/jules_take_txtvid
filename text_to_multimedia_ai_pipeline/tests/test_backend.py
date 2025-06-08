import requests
import os
import json # For loading response content
from PIL import Image # For creating a dummy image for the test
import cv2 # For creating dummy video
import wave # For creating dummy audio
import numpy as np # For image to OpenCV frame conversion
import shutil # Though not used directly by tests, good to have if we were to manage server-side test data

# Assuming the backend is running locally on port 8000
BASE_URL = "http://localhost:8000"

# These paths are relative to the project root (e.g., /app/text_to_multimedia_ai_pipeline).
TEST_IMAGES_DIR_RELATIVE_TO_PROJECT = "data/generated_images"
TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT = "data/generated_videos"
TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT, "lipsynced")
TEST_FINAL_VIDEOS_DIR_RELATIVE_TO_PROJECT = "data/final_videos" # New
TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT = "data/generated_audio"
TEST_SPEECH_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT, "speech")
TEST_MUSIC_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT, "music")
TEST_SFX_DIR_RELATIVE_TO_PROJECT = os.path.join(TEST_AUDIO_BASE_DIR_RELATIVE_TO_PROJECT, "sfx")

PROJECT_ROOT_FOR_TESTS = "text_to_multimedia_ai_pipeline" # Assumes tests run from /app

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    dirs_to_create = [
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_IMAGES_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_FINAL_VIDEOS_DIR_RELATIVE_TO_PROJECT), # New
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_SPEECH_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_MUSIC_DIR_RELATIVE_TO_PROJECT),
        os.path.join(PROJECT_ROOT_FOR_TESTS, TEST_SFX_DIR_RELATIVE_TO_PROJECT),
    ]
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
        # print(f"Ensured directory exists: {d}") # Keep setup quiet unless debugging

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_image_placeholder():
    payload = {"prompt": "A test prompt for placeholder image"}
    response = requests.post(f"{BASE_URL}/generate-image", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    try: data = response.json()
    except json.JSONDecodeError: assert False, f"Failed to decode JSON: {response.text}"
    assert data["message"] == "Image generated successfully (placeholder)"
    assert data["image_path"].startswith(TEST_IMAGES_DIR_RELATIVE_TO_PROJECT)
    assert data["image_path"].endswith(".png")
    assert data["resolution"] == "512x512"
    assert data["upscaling_status"] == "pending_integration"

def test_generate_video_placeholder():
    dummy_image_name = "test_input_for_video.png"
    dummy_image_path_relative = os.path.join(TEST_IMAGES_DIR_RELATIVE_TO_PROJECT, dummy_image_name)
    dummy_image_save_path = os.path.join(PROJECT_ROOT_FOR_TESTS, dummy_image_path_relative)
    try:
        Image.new('RGB', (60, 30), color='red').save(dummy_image_save_path)
    except Exception as e: assert False, f"Failed to create dummy image for test: {e}"

    payload = {"image_path": dummy_image_path_relative, "motion_type": "Test Motion"}
    response = requests.post(f"{BASE_URL}/generate-video", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    try: data = response.json()
    except json.JSONDecodeError: assert False, f"Failed to decode JSON: {response.text}"
    assert data["message"] == "Video generated successfully (placeholder)"
    assert data["video_path"].startswith(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT)
    assert not data["video_path"].startswith(TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT)
    assert data["video_path"].endswith(".mp4")
    assert data["base_resolution"] == "60x30"
    if os.path.exists(dummy_image_save_path): os.remove(dummy_image_save_path)

def test_generate_speech_placeholder():
    payload = {"text": "Hello", "voice": "TestV", "emotion": "TestE"}
    response = requests.post(f"{BASE_URL}/generate-speech", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()
    assert data["message"] == "Speech generated successfully (placeholder)"
    assert data["audio_path"].startswith(TEST_SPEECH_DIR_RELATIVE_TO_PROJECT)
    assert data["audio_path"].endswith(".wav")
    assert data["voice_used"] == payload["voice"]
    assert data["emotion_used"] == payload["emotion"]

def test_generate_music_placeholder():
    payload = {"style": "TestS", "duration_seconds": 7}
    response = requests.post(f"{BASE_URL}/generate-music", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()
    assert data["message"] == "Music generated successfully (placeholder)"
    assert data["audio_path"].startswith(TEST_MUSIC_DIR_RELATIVE_TO_PROJECT)
    assert data["audio_path"].endswith(".wav")
    assert data["style_used"] == payload["style"]
    assert data["duration_seconds"] == payload["duration_seconds"]

def test_generate_sfx_placeholder():
    payload = {"category": "TestC", "description": "TestD"}
    response = requests.post(f"{BASE_URL}/generate-sfx", json=payload)
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()
    assert data["message"] == "SFX generated successfully (placeholder)"
    assert data["audio_path"].startswith(TEST_SFX_DIR_RELATIVE_TO_PROJECT)
    assert data["audio_path"].endswith(".wav")
    assert data["category_used"] == payload["category"]
    assert data["description_logged"] == payload["description"]

def test_sync_lips_placeholder():
    dummy_video_name = "dummy_lipsync_in_video.mp4"
    dummy_video_rel_path = os.path.join(TEST_VIDEOS_DIR_RELATIVE_TO_PROJECT, dummy_video_name)
    dummy_video_abs_path = os.path.join(PROJECT_ROOT_FOR_TESTS, dummy_video_rel_path)
    try:
        frame = Image.new('RGB', (10,10),color='green'); arr = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        h,w,_=arr.shape; vw=cv2.VideoWriter(dummy_video_abs_path, cv2.VideoWriter_fourcc(*'mp4v'),1,(w,h))
        assert vw.isOpened(), "Failed to open VideoWriter for dummy video"
        vw.write(arr); vw.release()
    except Exception as e: assert False, f"Failed to create dummy video: {e}"

    dummy_audio_name = "dummy_lipsync_in_audio.wav"
    dummy_audio_rel_path = os.path.join(TEST_SPEECH_DIR_RELATIVE_TO_PROJECT, dummy_audio_name)
    dummy_audio_abs_path = os.path.join(PROJECT_ROOT_FOR_TESTS, dummy_audio_rel_path)
    try:
        with wave.open(dummy_audio_abs_path, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000); wf.writeframes(b'\0\0'*16000)
    except Exception as e:
        if os.path.exists(dummy_video_abs_path): os.remove(dummy_video_abs_path)
        assert False, f"Failed to create dummy audio: {e}"

    payload = {"video_path": dummy_video_rel_path, "audio_path": dummy_audio_rel_path}
    response = requests.post(f"{BASE_URL}/sync-lips", json=payload)
    assert response.status_code == 200, f"API call failed: {response.text}"
    try: data = response.json()
    except json.JSONDecodeError: assert False, f"Failed to decode JSON: {response.text}"
    assert data["message"] == "Lip sync applied successfully (placeholder)"
    assert data["lipsynced_video_path"].startswith(TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT)
    expected_fn_part = os.path.splitext(dummy_video_name)[0] + "_lipsynced.mp4"
    assert expected_fn_part in data["lipsynced_video_path"]

    if os.path.exists(dummy_video_abs_path): os.remove(dummy_video_abs_path)
    if os.path.exists(dummy_audio_abs_path): os.remove(dummy_audio_abs_path)

def test_assemble_video_placeholder():
    # 1. Setup Dummy Files
    base_video_name = "dummy_assembly_base.mp4"
    base_video_rel_path = os.path.join(TEST_LIPSYNCED_VIDEOS_DIR_RELATIVE_TO_PROJECT, base_video_name)
    base_video_abs_path = os.path.join(PROJECT_ROOT_FOR_TESTS, base_video_rel_path)
    try:
        frame = Image.new('RGB', (10, 10), color='cyan'); frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        h, w, _ = frame_cv.shape; fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        vw = cv2.VideoWriter(base_video_abs_path, fourcc, 1, (w,h))
        assert vw.isOpened(), "Failed to open VideoWriter for base video"
        vw.write(frame_cv); vw.release()
    except Exception as e: assert False, f"Failed to create dummy base video: {e}"

    speech_audio_name = "dummy_assembly_speech.wav"
    speech_audio_rel_path = os.path.join(TEST_SPEECH_DIR_RELATIVE_TO_PROJECT, speech_audio_name)
    speech_audio_abs_path = os.path.join(PROJECT_ROOT_FOR_TESTS, speech_audio_rel_path)
    try:
        with wave.open(speech_audio_abs_path, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000); wf.writeframes(b'\0\0' * 16000) # 1s
    except Exception as e: assert False, f"Failed to create dummy speech audio: {e}"

    music_audio_name = "dummy_assembly_music.wav"
    music_audio_rel_path = os.path.join(TEST_MUSIC_DIR_RELATIVE_TO_PROJECT, music_audio_name)
    music_audio_abs_path = os.path.join(PROJECT_ROOT_FOR_TESTS, music_audio_rel_path)
    try:
        with wave.open(music_audio_abs_path, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000); wf.writeframes(b'\0\0' * 16000 * 2) # 2s
    except Exception as e: assert False, f"Failed to create dummy music audio: {e}"

    sfx_audio_name = "dummy_assembly_sfx1.wav"
    sfx_audio_rel_path = os.path.join(TEST_SFX_DIR_RELATIVE_TO_PROJECT, sfx_audio_name)
    sfx_audio_abs_path = os.path.join(PROJECT_ROOT_FOR_TESTS, sfx_audio_rel_path)
    try:
        with wave.open(sfx_audio_abs_path, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000); wf.writeframes(b'\0\0' * int(16000 * 0.5)) # 0.5s
    except Exception as e: assert False, f"Failed to create dummy sfx audio: {e}"

    # 2. Payload
    export_settings = {"resolution": "1080p", "quality": "Best", "format": "MP4 (H.264)"} # Match frontend option
    payload = {
        "base_video_path": base_video_rel_path,
        "speech_audio_path": speech_audio_rel_path,
        "music_audio_path": music_audio_rel_path,
        "sfx_tracks": [{"sfx_path": sfx_audio_rel_path}],
        "export_settings": export_settings
    }

    # 3. API Call
    response = requests.post(f"{BASE_URL}/assemble-video", json=payload)

    # 4. Assertions
    assert response.status_code == 200, f"API call failed: {response.text}"
    try: data = response.json()
    except json.JSONDecodeError: assert False, f"Failed to decode JSON response: {response.text}"

    assert data["message"] == "Video assembled successfully (placeholder)"
    assert "final_video_path" in data
    final_path = data["final_video_path"]
    assert final_path.startswith(TEST_FINAL_VIDEOS_DIR_RELATIVE_TO_PROJECT) # e.g. data/final_videos/

    expected_final_filename_base = os.path.splitext(base_video_name)[0]
    # Backend logic: final_video_placeholder_dummy_assembly_base.mp4 (if format is MP4)
    assert f"final_video_placeholder_{expected_final_filename_base}" in final_path
    assert final_path.endswith(".mp4") # Based on "MP4 (H.264)" format in export_settings

    assert "settings_applied" in data
    assert data["settings_applied"] == export_settings

    # 5. Cleanup
    paths_to_remove = [
        base_video_abs_path, speech_audio_abs_path,
        music_audio_abs_path, sfx_audio_abs_path
    ]
    for p in paths_to_remove:
        if os.path.exists(p):
            os.remove(p)
