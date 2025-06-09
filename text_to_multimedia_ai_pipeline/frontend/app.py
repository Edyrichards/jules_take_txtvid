import streamlit as st
import requests
import os
import time

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- Constants ---
PROJECT_BASE_PATH_FOR_FILES = "text_to_multimedia_ai_pipeline"
BACKEND_BASE_URL = "http://localhost:8000"

# --- Session State Initialization ---
def initialize_session_state():
    # Default values for generated media paths
    media_paths = {
        'generated_image_path': None, 'generated_video_path': None, 'generated_speech_path': None,
        'generated_music_path': None, 'generated_sfx_path': None, 'lipsynced_video_path': None,
        'final_video_path': None
    }
    # Default values for UI inputs / selections
    ui_inputs = {
        'current_step': 0,
        'project_name_input': "My Multimedia Project", # Changed from project_name
        'selected_template_option': "None",            # New for template selection
        'image_prompt_text_input': "A futuristic cityscape at dusk, high detail, vibrant colors",
        'image_style_preset_input': "Photographic",
        'video_motion_type_input': "None",
        'tts_text_input': "Hello, welcome to this generated presentation.",
        'tts_voice_input': "Male Young Professional", # Default if no template
        'tts_emotion_input': "Neutral",
        'music_style_input': "Ambient",
        'music_duration_input': 30,
        'sfx_category_input': "Nature",
        'sfx_description_input': "birds chirping",
        'final_resolution': "Source",
        'final_quality': "Good (Fast)",
        'final_format': "MP4 (H.264)",
    }

    defaults = {**media_paths, **ui_inputs}

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# --- Reset Functions ---
def reset_all_session_state():
    # Store current step to return to it after reset if needed, or just go to 0
    # For "Start New Project", we always go to step 0.

    # Get all keys from the defaults to ensure we cover everything
    # (except current_step which is handled separately)
    temp_defaults = {}
    # Call initialize for a temp dict to get all default keys and values
    def temp_init():
        temp_ui_inputs = {
            'project_name_input': "My Multimedia Project",
            'selected_template_option': "None",
            'image_prompt_text_input': "A futuristic cityscape at dusk, high detail, vibrant colors",
            'image_style_preset_input': "Photographic",
            'video_motion_type_input': "None",
            'tts_text_input': "Hello, welcome to this generated presentation.",
            'tts_voice_input': "Male Young Professional",
            'tts_emotion_input': "Neutral",
            'music_style_input': "Ambient",
            'music_duration_input': 30,
            'sfx_category_input': "Nature",
            'sfx_description_input': "birds chirping",
            'final_resolution': "Source",
            'final_quality': "Good (Fast)",
            'final_format': "MP4 (H.264)",
        }
        temp_media_paths = {
            'generated_image_path': None, 'generated_video_path': None, 'generated_speech_path': None,
            'generated_music_path': None, 'generated_sfx_path': None, 'lipsynced_video_path': None,
            'final_video_path': None
        }
        return {**temp_media_paths, **temp_ui_inputs}

    all_default_keys = temp_init()

    for key in all_default_keys.keys():
        st.session_state[key] = all_default_keys[key] # Reset to its specific default

    st.session_state.current_step = 0


def reset_downstream_from_image_gen():
    st.session_state.generated_video_path = None; st.session_state.lipsynced_video_path = None
    st.session_state.final_video_path = None; reset_all_audio_components() # Clears speech, music, sfx

def reset_downstream_from_video_gen():
    st.session_state.lipsynced_video_path = None; st.session_state.final_video_path = None
    # Speech itself is not reset as it's independent of video, but lipsync is.

def reset_downstream_from_speech_gen():
    st.session_state.lipsynced_video_path = None; st.session_state.final_video_path = None

def reset_downstream_from_music_gen():
    st.session_state.final_video_path = None

def reset_downstream_from_sfx_gen():
    st.session_state.final_video_path = None

def reset_downstream_from_lipsync_gen():
    st.session_state.final_video_path = None

def reset_all_audio_components(): # Helper for image gen reset
    st.session_state.generated_speech_path = None
    st.session_state.generated_music_path = None
    st.session_state.generated_sfx_path = None


