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
    media_paths = {
        'generated_image_path': None, 'generated_video_path': None, 'generated_speech_path': None,
        'generated_music_path': None, 'generated_sfx_path': None, 'lipsynced_video_path': None,
        'final_video_path': None
    }
    ui_inputs = {
        'current_step': 0,
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
    defaults = {**media_paths, **ui_inputs}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# --- Reset Functions ---
def reset_all_session_state():
    def temp_init_defaults(): # Renamed to avoid conflict
        temp_ui_inputs = {
            'project_name_input': "My Multimedia Project", 'selected_template_option': "None",
            'image_prompt_text_input': "A futuristic cityscape at dusk, high detail, vibrant colors",
            'image_style_preset_input': "Photographic", 'video_motion_type_input': "None",
            'tts_text_input': "Hello, welcome to this generated presentation.",
            'tts_voice_input': "Male Young Professional", 'tts_emotion_input': "Neutral",
            'music_style_input': "Ambient", 'music_duration_input': 30,
            'sfx_category_input': "Nature", 'sfx_description_input': "birds chirping",
            'final_resolution': "Source", 'final_quality': "Good (Fast)", 'final_format': "MP4 (H.264)",
        }
        temp_media_paths = {
            'generated_image_path': None, 'generated_video_path': None, 'generated_speech_path': None,
            'generated_music_path': None, 'generated_sfx_path': None, 'lipsynced_video_path': None,
            'final_video_path': None
        }
        return {**temp_media_paths, **temp_ui_inputs}
    all_default_keys_values = temp_init_defaults()
    for key in all_default_keys_values.keys():
        st.session_state[key] = all_default_keys_values[key]
    st.session_state.current_step = 0

def reset_downstream_from_image_gen():
    keys = ['generated_video_path', 'lipsynced_video_path', 'final_video_path',
            'generated_speech_path', 'generated_music_path', 'generated_sfx_path']
    for key in keys: st.session_state[key] = None
def reset_downstream_from_video_gen():
    keys = ['lipsynced_video_path', 'final_video_path']
    for key in keys: st.session_state[key] = None
def reset_downstream_from_speech_gen():
    keys = ['lipsynced_video_path', 'final_video_path']
    for key in keys: st.session_state[key] = None
def reset_downstream_from_audio_change(): # Music or SFX
    st.session_state.final_video_path = None
def reset_downstream_from_lipsync_gen():
    st.session_state.final_video_path = None

# --- Template Application Function ---
def apply_template():
    template = st.session_state.selected_template_option
    # Voice options for templates
    tts_voice_options_list = ["Male Young Professional", "Female Young Friendly", "Male Mature Narrator", "Female Mature Professional"]

    if template == "Quick Cinematic Clip":
        st.session_state.update({
            'image_prompt_text_input': "Expansive alien desert under a twin-sun sky, cinematic vista, detailed matte painting style.",
            'image_style_preset_input': "Cinematic", 'video_motion_type_input': "Slow Pan Right",
            'tts_text_input': "In a world beyond imagination...",
            'tts_voice_input': "Male Mature Narrator" if "Male Mature Narrator" in tts_voice_options_list else tts_voice_options_list[0],
            'music_style_input': "Cinematic", 'music_duration_input': 15
        })
        st.success("Applied 'Quick Cinematic Clip' template!")
    elif template == "Spoken Presentation Slide":
        st.session_state.update({
            'image_prompt_text_input': "Clean infographic background, abstract data visualization, professional, blue and white palette.",
            'image_style_preset_input': "Illustration", 'video_motion_type_input': "Slow Zoom In",
            'tts_text_input': "Today, we will discuss the key findings from our latest research.",
            'tts_voice_input': "Female Mature Professional" if "Female Mature Professional" in tts_voice_options_list else tts_voice_options_list[0],
            'music_style_input': "Ambient", 'music_duration_input': 20
        })
        st.success("Applied 'Spoken Presentation Slide' template!")
    elif template == "None":
        st.session_state.update({
            'image_prompt_text_input': "A futuristic cityscape at dusk, high detail, vibrant colors",
            'image_style_preset_input': "Photographic", 'video_motion_type_input': "None",
            'tts_text_input': "Hello, welcome to this generated presentation.",
            'tts_voice_input': "Male Young Professional", 'music_style_input': "Ambient", 'music_duration_input': 30
        })
        st.info("Template set to 'None'. Fields reset to initial defaults.")

# --- UI Display Functions for Each Step ---
def display_step_0_project_setup():
    st.header("Step 0: Project Setup & Initialization")
    st.session_state.project_name_input = st.text_input("Project Name:", value=st.session_state.project_name_input, key="proj_name_step0_widget", help="Give your project a unique name for future reference (conceptual).")
    template_options = ["None", "Quick Cinematic Clip", "Spoken Presentation Slide"]
    try: idx = template_options.index(st.session_state.selected_template_option)
    except ValueError: idx = 0
    st.selectbox("Load Template:", template_options, index=idx, key="selected_template_option", on_change=apply_template, help="Select a template to pre-fill some settings for common use cases.")
    if st.button("Start Project / Next", key="next_step0_widget"):
        st.session_state.current_step = 1; st.rerun()

def display_step_1_image_generation():
    st.header("Step 1: Image Generation from Text")
    style_opts = ["None", "Photographic", "Illustration", "Animation", "Cinematic", "Sketch"]
    try: style_idx = style_opts.index(st.session_state.image_style_preset_input)
    except ValueError: style_idx = 0; st.session_state.image_style_preset_input = style_opts[0]
    st.session_state.image_style_preset_input = st.selectbox("Select image style:", style_opts, index=style_idx, key="img_style_widget", help="Choose a visual style. 'None' uses model's default.")
    st.session_state.image_prompt_text_input = st.text_area("Enter your image prompt:", value=st.session_state.image_prompt_text_input, height=100, key="img_prompt_widget", help="Describe the image. Be specific about subjects, style, colors, composition.")
    if st.button("Generate Image", key="gen_img_widget"):
        if st.session_state.image_prompt_text_input:
            prompt = f"{st.session_state.image_style_preset_input} style: {st.session_state.image_prompt_text_input}" if st.session_state.image_style_preset_input != "None" else st.session_state.image_prompt_text_input
            with st.spinner("Generating image..."):
                try:
                    response = requests.post(f"{BACKEND_BASE_URL}/generate-image", json={"prompt": prompt})
                    if response.status_code == 200:
                        time.sleep(0.75); data = response.json(); path = data.get("image_path")
                        if path and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path)):
                            st.session_state.generated_image_path = path; reset_downstream_from_image_gen()
                            st.success(f"Image generated! Path: {path}")
                            with st.expander("Generation Details", expanded=False):
                                st.markdown(f"**Path:** `{path}`"); st.markdown(f"**Prompt Used:** `{data.get('prompt_used', 'N/A')}`")
                                st.markdown(f"**Negative Prompt:** `{data.get('negative_prompt_used', 'N/A')}`"); st.markdown(f"**Resolution:** `{data.get('resolution', 'N/A')}`")
                                st.markdown(f"**Time (Simulated Backend):** `{data.get('generation_time_seconds', 'N/A')}s`"); st.markdown(f"**Upscaling:** `{data.get('upscaling_status', 'N/A')}`")
                        else: st.error(f"Image file not found: {path}")
                    else: st.error(f"Failed: {response.status_code} - {response.text}")
                except Exception as e: st.error(f"Error: {e}")
        else: st.warning("Please enter a prompt.")
    if st.session_state.generated_image_path: st.image(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_image_path), caption="Generated Image")
    col1, col2 = st.columns([1,1]);
    if col1.button("Back", key="back_step1_widget"): st.session_state.current_step = 0; st.rerun()
    if col2.button("Next", key="next_step1_widget", disabled=st.session_state.generated_image_path is None): st.session_state.current_step = 2; st.rerun()

