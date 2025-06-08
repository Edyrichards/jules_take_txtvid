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

# --- Image Generation Section ---
st.header("Generate Image")

style_options = ["None", "Photographic", "Illustration", "Animation", "Cinematic", "Sketch"]
selected_style = st.selectbox("Select style:", style_options)

prompt_text_input = st.text_area("Enter your image prompt:", height=100, key="prompt_text_area")

# Path context for os.path.exists checks if needed from script's perspective
# /app is the root in the sandbox. Backend saves files relative to /app/text_to_multimedia_ai_pipeline
PROJECT_BASE_PATH_FOR_FILES = "text_to_multimedia_ai_pipeline" # Relative to /app
backend_url_generate_image = "http://localhost:8000/generate-image"

if st.button("Generate Image"):
    if prompt_text_input:
        final_prompt = prompt_text_input
        if selected_style != "None":
            final_prompt = f"{selected_style} style: {prompt_text_input}"

        with st.spinner("Generating image..."):
            try:
                payload = {"prompt": final_prompt}
                response_generate = requests.post(backend_url_generate_image, json=payload)

                if response_generate.status_code == 200:
                    data = response_generate.json()
                    # This path is relative to project root e.g. "data/generated_images/placeholder_image.png"
                    image_path_relative_to_project = data.get("image_path")

                    if image_path_relative_to_project:
                        # For st.image, this path should work if Streamlit CWD is project root.
                        # For os.path.exists, we need a path relative to the script's CWD (which is /app)
                        # or an absolute path.
                        # Backend saves to /app/text_to_multimedia_ai_pipeline/data/...
                        # So, path for os.path.exists from /app is text_to_multimedia_ai_pipeline/data/...
                        path_for_os_exists = os.path.join(PROJECT_BASE_PATH_FOR_FILES, image_path_relative_to_project)

                        if os.path.exists(path_for_os_exists):
                            st.image(path_for_os_exists, caption=f"Generated image for: {final_prompt[:70]}...")
                            st.success(data.get("message", "Image generated!"))
                            st.session_state.generated_image_path = image_path_relative_to_project # Store for video gen
                            st.session_state.generated_video_path = None # Reset video path if new image
                        else:
                            st.error(f"Image file not found by frontend at path: {path_for_os_exists}")
                            st.info(f"Backend returned: {image_path_relative_to_project}. Backend response: {data}")
                    else:
                        st.error("Backend did not return an image path.")
                else:
                    st.error(f"Failed to generate image. Backend responded with status: {response_generate.status_code}")
                    try:
                        error_detail = response_generate.json().get("detail", "No additional details.")
                        st.error(f"Details: {error_detail}")
                    except requests.exceptions.JSONDecodeError:
                        st.error("Could not parse error details from backend.")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to the image generation backend at {backend_url_generate_image}.")
            except Exception as e:
                st.error(f"An unexpected error occurred during image generation: {e}")
    else:
        st.warning("Please enter a prompt.")

# --- Video Generation Section ---
st.header("Generate Video")

if st.session_state.generated_image_path:
    st.write(f"Using image: `{st.session_state.generated_image_path}` for video generation.")

    motion_presets = [
        "None", "Slow Pan Right", "Slow Pan Left", "Slow Zoom In", "Slow Zoom Out",
        "Tilt Up", "Tilt Down", "Dolly Zoom", "Gentle Rotation Clockwise",
        "Gentle Rotation Counter-Clockwise", "Subtle Object Sway", "Lighting Flicker"
    ]
    selected_motion = st.selectbox("Select motion type:", motion_presets, key="motion_type_selectbox")

    # Button is implicitly enabled only if st.session_state.generated_image_path is not None
    if st.button("Generate Video"):
        backend_url_generate_video = "http://localhost:8000/generate-video"
        with st.spinner("Generating video..."):
            try:
                payload = {
                    "image_path": st.session_state.generated_image_path, # This is project-root relative path
                    "motion_type": selected_motion
                }
                response_generate_video = requests.post(backend_url_generate_video, json=payload)

                if response_generate_video.status_code == 200:
                    video_data = response_generate_video.json()
                    # This path is relative to project root, e.g., "data/generated_videos/placeholder_video.mp4"
                    video_path_relative_to_project = video_data.get("video_path")

                    if video_path_relative_to_project:
                        # For st.video, this path should work if Streamlit CWD is project root.
                        # For os.path.exists, similar to image section:
                        path_for_os_exists_video = os.path.join(PROJECT_BASE_PATH_FOR_FILES, video_path_relative_to_project)

                        if os.path.exists(path_for_os_exists_video):
                            st.session_state.generated_video_path = video_path_relative_to_project # Store for display
                            # Use the path that os.path.exists confirmed, for st.video
                            st.video(path_for_os_exists_video)
                            st.success(video_data.get("message", "Video generated!"))
                        else:
                            st.error(f"Video file not found by frontend at path: {path_for_os_exists_video}")
                            st.info(f"Backend returned: {video_path_relative_to_project}. Backend response: {video_data}")
                    else:
                        st.error("Backend did not return a video path.")
                else:
                    st.error(f"Failed to generate video. Backend responded with status: {response_generate_video.status_code}")
                    try:
                        error_detail = response_generate_video.json().get("detail", "No additional details.")
                        st.error(f"Details: {error_detail}")
                    except requests.exceptions.JSONDecodeError:
                        st.error("Could not parse error details from backend.")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to the video generation backend at {backend_url_generate_video}.")
            except Exception as e:
                st.error(f"An unexpected error occurred during video generation: {e}")
                # For local debugging:
                # st.error(f"Error: {e} - {traceback.format_exc()}")
else:
    st.info("Please generate an image first (in the 'Generate Image' section above) to enable video generation.")