# --- Template Application Function ---
def apply_template():
    template = st.session_state.selected_template_option
    if template == "Quick Cinematic Clip":
        st.session_state.image_prompt_text_input = "Expansive alien desert under a twin-sun sky, cinematic vista, detailed matte painting style."
        st.session_state.image_style_preset_input = "Cinematic"
        st.session_state.video_motion_type_input = "Slow Pan Right"
        st.session_state.tts_text_input = "In a world beyond imagination, where twin suns blaze in an alien sky..." # Example
        st.session_state.tts_voice_input = "Male Mature Narrator" # Assuming this exists in options
        st.session_state.music_style_input = "Cinematic"
        st.session_state.music_duration_input = 15 # Adjusted for a clip
        st.success("Applied 'Quick Cinematic Clip' template!")
    elif template == "Spoken Presentation Slide":
        st.session_state.image_prompt_text_input = "Clean infographic background, abstract data visualization, professional, blue and white palette."
        st.session_state.image_style_preset_input = "Illustration"
        st.session_state.video_motion_type_input = "Slow Zoom In"
        st.session_state.tts_text_input = "Today, we will discuss the key findings from our latest research presented on this slide."
        st.session_state.tts_voice_input = "Female Mature Professional" # Assuming this exists
        st.session_state.music_style_input = "Ambient" # Subtle background
        st.session_state.music_duration_input = 20
        st.success("Applied 'Spoken Presentation Slide' template!")
    elif template == "None":
        # Reset to defaults or specific "None" state if different from initial defaults
        # For now, re-initializing specific fields to their initial defaults
        st.session_state.image_prompt_text_input = "A futuristic cityscape at dusk, high detail, vibrant colors"
        st.session_state.image_style_preset_input = "Photographic"
        st.session_state.video_motion_type_input = "None"
        st.session_state.tts_text_input = "Hello, welcome to this generated presentation."
        st.session_state.tts_voice_input = "Male Young Professional"
        st.session_state.music_style_input = "Ambient"
        st.session_state.music_duration_input = 30
        st.info("Template set to 'None'. Fields reset to initial defaults.")


# --- UI Display Functions for Each Step ---

def display_step_0_project_setup():
    st.header("Step 0: Project Setup")
    st.session_state.project_name_input = st.text_input("Project Name:", value=st.session_state.project_name_input, key="proj_name_step0_input")

    template_options = ["None", "Quick Cinematic Clip", "Spoken Presentation Slide"]
    selected_idx = template_options.index(st.session_state.selected_template_option)

    # Use on_change for selectbox to immediately update session state, then apply_template can use it.
    st.selectbox("Load Template:", template_options,
                 index=selected_idx,
                 key="selected_template_option", # This key will hold the selection directly
                 on_change=apply_template) # Call apply_template when selection changes

    # The "Apply Template" button is somewhat redundant if on_change is used, but can be kept for explicit action.
    # if st.button("Apply Template", key="apply_template_step0"):
    #     apply_template()
    #     st.rerun() # Rerun to reflect changes if not using on_change on selectbox

    if st.button("Start Project / Next", key="next_step0"):
        st.session_state.current_step = 1
        st.rerun()