def display_step_2_video_generation():
    st.header("Step 2: Video Generation from Image")
    if not st.session_state.generated_image_path:
        st.warning("Please generate an image in Step 1 first.");
        if st.button("Go to Image Step", key="goto_img_step2_widget"): st.session_state.current_step = 1; st.rerun()
        return
    st.write(f"Using image: `{st.session_state.generated_image_path}`")
    motion_opts = ["None", "Slow Pan Right", "Slow Pan Left", "Slow Zoom In", "Slow Zoom Out", "Tilt Up", "Tilt Down", "Dolly Zoom"]
    try: motion_idx = motion_opts.index(st.session_state.video_motion_type_input)
    except ValueError: motion_idx = 0; st.session_state.video_motion_type_input = motion_opts[0]
    st.session_state.video_motion_type_input = st.selectbox("Select motion type:", motion_opts, index=motion_idx, key="video_motion_widget", help="Choose how the image should be animated.")
    if st.button("Generate Video", key="gen_video_widget"):
        with st.spinner("Generating video..."):
            try:
                payload = {"image_path": st.session_state.generated_image_path, "motion_type": st.session_state.video_motion_type_input}
                response = requests.post(f"{BACKEND_BASE_URL}/generate-video", json=payload)
                if response.status_code == 200:
                    time.sleep(0.75); data = response.json(); path = data.get("video_path")
                    if path and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path)):
                        st.session_state.generated_video_path = path; reset_downstream_from_video_gen(); st.success(f"Video generated! Path: {path}")
                    else: st.error(f"Video file not found: {path}")
                else: st.error(f"Failed: {response.status_code} - {response.text}")
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.generated_video_path: st.video(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_video_path))
    col1, col2 = st.columns([1,1]);
    if col1.button("Back", key="back_step2_widget"): st.session_state.current_step = 1; st.rerun()
    if col2.button("Next", key="next_step2_widget", disabled=st.session_state.generated_video_path is None): st.session_state.current_step = 3; st.rerun()

