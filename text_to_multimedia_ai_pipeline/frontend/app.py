import streamlit as st
import requests
import os # For joining paths
# import traceback # For debugging potential errors if running locally

st.title("Text-to-Multimedia AI Pipeline")

# --- Initialize Session State ---
if 'generated_image_path' not in st.session_state:
    st.session_state.generated_image_path = None
if 'generated_video_path' not in st.session_state:
    st.session_state.generated_video_path = None
if 'generated_speech_path' not in st.session_state:
    st.session_state.generated_speech_path = None
if 'generated_music_path' not in st.session_state:
    st.session_state.generated_music_path = None
if 'generated_sfx_path' not in st.session_state:
    st.session_state.generated_sfx_path = None
if 'lipsynced_video_path' not in st.session_state:
    st.session_state.lipsynced_video_path = None
if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None


# --- Backend Status (existing code) ---
st.header("Backend Status")
backend_url_health = "http://localhost:8000/health"
try:
    response_health = requests.get(backend_url_health)
    if response_health.status_code == 200:
        status = response_health.json().get("status", "unknown")
        st.success(f"Backend is {status}!")
    else:
        st.error(f"Backend (health check) returned status code: {response_health.status_code}")
except requests.exceptions.ConnectionError:
    st.error("Failed to connect to the backend for health check. Ensure it's running.")
except Exception as e:
    st.error(f"An error occurred during health check: {e}")

PROJECT_BASE_PATH_FOR_FILES = "text_to_multimedia_ai_pipeline"

def reset_all_downstream_from_image():
    st.session_state.generated_video_path = None
    st.session_state.generated_speech_path = None
    st.session_state.generated_music_path = None
    st.session_state.generated_sfx_path = None
    st.session_state.lipsynced_video_path = None
    st.session_state.final_video_path = None

def reset_all_downstream_from_video():
    st.session_state.generated_speech_path = None # Speech is independent of video for generation, but lipsync depends on both
    st.session_state.generated_music_path = None
    st.session_state.generated_sfx_path = None
    st.session_state.lipsynced_video_path = None
    st.session_state.final_video_path = None

def reset_all_downstream_from_speech():
    # Music and SFX are independent of speech
    # Lipsync and Final Video depend on speech
    st.session_state.lipsynced_video_path = None
    st.session_state.final_video_path = None

def reset_final_video_if_audio_changes():
    # If music or sfx changes, only the final video needs reset, not lipsync
    st.session_state.final_video_path = None


# --- Image Generation Section ---
st.header("Generate Image")
style_options_img = ["None", "Photographic", "Illustration", "Animation", "Cinematic", "Sketch"]
selected_style_img = st.selectbox("Select style:", style_options_img, key="style_selectbox_img")
prompt_text_input_img = st.text_area("Enter your image prompt:", height=100, key="prompt_text_area_img")
backend_url_generate_image = "http://localhost:8000/generate-image"
if st.button("Generate Image"):
    if prompt_text_input_img:
        final_prompt_img = prompt_text_input_img
        if selected_style_img != "None":
            final_prompt_img = f"{selected_style_img} style: {prompt_text_input_img}"
        with st.spinner("Generating image..."):
            try:
                payload = {"prompt": final_prompt_img}
                response_generate = requests.post(backend_url_generate_image, json=payload)
                if response_generate.status_code == 200:
                    data = response_generate.json()
                    image_path_relative_to_project = data.get("image_path")
                    if image_path_relative_to_project:
                        path_for_os_exists = os.path.join(PROJECT_BASE_PATH_FOR_FILES, image_path_relative_to_project)
                        if os.path.exists(path_for_os_exists):
                            st.image(path_for_os_exists, caption=f"Generated image for: {final_prompt_img[:70]}...")
                            st.success(data.get("message", "Image generated!"))
                            st.session_state.generated_image_path = image_path_relative_to_project
                            reset_all_downstream_from_image()
                        else:
                            st.error(f"Image file not found by frontend at path: {path_for_os_exists}")
                    else:
                        st.error("Backend did not return an image path.")
                else:
                    st.error(f"Failed to generate image. Backend responded: {response_generate.status_code} - {response_generate.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to image generation backend at {backend_url_generate_image}.")
            except Exception as e:
                st.error(f"Unexpected error during image generation: {e}")
    else:
        st.warning("Please enter a prompt.")