def display_step_1_image_generation():
    st.header("Step 1: Image Generation")

    style_options_img = ["None", "Photographic", "Illustration", "Animation", "Cinematic", "Sketch"]
    # Ensure image_style_preset_input is valid or default to "None" / first item
    try:
        style_idx = style_options_img.index(st.session_state.image_style_preset_input)
    except ValueError:
        style_idx = 0 # Default to "None" or first item
        st.session_state.image_style_preset_input = style_options_img[style_idx]

    st.session_state.image_style_preset_input = st.selectbox("Select style:", style_options_img,
                                                       index=style_idx,
                                                       key="style_selectbox_img_step1_widget")
    st.session_state.image_prompt_text_input = st.text_area("Enter your image prompt:", value=st.session_state.image_prompt_text_input, height=100, key="prompt_text_area_img_step1_widget")

    if st.button("Generate Image", key="gen_img_step1"):
        if st.session_state.image_prompt_text_input:
            final_prompt_img = st.session_state.image_prompt_text_input
            if st.session_state.image_style_preset_input != "None": # Use the session state value
                final_prompt_img = f"{st.session_state.image_style_preset_input} style: {st.session_state.image_prompt_text_input}"

            with st.spinner("Generating image..."):
                try:
                    payload = {"prompt": final_prompt_img}
                    response = requests.post(f"{BACKEND_BASE_URL}/generate-image", json=payload)
                    if response.status_code == 200:
                        time.sleep(0.75) # Simulate processing time
                        data = response.json()
                        path_rel = data.get("image_path")
                        if path_rel and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path_rel)):
                            st.session_state.generated_image_path = path_rel
                            reset_downstream_from_image_gen()
                            st.success(data.get("message", "Image generated!"))
                        else: st.error(f"Generated image file not found: {path_rel}")
                    else: st.error(f"Failed: {response.status_code} - {response.text}")
                except Exception as e: st.error(f"Error: {e}")
        else: st.warning("Please enter a prompt.")

    if st.session_state.generated_image_path:
        st.image(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_image_path), caption="Generated Image")

    col1, col2 = st.columns(2);_ = col1.button("Back to Project Setup", on_click=lambda: st.session_state.update(current_step=0), key="back_step1");_ = col2.button("Next: Video Options", on_click=lambda: st.session_state.update(current_step=2), disabled=st.session_state.generated_image_path is None, key="next_step1")
    if col1.button("Back to Project Setup", key="back_step1_new"): st.session_state.current_step = 0; st.rerun()
    if col2.button("Next: Video Options", key="next_step1_new", disabled=st.session_state.generated_image_path is None): st.session_state.current_step = 2; st.rerun()


def display_step_2_video_generation():
    st.header("Step 2: Video Generation")
    if not st.session_state.generated_image_path:
        st.warning("Please generate an image in Step 1 first.")
        if st.button("Go to Image Generation", key="goto_step1_from_step2"): st.session_state.current_step = 1; st.rerun()
        return

    st.write(f"Using image: `{st.session_state.generated_image_path}`")
    motion_options = ["None", "Slow Pan Right", "Slow Pan Left", "Slow Zoom In", "Slow Zoom Out", "Tilt Up", "Tilt Down", "Dolly Zoom"]
    try: motion_idx = motion_options.index(st.session_state.video_motion_type_input)
    except ValueError: motion_idx = 0; st.session_state.video_motion_type_input = motion_options[motion_idx]
    st.session_state.video_motion_type_input = st.selectbox("Select motion type:", motion_options, index=motion_idx, key="motion_selectbox_video_step2_widget")

    if st.button("Generate Video", key="gen_video_step2"):
        with st.spinner("Generating video..."):
            try:
                payload = {"image_path": st.session_state.generated_image_path, "motion_type": st.session_state.video_motion_type_input}
                response = requests.post(f"{BACKEND_BASE_URL}/generate-video", json=payload)
                if response.status_code == 200:
                    time.sleep(0.75) # Simulate processing time
                    data = response.json(); path_rel = data.get("video_path")
                    if path_rel and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path_rel)):
                        st.session_state.generated_video_path = path_rel; reset_downstream_from_video_gen(); st.success(data.get("message", "Video generated!"))
                    else: st.error(f"Video file not found: {path_rel}")
                else: st.error(f"Failed: {response.status_code} - {response.text}")
            except Exception as e: st.error(f"Error: {e}")

    if st.session_state.generated_video_path: st.video(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_video_path))
    col1, col2 = st.columns(2)
    if col1.button("Back to Image Gen", key="back_step2_new"): st.session_state.current_step = 1; st.rerun()
    if col2.button("Next: Audio Config", key="next_step2_new", disabled=st.session_state.generated_video_path is None): st.session_state.current_step = 3; st.rerun()