def display_step_3_audio_configuration():
    st.header("Step 3: Audio Configuration (Optional)")
    st.markdown("Configure optional audio elements: speech narration, background music, and sound effects.")
    tab_tts, tab_music, tab_sfx = st.tabs(["Text-to-Speech", "Background Music", "Sound Effects"])
    with tab_tts:
        st.subheader("Text-to-Speech (TTS)"); st.session_state.tts_text_input = st.text_area("Text to Synthesize:", value=st.session_state.tts_text_input, height=100, key="tts_text_area_widget", help="Enter text for speech.")
        voice_opts = ["Male Young Professional", "Female Young Friendly", "Male Mature Narrator", "Female Mature Professional"]; try: v_idx = voice_opts.index(st.session_state.tts_voice_input)
        except ValueError: v_idx=0; st.session_state.tts_voice_input=voice_opts[0]
        st.session_state.tts_voice_input = st.selectbox("Select Voice:", voice_opts, index=v_idx, key="tts_voice_widget", help="Choose a voice personality.")
        emotion_opts = ["Neutral", "Happy", "Calm", "Dramatic"]; try: e_idx = emotion_opts.index(st.session_state.tts_emotion_input)
        except ValueError: e_idx=0; st.session_state.tts_emotion_input=emotion_opts[0]
        st.session_state.tts_emotion_input = st.selectbox("Select Emotion:", emotion_opts, index=e_idx, key="tts_emotion_widget")
        if st.button("Generate Speech", key="gen_speech_widget"):
            if st.session_state.tts_text_input:
                with st.spinner("Generating speech..."):
                    try:
                        payload = {"text":st.session_state.tts_text_input, "voice":st.session_state.tts_voice_input, "emotion":st.session_state.tts_emotion_input}
                        response = requests.post(f"{BACKEND_BASE_URL}/generate-speech", json=payload)
                        if response.status_code == 200:
                            time.sleep(0.75); data = response.json(); path = data.get("audio_path")
                            if path and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path)):
                                st.session_state.generated_speech_path = path; reset_downstream_from_speech_gen(); st.success(f"Speech generated! Path: {path}")
                            else: st.error(f"Speech file not found: {path}")
                        else: st.error(f"Failed: {response.status_code} - {response.text}")
                    except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Enter text for speech.")
        if st.session_state.generated_speech_path: st.audio(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_speech_path))
    with tab_music:
        st.subheader("Background Music"); music_styles = ["Ambient", "Upbeat", "Dramatic", "Peaceful", "Electronic", "Acoustic", "Experimental", "Cinematic"];
        try: mstyle_idx = music_styles.index(st.session_state.music_style_input)
        except ValueError: mstyle_idx=0; st.session_state.music_style_input=music_styles[0]
        st.session_state.music_style_input = st.selectbox("Select Music Style:", music_styles, index=mstyle_idx, key="music_style_widget")
        st.session_state.music_duration_input = st.number_input("Duration (seconds):", value=st.session_state.music_duration_input, min_value=5, max_value=60, step=5, key="music_duration_widget")
        if st.button("Generate Music", key="gen_music_widget"):
            with st.spinner("Generating music..."):
                try:
                    payload = {"style":st.session_state.music_style_input, "duration_seconds":st.session_state.music_duration_input}
                    response = requests.post(f"{BACKEND_BASE_URL}/generate-music", json=payload)
                    if response.status_code == 200:
                        time.sleep(0.75); data = response.json(); path = data.get("audio_path")
                        if path and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path)):
                            st.session_state.generated_music_path = path; reset_downstream_from_music_gen(); st.success(f"Music generated! Path: {path}")
                        else: st.error(f"Music file not found: {path}")
                    else: st.error(f"Failed: {response.status_code} - {response.text}")
                except Exception as e: st.error(f"Error: {e}")
        if st.session_state.generated_music_path: st.audio(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_music_path))
    with tab_sfx:
        st.subheader("Sound Effects (SFX)"); sfx_cats = ["Nature", "Urban", "Mechanical", "Human", "Fantasy", "Sci-Fi", "Ambient", "Impacts", "Alerts"];
        try: sfx_cat_idx = sfx_cats.index(st.session_state.sfx_category_input)
        except ValueError: sfx_cat_idx=0; st.session_state.sfx_category_input=sfx_cats[0]
        st.session_state.sfx_category_input = st.selectbox("Select SFX Category:", sfx_cats, index=sfx_cat_idx, key="sfx_cat_widget")
        st.session_state.sfx_description_input = st.text_input("Describe the sound effect:", value=st.session_state.sfx_description_input, key="sfx_desc_widget")
        st.caption("Note: A pre-generated SFX library will also be available for common sounds.")
        if st.button("Generate SFX", key="gen_sfx_widget"):
            if st.session_state.sfx_description_input:
                with st.spinner("Generating SFX..."):
                    try:
                        payload = {"category":st.session_state.sfx_category_input, "description":st.session_state.sfx_description_input}
                        response = requests.post(f"{BACKEND_BASE_URL}/generate-sfx", json=payload)
                        if response.status_code == 200:
                            time.sleep(0.75); data = response.json(); path = data.get("audio_path")
                            if path and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path)):
                                st.session_state.generated_sfx_path = path; reset_downstream_from_sfx_gen(); st.success(f"SFX generated! Path: {path}")
                            else: st.error(f"SFX file not found: {path}")
                        else: st.error(f"Failed: {response.status_code} - {response.text}")
                    except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Please describe the SFX.")
        if st.session_state.generated_sfx_path: st.audio(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.generated_sfx_path))
    st.divider()
    col1, col2 = st.columns([1,1]);
    if col1.button("Back", key="back_step3_widget"): st.session_state.current_step = 2; st.rerun()
    if col2.button("Next", key="next_step3_widget"): st.session_state.current_step = 4; st.rerun()