# --- Video Generation Section ---
st.header("Generate Video")
if st.session_state.generated_image_path:
    st.write(f"Using image: `{st.session_state.generated_image_path}` for video generation.")
    motion_presets_video = ["None", "Slow Pan Right", "Slow Pan Left", "Slow Zoom In", "Slow Zoom Out", "Tilt Up", "Tilt Down", "Dolly Zoom", "Gentle Rotation Clockwise", "Gentle Rotation Counter-Clockwise", "Subtle Object Sway", "Lighting Flicker"]
    selected_motion_video = st.selectbox("Select motion type:", motion_presets_video, key="motion_type_selectbox_video")
    if st.button("Generate Video"):
        backend_url_generate_video = "http://localhost:8000/generate-video"
        with st.spinner("Generating video..."):
            try:
                payload = {"image_path": st.session_state.generated_image_path, "motion_type": selected_motion_video}
                response_generate_video = requests.post(backend_url_generate_video, json=payload)
                if response_generate_video.status_code == 200:
                    video_data = response_generate_video.json()
                    video_path_relative_to_project = video_data.get("video_path")
                    if video_path_relative_to_project:
                        path_for_os_exists_video = os.path.join(PROJECT_BASE_PATH_FOR_FILES, video_path_relative_to_project)
                        if os.path.exists(path_for_os_exists_video):
                            st.session_state.generated_video_path = video_path_relative_to_project
                            reset_all_downstream_from_video()
                            st.video(path_for_os_exists_video)
                            st.success(video_data.get("message", "Video generated!"))
                        else:
                            st.error(f"Video file not found by frontend at path: {path_for_os_exists_video}")
                    else:
                        st.error("Backend did not return a video path.")
                else:
                    st.error(f"Failed to generate video. Backend responded: {response_generate_video.status_code} - {response_generate_video.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to video generation backend at {backend_url_generate_video}.")
            except Exception as e:
                st.error(f"Unexpected error during video generation: {e}")
else:
    st.info("Generate an image first to enable video generation.")

# --- Text-to-Speech Section ---
st.header("Text-to-Speech")
tts_text_input = st.text_area("Text to Synthesize:", height=100, key="tts_text_area")
tts_voice_options = ["Male Young Professional", "Female Young Friendly", "Male Mature Narrator", "Female Mature Professional", "Male Elderly Wise", "Female Warm Narrator"]
tts_selected_voice = st.selectbox("Select Voice:", tts_voice_options, key="tts_voice_selectbox")
tts_emotion_options = ["Neutral", "Happy", "Calm", "Dramatic"]
tts_selected_emotion = st.selectbox("Select Emotion:", tts_emotion_options, key="tts_emotion_selectbox")
backend_url_generate_speech = "http://localhost:8000/generate-speech"
if st.button("Generate Speech"):
    if tts_text_input:
        with st.spinner("Generating speech..."):
            try:
                payload = {"text": tts_text_input, "voice": tts_selected_voice, "emotion": tts_selected_emotion}
                response_generate_speech = requests.post(backend_url_generate_speech, json=payload)
                if response_generate_speech.status_code == 200:
                    speech_data = response_generate_speech.json()
                    speech_path_relative_to_project = speech_data.get("audio_path")
                    if speech_path_relative_to_project:
                        path_for_os_exists_speech = os.path.join(PROJECT_BASE_PATH_FOR_FILES, speech_path_relative_to_project)
                        if os.path.exists(path_for_os_exists_speech):
                            st.session_state.generated_speech_path = speech_path_relative_to_project
                            reset_all_downstream_from_speech()
                            st.audio(path_for_os_exists_speech, format='audio/wav')
                            st.success(speech_data.get("message", "Speech generated!"))
                            st.caption(f"Voice: {speech_data.get('voice_used', 'N/A')}, Emotion: {speech_data.get('emotion_used', 'N/A')}")
                        else:
                            st.error(f"Speech audio file not found by frontend at: {path_for_os_exists_speech}")
                    else:
                        st.error("Backend did not return a speech audio path.")
                else:
                    st.error(f"Failed to generate speech. Backend responded: {response_generate_speech.status_code} - {response_generate_speech.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to speech generation backend at {backend_url_generate_speech}.")
            except Exception as e:
                st.error(f"Unexpected error during speech generation: {e}")
    else:
        st.warning("Please enter text to synthesize.")

