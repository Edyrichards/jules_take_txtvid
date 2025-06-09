from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from PIL import Image # For dummy image
import io
from fastapi.responses import FileResponse # Required for returning files
import cv2 # For OpenCV
import shutil # For file operations
import wave # For placeholder speech/music/sfx audio
from typing import List, Optional # For AssemblyRequest model

app = FastAPI()

# --- Project Root Path (for resolving relative paths from client) ---
PROJECT_ROOT_DIR = "/app/text_to_multimedia_ai_pipeline"

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ImagePrompt(BaseModel):
    prompt: str

GENERATED_IMAGES_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_images")
os.makedirs(GENERATED_IMAGES_DIR_SERVER, exist_ok=True)

# New imports for MLX Stable Diffusion
from . import config_sd as mlx_config_sd # Alias to avoid conflict if main.py had its own config_sd
from . import mlx_stable_diffusion
import time # Already imported but ensure it's used

@app.post("/generate-image")
async def generate_image(prompt_data: ImagePrompt):
    prompt = prompt_data.prompt
    # Example negative prompt, could be configurable
    negative_prompt = "low quality, blurry, noisy, text, watermark, signature, ugly, deformed"

    print(f"Received prompt for MLX Stable Diffusion: '{prompt}'")
    print(f"Using negative prompt: '{negative_prompt}'")

    try:
        start_time_gen = time.time()

        # Call the MLX Stable Diffusion generation function
        pil_image = mlx_stable_diffusion.generate_image_with_mlx(
            prompt=prompt,
            negative_prompt=negative_prompt,
            # num_steps and guidance_scale will use defaults from config_sd via mlx_stable_diffusion.py
        )

        end_time_gen = time.time()
        generation_time = end_time_gen - start_time_gen
        print(f"MLX Stable Diffusion image generated in {generation_time:.2f} seconds (actual or placeholder timing).")

        # Save the PIL image to a file
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        sane_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30]).rstrip("_")
        image_filename = f"sd_image_{sane_prompt}_{timestamp}.{mlx_config_sd.OUTPUT_IMAGE_FORMAT.lower()}"

        image_path_server = os.path.join(GENERATED_IMAGES_DIR_SERVER, image_filename)
        image_path_client = os.path.join("data/generated_images", image_filename)

        pil_image.save(image_path_server, format=mlx_config_sd.OUTPUT_IMAGE_FORMAT)
        print(f"Generated image saved to: {image_path_server}")

        # --- Upscaling Placeholder (as before) ---
        print("Placeholder: Upscaling would be applied here (e.g., with Real-ESRGAN) if an upscaler was integrated.")
        upscaling_status_message = "pending_integration"
        base_resolution = f"{pil_image.width}x{pil_image.height}"
        # --- End of Upscaling Placeholder ---

        return {
            "message": f"Image generated successfully with MLX Stable Diffusion in {generation_time:.2f}s.",
            "image_path": image_path_client,
            "resolution": base_resolution,
            "upscaling_status": upscaling_status_message,
            "prompt_used": prompt,
            "negative_prompt_used": negative_prompt,
            "generation_time_seconds": round(generation_time, 2)
        }
    except FileNotFoundError as fnf_error:
        print(f"Model FileNotFoundError in /generate-image: {fnf_error}")
        # This error is specifically for model files not found by mlx_stable_diffusion.ensure_models_loaded()
        raise HTTPException(status_code=500, detail=f"Model files not found. Please check server logs and ensure models are correctly placed as per 'models/stable_diffusion_mlx/README.md'. Error: {fnf_error}")
    except RuntimeError as e:
        # Catch potential MLX/MPS runtime errors
        print(f"RuntimeError in /generate-image: {e}")
        import traceback
        traceback.print_exc()
        error_detail = str(e)
        if "MPS" in error_detail or "mlx" in error_detail or "metal" in error_detail.lower():
            error_detail = "An error occurred with the MLX/MPS (Apple Silicon GPU) backend during image generation. This could be due to model compatibility, memory issues, or driver problems. Check server logs for details."
        raise HTTPException(status_code=500, detail=error_detail)
    except Exception as e:
        print(f"General Exception in /generate-image: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during image generation: {str(e)}")

class VideoRequest(BaseModel):
    image_path: str
    motion_type: str

GENERATED_VIDEOS_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_videos")
os.makedirs(GENERATED_VIDEOS_DIR_SERVER, exist_ok=True)