def display_step_4_lip_sync():
    st.header("Step 4: Lip Sync Video with Speech")
    if not (st.session_state.generated_video_path and st.session_state.generated_speech_path):
        st.info("Lip sync requires a generated video (Step 2) and generated speech audio (Step 3 - TTS).");
        if st.button("Back to Audio Step", key="back_lipsync_widget_pre"): st.session_state.current_step = 3; st.rerun()
        return
    st.write(f"Applying Lip Sync to video: `{st.session_state.generated_video_path}`")
    st.write(f"Using speech audio: `{st.session_state.generated_speech_path}`")
    if st.button("Apply Lip Sync", key="apply_lipsync_widget"):
        with st.spinner("Applying lip sync..."):
            try:
                payload = {"video_path": st.session_state.generated_video_path, "audio_path": st.session_state.generated_speech_path}
                response = requests.post(f"{BACKEND_BASE_URL}/sync-lips", json=payload)
                if response.status_code == 200:
                    time.sleep(0.75); data = response.json(); path = data.get("lipsynced_video_path")
                    if path and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES, path)):
                        st.session_state.lipsynced_video_path = path; reset_downstream_from_lipsync_gen(); st.success(f"Lip sync applied (placeholder)! Output: {path}")
                    else: st.error(f"Lipsynced video file not found: {path}")
                else: st.error(f"Failed: {response.status_code} - {response.text}")
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.lipsynced_video_path: st.video(os.path.join(PROJECT_BASE_PATH_FOR_FILES, st.session_state.lipsynced_video_path))
    col1, col2 = st.columns([1,1]);
    if col1.button("Back", key="back_step4_widget"): st.session_state.current_step = 3; st.rerun()
    if col2.button("Next", key="next_step4_widget", disabled=st.session_state.lipsynced_video_path is None): st.session_state.current_step = 5; st.rerun()

