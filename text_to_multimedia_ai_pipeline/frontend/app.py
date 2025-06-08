import streamlit as st
import requests
import os # For joining paths

st.title("Text-to-Multimedia AI Pipeline")

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


project_root_path = "/app/text_to_multimedia_ai_pipeline"
backend_url_generate = "http://localhost:8000/generate-image"

if st.button("Generate Image"):
    if prompt_text_input:

        final_prompt = prompt_text_input
        if selected_style != "None":
            final_prompt = f"{selected_style} style: {prompt_text_input}"

        # For debugging/visibility during actual app run, not visible in tool output here
        # This st.write will only be visible when running the Streamlit app.
        # st.write(f"Sending prompt to backend: \"{final_prompt}\"")

        with st.spinner("Generating image..."):
            try:
                payload = {"prompt": final_prompt}
                response_generate = requests.post(backend_url_generate, json=payload)

                if response_generate.status_code == 200:
                    data = response_generate.json()
                    relative_image_path = data.get("image_path")

                    if relative_image_path:
                        full_image_path = os.path.join(project_root_path, relative_image_path)

                        if os.path.exists(full_image_path):
                            # Using final_prompt for the caption
                            st.image(full_image_path, caption=f"Generated image for: {final_prompt[:70]}...")
                            st.success(data.get("message", "Image generated!"))
                        else:
                            st.error(f"Image file not found at expected path: {full_image_path}")
                            st.info(f"Backend returned relative path: {relative_image_path}")
                            st.info(f"Backend response: {data}")
                            # Fallback check for generic placeholder (for debugging)
                            placeholder_image_name = "placeholder_image.png"
                            expected_placeholder_path_in_data_dir = os.path.join("data/generated_images", placeholder_image_name)
                            full_expected_placeholder_path = os.path.join(project_root_path, expected_placeholder_path_in_data_dir)
                            if os.path.exists(full_expected_placeholder_path):
                                st.warning(f"Note: The generic placeholder image DOES exist at {full_expected_placeholder_path}. The issue might be with how the dynamic path is handled or returned by the backend for the current request.")
                            else:
                                st.warning(f"Note: The generic placeholder image ALSO does not exist at {full_expected_placeholder_path}. Ensure backend is running and creating images.")
                else:
                    st.error(f"Failed to generate image. Backend responded with status: {response_generate.status_code}")
                    try:
                        error_detail = response_generate.json().get("detail", "No additional details.")
                        st.error(f"Details: {error_detail}")
                    except requests.exceptions.JSONDecodeError:
                        st.error("Could not parse error details from backend.")

            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to the backend at {backend_url_generate}. Ensure it's running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")