@app.post("/generate-video")
async def generate_video(request: VideoRequest):
    print(f"Received video request: image_path='{request.image_path}', motion_type='{request.motion_type}'")
    actual_image_path_on_server = os.path.join(PROJECT_ROOT_DIR, request.image_path)
    if not os.path.exists(actual_image_path_on_server):
        print(f"Error: Input image not found at {actual_image_path_on_server}")
        raise HTTPException(status_code=404, detail=f"Input image not found: {request.image_path}")
    output_video_filename = "placeholder_video.mp4"
    output_video_path_on_server = os.path.join(GENERATED_VIDEOS_DIR_SERVER, output_video_filename)
    try:
        img_cv = cv2.imread(actual_image_path_on_server)
        if img_cv is None:
            print(f"Error: cv2.imread failed to load image from {actual_image_path_on_server}")
            raise HTTPException(status_code=500, detail=f"Could not read image data from {request.image_path} using OpenCV.")
        height, width, _ = img_cv.shape
        fps = 1
        duration_seconds = 1
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_video_path_on_server, fourcc, fps, (width, height))
        if not video_writer.isOpened():
            print(f"Error: cv2.VideoWriter failed to open for path {output_video_path_on_server}")
            raise HTTPException(status_code=500, detail="Failed to initialize video writer.")
        for _ in range(fps * duration_seconds):
            video_writer.write(img_cv)
        video_writer.release()
        print(f"Placeholder video saved to {output_video_path_on_server}")
        print("Placeholder: Frame interpolation (e.g., RIFE) would be applied here for smoothness if integrated.")
        frame_interpolation_status = "pending_integration"
        print("Placeholder: Video upscaling (e.g., lightweight video ESRGAN) would be applied here if integrated.")
        video_upscaling_status = "pending_integration"
    except Exception as e:
        print(f"Error generating placeholder video with OpenCV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create placeholder video: {str(e)}")
    client_accessible_video_path = os.path.join("data/generated_videos", output_video_filename)
    return {
        "message": "Video generated successfully (placeholder)",
        "video_path": client_accessible_video_path,
        "base_resolution": f"{width}x{height}",
        "fps": fps,
        "duration_seconds": duration_seconds,
        "frame_interpolation_status": frame_interpolation_status,
        "video_upscaling_status": video_upscaling_status
    }

class TTSRequest(BaseModel):
    text: str
    voice: str
    emotion: str

GENERATED_AUDIO_SPEECH_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_audio/speech")
os.makedirs(GENERATED_AUDIO_SPEECH_DIR_SERVER, exist_ok=True)