def display_step_5_final_assembly():
    st.header("Step 5: Final Assembly & Video Export")
    if not (st.session_state.lipsynced_video_path and st.session_state.generated_speech_path):
        st.info("Final assembly requires a lipsynced video (Step 4) and the corresponding speech audio (Step 3).")
        if st.button("Back to Lip Sync Step", key="back_assembly_widget_pre"): st.session_state.current_step = 4; st.rerun()
        return
    st.subheader("Media to be Assembled:")
    st.markdown(f"- **Base Video (Lipsynced):** `{st.session_state.lipsynced_video_path}`")
    st.markdown(f"- **Primary Speech Audio:** `{st.session_state.generated_speech_path}`")
    if st.session_state.generated_music_path: st.markdown(f"- **Background Music:** `{st.session_state.generated_music_path}`")
    sfx_for_assembly = []
    if st.session_state.generated_sfx_path:
        sfx_for_assembly.append({"sfx_path": st.session_state.generated_sfx_path}) # Simplification for one SFX
        st.markdown("- **Sound Effects:**")
        for sfx_item in sfx_for_assembly: st.markdown(f"  - `{sfx_item['sfx_path']}`")

    st.subheader("Export Settings")
    res_opts=["Source","512p","720p","1080p"]; fmt_opts=["MP4 (H.264)","WebM (VP9)"]; qual_opts=["Good (Fast)","Better (Balanced)","Best (Slow)"]
    try: res_idx = res_opts.index(st.session_state.final_resolution); except ValueError: res_idx=0
    st.session_state.final_resolution=st.selectbox("Resolution:",res_opts,index=res_idx,key="final_res_sel_widget", help="Select output resolution. 'Source' uses input video's resolution.")
    try: qual_idx = qual_opts.index(st.session_state.final_quality); except ValueError: qual_idx=0
    st.session_state.final_quality=st.selectbox("Quality:",qual_opts,index=qual_idx,key="final_qual_sel_widget", help="Higher quality may take longer (in real pipeline).")
    try: fmt_idx = fmt_opts.index(st.session_state.final_format); except ValueError: fmt_idx=0
    st.session_state.final_format=st.selectbox("Format:",fmt_opts,index=fmt_idx,key="final_fmt_sel_widget", help="Select video file format for export.")

    if st.button("Assemble and Export Video", key="assemble_export_widget"):
        payload = {
            "base_video_path": st.session_state.lipsynced_video_path, "speech_audio_path": st.session_state.generated_speech_path,
            "music_audio_path": st.session_state.generated_music_path, "sfx_tracks": sfx_for_assembly if sfx_for_assembly else None,
            "export_settings": {"resolution":st.session_state.final_resolution,"quality":st.session_state.final_quality,"format":st.session_state.final_format}
        }
        with st.spinner("Assembling and exporting final video..."):
            try:
                response = requests.post(f"{BACKEND_BASE_URL}/assemble-video",json=payload)
                if response.status_code == 200:
                    time.sleep(0.75); data=response.json(); path=data.get("final_video_path")
                    if path and os.path.exists(os.path.join(PROJECT_BASE_PATH_FOR_FILES,path)):
                        st.session_state.final_video_path=path; st.success(f"Final video assembled! Path: {path}")
                        st.json({"settings_applied":data.get("settings_applied")})
                    else: st.error(f"Final video file not found: {path}")
                else: st.error(f"Failed: {response.status_code} - {response.text}")
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.final_video_path: st.video(os.path.join(PROJECT_BASE_PATH_FOR_FILES,st.session_state.final_video_path))
    st.divider()
    col1, col2 = st.columns([1,1]);
    if col1.button("Back", key="back_step5_widget"): st.session_state.current_step = 4; st.rerun()
    if col2.button("Start New Project", key="new_project_step5_widget"): reset_all_session_state(); st.rerun()