# --- Music Generation Section ---
st.header("Music Generation")
music_style_options = ["Ambient", "Upbeat", "Dramatic", "Peaceful", "Electronic", "Acoustic", "Experimental", "Cinematic"]
music_selected_style = st.selectbox("Select Music Style:", music_style_options, key="music_style_selectbox")
music_duration_seconds = st.number_input("Duration (seconds):", min_value=5, max_value=60, value=30, step=5, key="music_duration_numberinput")
backend_url_generate_music = "http://localhost:8000/generate-music"
if st.button("Generate Music"):
    with st.spinner("Generating music..."):
        try:
            payload = {"style": music_selected_style, "duration_seconds": music_duration_seconds}
            response_generate_music = requests.post(backend_url_generate_music, json=payload)
            if response_generate_music.status_code == 200:
                music_data = response_generate_music.json()
                music_path_relative_to_project = music_data.get("audio_path")
                if music_path_relative_to_project:
                    path_for_os_exists_music = os.path.join(PROJECT_BASE_PATH_FOR_FILES, music_path_relative_to_project)
                    if os.path.exists(path_for_os_exists_music):
                        st.session_state.generated_music_path = music_path_relative_to_project
                        reset_final_video_if_audio_changes()
                        st.audio(path_for_os_exists_music, format='audio/wav')
                        st.success(music_data.get("message", "Music generated!"))
                        st.caption(f"Style: {music_data.get('style_used', 'N/A')}, Duration: {music_data.get('duration_seconds', 'N/A')}s")
                    else:
                        st.error(f"Music audio file not found by frontend at: {path_for_os_exists_music}")
                else:
                    st.error("Backend did not return a music audio path.")
            else:
                st.error(f"Failed to generate music. Backend responded: {response_generate_music.status_code} - {response_generate_music.text}")
        except requests.exceptions.ConnectionError:
            st.error(f"Failed to connect to music generation backend at {backend_url_generate_music}.")
        except Exception as e:
            st.error(f"Unexpected error during music generation: {e}")

# --- Sound Effects (SFX) Generation ---
st.header("Sound Effects (SFX)")
sfx_category_options = ["Nature", "Urban", "Mechanical", "Human", "Fantasy", "Sci-Fi", "Ambient", "Impacts", "Alerts"]
sfx_selected_category = st.selectbox("Select SFX Category:", sfx_category_options, key="sfx_category_selectbox")
sfx_description_input = st.text_input("Describe the sound effect:", key="sfx_description_input")
st.caption("Note: A pre-generated SFX library will also be available for common sounds.")
backend_url_generate_sfx = "http://localhost:8000/generate-sfx"
if st.button("Generate SFX"):
    if sfx_description_input:
        with st.spinner("Generating SFX..."):
            try:
                payload = {"category": sfx_selected_category, "description": sfx_description_input}
                response_generate_sfx = requests.post(backend_url_generate_sfx, json=payload)
                if response_generate_sfx.status_code == 200:
                    sfx_data = response_generate_sfx.json()
                    sfx_path_relative_to_project = sfx_data.get("audio_path")
                    if sfx_path_relative_to_project:
                        path_for_os_exists_sfx = os.path.join(PROJECT_BASE_PATH_FOR_FILES, sfx_path_relative_to_project)
                        if os.path.exists(path_for_os_exists_sfx):
                            st.session_state.generated_sfx_path = sfx_path_relative_to_project
                            reset_final_video_if_audio_changes()
                            st.audio(path_for_os_exists_sfx, format='audio/wav')
                            st.success(sfx_data.get("message", "SFX generated!"))
                            st.caption(f"Category: {sfx_data.get('category_used', 'N/A')}, Description: {sfx_data.get('description_logged', 'N/A')}")
                        else:
                            st.error(f"SFX audio file not found by frontend at: {path_for_os_exists_sfx}")
                    else:
                        st.error("Backend did not return an SFX audio path.")
                else:
                    st.error(f"Failed to generate SFX. Backend responded: {response_generate_sfx.status_code} - {response_generate_sfx.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to SFX generation backend at {backend_url_generate_sfx}.")
            except Exception as e:
                st.error(f"Unexpected error during SFX generation: {e}")
    else:
        st.warning("Please describe the sound effect.")