def display_step_3_audio_configuration():
    st.header("Step 3: Audio Configuration")
    tab1, tab2, tab3 = st.tabs(["Text-to-Speech", "Background Music", "Sound Effects"])
    with tab1:
        st.subheader("Text-to-Speech")
        st.session_state.tts_text_input = st.text_area("Text:", value=st.session_state.tts_text_input, height=100, key="tts_text_widget")
        voice_opts = ["Male Young Professional", "Female Young Friendly", "Male Mature Narrator", "Female Mature Professional"]
        try: voice_idx = voice_opts.index(st.session_state.tts_voice_input)
        except ValueError: voice_idx = 0; st.session_state.tts_voice_input = voice_opts[voice_idx]
        st.session_state.tts_voice_input = st.selectbox("Voice:", voice_opts, index=voice_idx, key="tts_voice_widget")
        emotion_opts = ["Neutral", "Happy", "Calm", "Dramatic"];
        try: emotion_idx = emotion_opts.index(st.session_state.tts_emotion_input)
        except ValueError: emotion_idx = 0; st.session_state.tts_emotion_input = emotion_opts[emotion_idx]
        st.session_state.tts_emotion_input = st.selectbox("Emotion:", emotion_opts, index=emotion_idx, key="tts_emotion_widget")
        if st.button("Generate Speech", key="gen_speech_step3_widget"):
            # ... (API call logic as before, using st.session_state.tts_text_input etc.)
            if st.session_state.tts_text_input:
                with st.spinner("Generating speech..."):
                    try:
                        payload = {"text": st.session_state.tts_text_input, "voice": st.session_state.tts_voice_input, "emotion": st.session_state.tts_emotion_input}
                        response = requests.post(f"{BACKEND_BASE_URL}/generate-speech", json=payload)
                        if response.status_code == 200:
                            time.sleep(0.75) # Simulate processing time
                            data = response.json(); path_rel = data.get("audio_path")
                            if path_rel and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path_rel)):
                                st.session_state.generated_speech_path = path_rel; reset_downstream_from_speech_gen(); st.success(data.get("message"))
                            else: st.error(f"Speech file not found: {path_rel if path_rel else 'N/A'}")
                        else: st.error(f"Failed: {response.status_code} - {response.text}")
                    except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Please enter text for speech.")
        if st.session_state.generated_speech_path: st.audio(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_speech_path))
    with tab2:
        st.subheader("Background Music")
        music_styles = ["Ambient", "Upbeat", "Dramatic", "Peaceful", "Electronic"];
        try: music_idx = music_styles.index(st.session_state.music_style_input)
        except ValueError: music_idx = 0; st.session_state.music_style_input = music_styles[music_idx]
        st.session_state.music_style_input = st.selectbox("Style:", music_styles, index=music_idx, key="music_style_widget")
        st.session_state.music_duration_input = st.number_input("Duration (s):", value=st.session_state.music_duration_input, min_value=5, max_value=60, step=5, key="music_duration_widget")
        if st.button("Generate Music", key="gen_music_step3_widget"):
            # ... (API call logic)
            with st.spinner("Generating music..."):
                try:
                    payload = {"style": st.session_state.music_style_input, "duration_seconds": st.session_state.music_duration_input}
                    response = requests.post(f"{BACKEND_BASE_URL}/generate-music", json=payload)
                    if response.status_code == 200:
                        time.sleep(0.75) # Simulate processing time
                        data = response.json(); path_rel = data.get("audio_path")
                        if path_rel and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path_rel)):
                            st.session_state.generated_music_path = path_rel; reset_downstream_from_music_gen(); st.success(data.get("message"))
                        else: st.error(f"Music file not found: {path_rel if path_rel else 'N/A'}")
                    else: st.error(f"Failed: {response.status_code} - {response.text}")
                except Exception as e: st.error(f"Error: {e}")
        if st.session_state.generated_music_path: st.audio(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_music_path))
    with tab3:
        st.subheader("Sound Effects")
        sfx_cats = ["Nature", "Urban", "Mechanical", "Impacts", "Alerts"];
        try: sfx_cat_idx = sfx_cats.index(st.session_state.sfx_category_input)
        except ValueError: sfx_cat_idx = 0; st.session_state.sfx_category_input = sfx_cats[sfx_cat_idx]
        st.session_state.sfx_category_input = st.selectbox("Category:", sfx_cats, index=sfx_cat_idx, key="sfx_cat_widget")
        st.session_state.sfx_description_input = st.text_input("Description:", value=st.session_state.sfx_description_input, key="sfx_desc_widget")
        st.caption("Note: A pre-generated SFX library will also be available.")
        if st.button("Generate SFX", key="gen_sfx_step3_widget"):
            # ... (API call logic)
            if st.session_state.sfx_description_input:
                with st.spinner("Generating SFX..."):
                    try:
                        payload = {"category": st.session_state.sfx_category_input, "description": st.session_state.sfx_description_input}
                        response = requests.post(f"{BACKEND_BASE_URL}/generate-sfx", json=payload)
                        if response.status_code == 200:
                            time.sleep(0.75) # Simulate processing time
                            data = response.json(); path_rel = data.get("audio_path")
                            if path_rel and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path_rel)):
                                st.session_state.generated_sfx_path = path_rel; reset_downstream_from_sfx_gen(); st.success(data.get("message"))
                            else: st.error(f"SFX file not found: {path_rel if path_rel else 'N/A'}")
                        else: st.error(f"Failed: {response.status_code} - {response.text}")
                    except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Please describe SFX.")
        if st.session_state.generated_sfx_path: st.audio(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_sfx_path))
    st.divider()
    col1,col2=st.columns(2)
    if col1.button("Back to Video Gen",key="back_step3_new"):st.session_state.current_step=2;st.rerun()
    if col2.button("Next: Lip Sync",key="next_step3_new"):st.session_state.current_step=4;st.rerun()