@app.post("/generate-speech")
async def generate_speech(request: TTSRequest):
    print(f"Received speech request: text='{request.text[:50]}...', voice='{request.voice}', emotion='{request.emotion}'")
    output_filename = "placeholder_speech.wav"
    output_path_server = os.path.join(GENERATED_AUDIO_SPEECH_DIR_SERVER, output_filename)
    output_path_client = os.path.join("data/generated_audio/speech", output_filename)
    try:
        with wave.open(output_path_server, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            silent_frame = b'\x00\x00'
            num_frames = 44100 * 1
            frames_data = silent_frame * num_frames
            wf.writeframes(frames_data)
        print(f"Placeholder speech audio saved to {output_path_server}")
    except Exception as e:
        print(f"Error generating placeholder speech audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create placeholder speech audio: {str(e)}")
    return {
        "message": "Speech generated successfully (placeholder)",
        "audio_path": output_path_client,
        "voice_used": request.voice,
        "emotion_used": request.emotion
    }

class MusicRequest(BaseModel):
    style: str
    duration_seconds: int

GENERATED_AUDIO_MUSIC_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_audio/music")
os.makedirs(GENERATED_AUDIO_MUSIC_DIR_SERVER, exist_ok=True)

@app.post("/generate-music")
async def generate_music(request: MusicRequest):
    print(f"Received music request: style='{request.style}', duration='{request.duration_seconds}s'")
    output_filename = "placeholder_music.wav"
    output_path_server = os.path.join(GENERATED_AUDIO_MUSIC_DIR_SERVER, output_filename)
    output_path_client = os.path.join("data/generated_audio/music", output_filename)
    duration = max(1, request.duration_seconds)
    try:
        with wave.open(output_path_server, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            num_frames_music = 44100 * duration
            silent_frame_music = b'\x00\x00'
            frames_data_music = silent_frame_music * num_frames_music
            wf.writeframes(frames_data_music)
        print(f"Placeholder music audio saved to {output_path_server} (Duration: {duration}s)")
    except Exception as e:
        print(f"Error generating placeholder music audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create placeholder music audio: {str(e)}")
    return {
        "message": "Music generated successfully (placeholder)",
        "audio_path": output_path_client,
        "style_used": request.style,
        "duration_seconds": duration
    }

class SFXRequest(BaseModel):
    category: str
    description: str

GENERATED_AUDIO_SFX_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_audio/sfx")
os.makedirs(GENERATED_AUDIO_SFX_DIR_SERVER, exist_ok=True)

@app.post("/generate-sfx")
async def generate_sfx(request: SFXRequest):
    print(f"Received SFX request: category='{request.category}', description='{request.description[:50]}...'")
    output_filename = "placeholder_sfx.wav"
    output_path_server = os.path.join(GENERATED_AUDIO_SFX_DIR_SERVER, output_filename)
    output_path_client = os.path.join("data/generated_audio/sfx", output_filename)
    sfx_duration = 0.5
    try:
        with wave.open(output_path_server, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            num_frames_sfx = int(44100 * sfx_duration)
            silent_frame_sfx = b'\x00\x00'
            frames_data_sfx = silent_frame_sfx * num_frames_sfx
            wf.writeframes(frames_data_sfx)
        print(f"Placeholder SFX audio saved to {output_path_server} (Duration: {sfx_duration}s)")
        print(f"Concept: For SFX '{request.description}' in category '{request.category}'. Future: AudioLDM or library lookup.")
    except Exception as e:
        print(f"Error generating placeholder SFX audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create placeholder SFX audio: {str(e)}")
    return {
        "message": "SFX generated successfully (placeholder)",
        "audio_path": output_path_client,
        "category_used": request.category,
        "description_logged": request.description
    }

class LipSyncRequest(BaseModel):
    video_path: str
    audio_path: str

GENERATED_VIDEOS_LIPSYNCED_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_videos/lipsynced")
os.makedirs(GENERATED_VIDEOS_LIPSYNCED_DIR_SERVER, exist_ok=True)

@app.post("/sync-lips")
async def sync_lips(request: LipSyncRequest):
    print(f"Received lip sync request for video: '{request.video_path}' and audio: '{request.audio_path}'")
    actual_video_path_server = os.path.join(PROJECT_ROOT_DIR, request.video_path)
    actual_audio_path_server = os.path.join(PROJECT_ROOT_DIR, request.audio_path)
    if not os.path.exists(actual_video_path_server):
        raise HTTPException(status_code=404, detail=f"Input video not found: {request.video_path}")
    if not os.path.exists(actual_audio_path_server):
        raise HTTPException(status_code=404, detail=f"Input audio not found: {request.audio_path}")
    try:
        base_video_name = os.path.basename(request.video_path)
        name_part, ext_part = os.path.splitext(base_video_name)
        output_filename = f"{name_part}_lipsynced{ext_part}"
        output_path_server = os.path.join(GENERATED_VIDEOS_LIPSYNCED_DIR_SERVER, output_filename)
        output_path_client = os.path.join("data/generated_videos/lipsynced", output_filename)
        shutil.copy(actual_video_path_server, output_path_server)
        print(f"Placeholder lip-synced video (copied) saved to {output_path_server}")
    except Exception as e:
        print(f"Error during placeholder lip sync (copying video): {e}")
        raise HTTPException(status_code=500, detail=f"Failed placeholder lip sync: {str(e)}")
    return {
        "message": "Lip sync applied successfully (placeholder)",
        "lipsynced_video_path": output_path_client
    }

# --- Final Assembly ---
class SFXTrackInput(BaseModel):
    sfx_path: str
    # timing_sec: float = 0.0 # Placeholder, not used by backend yet

class ExportSettingsInput(BaseModel):
    resolution: str
    quality: str
    format: str
    # use_hw_acceleration: bool = True # Conceptual

class AssemblyRequest(BaseModel):
    base_video_path: str # Client-relative path to (ideally) lipsynced video
    speech_audio_path: str # Client-relative path to primary speech audio
    music_audio_path: Optional[str] = None
    sfx_tracks: Optional[List[SFXTrackInput]] = None
    export_settings: ExportSettingsInput

FINAL_VIDEOS_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/final_videos")
os.makedirs(FINAL_VIDEOS_DIR_SERVER, exist_ok=True)

@app.post("/assemble-video")
async def assemble_video(request: AssemblyRequest):
    print("--- Received Video Assembly Request ---")
    print(f"  Base Video: {request.base_video_path}")
    print(f"  Speech Audio: {request.speech_audio_path}")
    if request.music_audio_path:
        print(f"  Music Audio: {request.music_audio_path}")
    if request.sfx_tracks:
        print(f"  SFX Tracks: {[(track.sfx_path) for track in request.sfx_tracks]}") # Simplified logging for now
    print(f"  Export Settings: {request.export_settings.dict()}")
    print("------------------------------------")

    # Validate existence of essential input files
    actual_base_video_path_server = os.path.join(PROJECT_ROOT_DIR, request.base_video_path)
    if not os.path.exists(actual_base_video_path_server):
        raise HTTPException(status_code=404, detail=f"Base video not found: {request.base_video_path}")

    actual_speech_audio_path_server = os.path.join(PROJECT_ROOT_DIR, request.speech_audio_path)
    if not os.path.exists(actual_speech_audio_path_server):
        raise HTTPException(status_code=404, detail=f"Speech audio not found: {request.speech_audio_path}")

    if request.music_audio_path:
        actual_music_audio_path_server = os.path.join(PROJECT_ROOT_DIR, request.music_audio_path)
        if not os.path.exists(actual_music_audio_path_server):
            raise HTTPException(status_code=404, detail=f"Music audio not found: {request.music_audio_path}")

    if request.sfx_tracks:
        for sfx_track in request.sfx_tracks:
            actual_sfx_path_server = os.path.join(PROJECT_ROOT_DIR, sfx_track.sfx_path)
            if not os.path.exists(actual_sfx_path_server):
                raise HTTPException(status_code=404, detail=f"SFX audio not found: {sfx_track.sfx_path}")

    # --- FFmpeg Workflow Placeholder ---
    # 1. Timing and Alignment:
    #    - Speech is assumed to be aligned with base_video_path (e.g., it's from a lipsynced video).
    #    - Music: For placeholder, assume it plays from start to end or matches video duration.
    #    - SFX: Placeholder doesn't use timing_sec. Assume they are overlaid if present.
    print("CONCEPTUAL: Audio timing/alignment would be handled here.")

    # 2. Audio Track Mixing (using pydub or moviepy - conceptual):
    #    - Load speech_audio_path.
    #    - If music_audio_path, load it. Optionally apply ducking.
    #    - If sfx_tracks, load and overlay them at appropriate (currently undefined) times.
    #    - Combine into a master audio track.
    print("CONCEPTUAL: Audio track mixing (speech, music, SFX) would occur here.")

    # 3. Combining Master Audio with Video (using moviepy or ffmpeg - conceptual):
    #    - Take base_video_path (video stream only).
    #    - Set its audio to the newly created master audio track.
    print("CONCEPTUAL: Master audio would be combined with the base video stream here.")

    # 4. Encoding with Export Settings (conceptual):
    #    - Apply request.export_settings (resolution, quality, format).
    print(f"CONCEPTUAL: Encoding to {request.export_settings.format} at {request.export_settings.resolution} with {request.export_settings.quality} quality.")

    # Placeholder: Just copy the base video to the final output location.
    try:
        base_video_name = os.path.basename(request.base_video_path)
        # Ensure a common video extension for the placeholder if format changes
        name_part, _ = os.path.splitext(base_video_name)
        # Make output filename reflect the chosen format for realism, though it's still a copy
        output_format_extension = ".mp4" # Default
        if "webm" in request.export_settings.format.lower():
            output_format_extension = ".webm"

        output_filename = f"final_video_placeholder_{name_part}{output_format_extension}"

        output_path_server = os.path.join(FINAL_VIDEOS_DIR_SERVER, output_filename)
        output_path_client = os.path.join("data/final_videos", output_filename) # Relative path for client

        shutil.copy(actual_base_video_path_server, output_path_server)
        print(f"Placeholder final video (copied from base video) saved to {output_path_server}")
    except Exception as e:
        print(f"Error during placeholder final video assembly (copying video): {e}")
        raise HTTPException(status_code=500, detail=f"Failed placeholder final assembly: {str(e)}")
    # --- End of FFmpeg Workflow Placeholder ---

    return {
        "message": "Video assembled successfully (placeholder)",
        "final_video_path": output_path_client,
        "settings_applied": request.export_settings.dict()
    }

# --- Conceptual Audio Synchronization and Final Assembly Notes (already present) ---
# ... (rest of the file) ...