# --- Lip Sync Video Section ---
st.header("Lip Sync Video")
if st.session_state.generated_video_path and st.session_state.generated_speech_path:
    st.write(f"Applying Lip Sync to video: `{st.session_state.generated_video_path}`")
    st.write(f"Using speech audio: `{st.session_state.generated_speech_path}`")
    if st.button("Apply Lip Sync"):
        backend_url_sync_lips = "http://localhost:8000/sync-lips"
        with st.spinner("Applying lip sync..."):
            try:
                payload = {"video_path": st.session_state.generated_video_path, "audio_path": st.session_state.generated_speech_path}
                response_sync_lips = requests.post(backend_url_sync_lips, json=payload)
                if response_sync_lips.status_code == 200:
                    lipsync_data = response_sync_lips.json()
                    lipsynced_video_path_relative = lipsync_data.get("lipsynced_video_path")
                    if lipsynced_video_path_relative:
                        path_for_os_exists_lipsync = os.path.join(PROJECT_BASE_PATH_FOR_FILES, lipsynced_video_path_relative)
                        if os.path.exists(path_for_os_exists_lipsync):
                            st.session_state.lipsynced_video_path = lipsynced_video_path_relative
                            st.session_state.final_video_path = None # Reset final video if lipsync changes
                            st.video(path_for_os_exists_lipsync)
                            st.success(lipsync_data.get("message", "Lip sync applied!"))
                        else:
                            st.error(f"Lipsynced video file not found by frontend at: {path_for_os_exists_lipsync}")
                    else:
                        st.error("Backend did not return a lipsynced video path.")
                else:
                    st.error(f"Failed to apply lip sync. Backend responded: {response_sync_lips.status_code} - {response_sync_lips.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to the lip sync backend at {backend_url_sync_lips}.")
            except Exception as e:
                st.error(f"An unexpected error occurred during lip sync: {e}")
else:
    st.info("Generate a video and speech audio first to enable lip sync.")

# --- Final Assembly & Export Section ---
st.header("Final Assembly & Export")
if st.session_state.lipsynced_video_path and st.session_state.generated_speech_path:
    st.write("Ready to assemble the final video using:")
    st.write(f"- Video (lipsynced): `{st.session_state.lipsynced_video_path}`")
    st.write(f"- Speech Audio: `{st.session_state.generated_speech_path}`")
    if st.session_state.generated_music_path:
        st.write(f"- Music Audio: `{st.session_state.generated_music_path}`")
    if st.session_state.generated_sfx_path:
        st.write(f"- SFX Audio: `{st.session_state.generated_sfx_path}`")

    st.subheader("Export Settings")
    final_resolution = st.selectbox("Resolution:", ["Source", "512p", "720p", "1080p"], key="final_resolution_selectbox")
    final_quality = st.selectbox("Quality:", ["Good (Fast)", "Better (Balanced)", "Best (Slow)"], key="final_quality_selectbox")
    final_format = st.selectbox("Format:", ["MP4 (H.264)", "WebM (VP9)"], key="final_format_selectbox")

    if st.button("Assemble and Export Video"):
        backend_url_assemble_video = "http://localhost:8000/assemble-video"
        sfx_tracks_payload = []
        if st.session_state.generated_sfx_path:
            sfx_tracks_payload.append({"sfx_path": st.session_state.generated_sfx_path})
            # For placeholder, we only handle one SFX. Real implementation would allow multiple.

        assembly_payload = {
            "base_video_path": st.session_state.lipsynced_video_path,
            "speech_audio_path": st.session_state.generated_speech_path,
            "music_audio_path": st.session_state.generated_music_path, # Can be None
            "sfx_tracks": sfx_tracks_payload if sfx_tracks_payload else None,
            "export_settings": {
                "resolution": final_resolution,
                "quality": final_quality,
                "format": final_format
            }
        }
        with st.spinner("Assembling and exporting final video..."):
            try:
                response_assemble = requests.post(backend_url_assemble_video, json=assembly_payload)
                if response_assemble.status_code == 200:
                    assembly_data = response_assemble.json()
                    final_video_path_relative = assembly_data.get("final_video_path")
                    if final_video_path_relative:
                        path_for_os_exists_final = os.path.join(PROJECT_BASE_PATH_FOR_FILES, final_video_path_relative)
                        if os.path.exists(path_for_os_exists_final):
                            st.session_state.final_video_path = final_video_path_relative
                            st.video(path_for_os_exists_final)
                            st.success(assembly_data.get("message", "Video assembled!"))
                            st.json(assembly_data.get("settings_applied", {}))
                        else:
                            st.error(f"Final video file not found by frontend at: {path_for_os_exists_final}")
                    else:
                        st.error("Backend did not return a final video path.")
                else:
                    st.error(f"Failed to assemble video. Backend responded: {response_assemble.status_code} - {response_assemble.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to the video assembly backend at {backend_url_assemble_video}.")
            except Exception as e:
                st.error(f"An unexpected error occurred during final assembly: {e}")
else:
    st.info("Generate a lipsynced video and speech audio first to enable final assembly.")