def display_step_4_lip_sync():
    st.header("Step 4: Lip Sync")
    if not st.session_state.generated_video_path or not st.session_state.generated_speech_path:
        st.info("Lip sync requires video (Step 2) and speech audio (Step 3).")
        if st.button("Back to Audio Config",key="back_audio_lipsync_new"):st.session_state.current_step=3;st.rerun()
        return
    st.write(f"Video: `{st.session_state.generated_video_path}`"); st.write(f"Speech: `{st.session_state.generated_speech_path}`")
    if st.button("Apply Lip Sync",key="apply_lipsync_step4_widget"):
        # ... (API call logic)
        with st.spinner("Applying lip sync..."):
            try:
                payload = {"video_path": st.session_state.generated_video_path, "audio_path": st.session_state.generated_speech_path}
                response = requests.post(f"{BACKEND_BASE_URL}/sync-lips", json=payload)
                if response.status_code == 200:
                    time.sleep(0.75) # Simulate processing time
                    data = response.json(); path_rel = data.get("lipsynced_video_path")
                    if path_rel and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path_rel)):
                        st.session_state.lipsynced_video_path = path_rel; reset_downstream_from_lipsync_gen(); st.success(data.get("message"))
                    else: st.error(f"Lipsynced video not found: {path_rel if path_rel else 'N/A'}")
                else: st.error(f"Failed: {response.status_code} - {response.text}")
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.lipsynced_video_path: st.video(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.lipsynced_video_path))
    col1,col2=st.columns(2)
    if col1.button("Back to Audio Config",key="back_step4_new"):st.session_state.current_step=3;st.rerun()
    if col2.button("Next: Final Assembly",key="next_step4_new",disabled=st.session_state.lipsynced_video_path is None):st.session_state.current_step=5;st.rerun()