# --- Main App Logic ---
st.sidebar.title("Pipeline Steps")
step_options = ["0: Setup", "1: Image", "2: Video", "3: Audio", "4: Lip Sync", "5: Assembly"]
current_step_name = step_options[st.session_state.current_step]
st.sidebar.markdown(f"**Current: {current_step_name}**")

st.sidebar.divider()
st.sidebar.title("Project Management")
if st.sidebar.button("Save Project (Conceptual)", key="save_proj_sidebar_widget"):
    st.sidebar.info(f"Project saving for '{st.session_state.project_name_input}' would store all current settings and media paths. This feature is planned.")
if st.sidebar.button("Load Project (Conceptual)", key="load_proj_sidebar_widget"):
    st.sidebar.info("Project loading would allow restoring a saved project's settings and media. This feature is planned.")

st.sidebar.divider()
st.sidebar.title("Help & Tips")
with st.sidebar.expander("Getting Started & Workflow", expanded=False):
    st.markdown("""
    This pipeline guides you through generating a complete video from text:
    1.  **Project Setup:** Name your project and optionally use a template.
    2.  **Image Generation:** Create your base visual from a text prompt.
    3.  **Video Generation:** Animate the image into a short video clip.
    4.  **Audio Configuration:** Add voice-over, background music, and sound effects.
    5.  **Lip Sync:** Synchronize the generated speech with the video.
    6.  **Final Assembly:** Combine all elements and export your video.

    *   Media generated in one step (e.g., an image) is automatically used as input for subsequent relevant steps.
    *   Use the 'Back' and 'Next' buttons to navigate the wizard.
    """)
with st.sidebar.expander("Tips for Prompts", expanded=False):
    st.markdown("""
    - **Be Specific:** Instead of "a cat", try "A fluffy ginger cat sleeping on a sunlit windowsill, impressionist painting style."
    - **Keywords Matter:** Use descriptive adjectives and mention artistic styles if desired.
    - **Experiment:** Try variations of your prompt to see different results.
    """)

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