def display_step_5_final_assembly():
    st.header("Step 5: Final Assembly & Export")
    if not st.session_state.lipsynced_video_path or not st.session_state.generated_speech_path:
        st.info("Final assembly requires lipsynced video (Step 4) and speech (Step 3).")
        if st.button("Back to Lip Sync",key="back_lipsync_assembly_new"):st.session_state.current_step=4;st.rerun()
        return
    st.markdown(f"- Video: `{st.session_state.lipsynced_video_path}`"); st.markdown(f"- Speech: `{st.session_state.generated_speech_path}`")
    if st.session_state.generated_music_path: st.markdown(f"- Music: `{st.session_state.generated_music_path}`")
    if st.session_state.generated_sfx_path: st.markdown(f"- SFX: `{st.session_state.generated_sfx_path}`")
    st.subheader("Export Settings")
    res_opts=["Source","512p","720p","1080p"]; fmt_opts=["MP4 (H.264)","WebM (VP9)"]; qual_opts=["Good (Fast)","Better (Balanced)","Best (Slow)"]
    try: res_idx = res_opts.index(st.session_state.final_resolution)
    except ValueError: res_idx = 0; st.session_state.final_resolution = res_opts[res_idx]
    st.session_state.final_resolution=st.selectbox("Resolution:",res_opts,index=res_idx,key="final_res_widget")
    try: qual_idx = qual_opts.index(st.session_state.final_quality)
    except ValueError: qual_idx = 0; st.session_state.final_quality = qual_opts[qual_idx]
    st.session_state.final_quality=st.selectbox("Quality:",qual_opts,index=qual_idx,key="final_qual_widget")
    try: fmt_idx = fmt_opts.index(st.session_state.final_format)
    except ValueError: fmt_idx = 0; st.session_state.final_format = fmt_opts[fmt_idx]
    st.session_state.final_format=st.selectbox("Format:",fmt_opts,index=fmt_idx,key="final_fmt_widget")
    if st.button("Assemble and Export Video",key="assemble_step5_widget"):
        # ... (API call logic)
        sfx_tracks = [{"sfx_path": st.session_state.generated_sfx_path}] if st.session_state.generated_sfx_path else None
        payload = {
            "base_video_path": st.session_state.lipsynced_video_path, "speech_audio_path": st.session_state.generated_speech_path,
            "music_audio_path": st.session_state.generated_music_path, "sfx_tracks": sfx_tracks,
            "export_settings": {"resolution":st.session_state.final_resolution,"quality":st.session_state.final_quality,"format":st.session_state.final_format}
        }
        with st.spinner("Assembling..."):
            try:
                response = requests.post(f"{BACKEND_BASE_URL}/assemble-video",json=payload)
                if response.status_code == 200:
                    time.sleep(0.75) # Simulate processing time
                    data=response.json(); path_rel=data.get("final_video_path")
                    if path_rel and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES,path_rel)):
                        st.session_state.final_video_path=path_rel; st.success(data.get("message")); st.json({"settings_applied":data.get("settings_applied")})
                    else: st.error(f"Final video not found: {path_rel if path_rel else 'N/A'}")
                else: st.error(f"Failed: {response.status_code} - {response.text}")
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.final_video_path: st.video(os.path.join(PROJECT_BASE_PATH_FOR_FILES,st.session_state.final_video_path))
    st.divider()
    col1,col2=st.columns(2)
    if col1.button("Back to Lip Sync",key="back_step5_new"):st.session_state.current_step=4;st.rerun()
    if col2.button("Start New Project",key="new_project_step5_new"):reset_all_session_state();st.rerun()

# --- Main App Logic ---
st.sidebar.title("Pipeline Steps")
step_options = ["0: Setup", "1: Image", "2: Video", "3: Audio", "4: Lip Sync", "5: Assembly"]
current_step_name = step_options[st.session_state.current_step]
st.sidebar.markdown(f"**Current: {current_step_name}**")

st.sidebar.divider()
st.sidebar.title("Project Management")
if st.sidebar.button("Save Project (Conceptual)", key="save_proj_sidebar"):
    st.sidebar.info(f"Project saving for '{st.session_state.project_name_input}' would store all current settings and media paths. This feature is planned.")
if st.sidebar.button("Load Project (Conceptual)", key="load_proj_sidebar"):
    st.sidebar.info("Project loading would allow restoring a saved project's settings and media. This feature is planned.")

# The main page content based on current step
if st.session_state.current_step == 0: display_step_0_project_setup()
elif st.session_state.current_step == 1: display_step_1_image_generation()
elif st.session_state.current_step == 2: display_step_2_video_generation()
elif st.session_state.current_step == 3: display_step_3_audio_configuration()
elif st.session_state.current_step == 4: display_step_4_lip_sync()
elif st.session_state.current_step == 5: display_step_5_final_assembly()

st.sidebar.divider()
st.sidebar.header("Backend Status")
try:
    r = requests.get(f"{BACKEND_BASE_URL}/health"); r.raise_for_status()
    st.sidebar.success(f"Backend: {r.json().get('status','OK')}")
except: st.sidebar.error("Backend: Connection failed.")
