from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from PIL import Image # For dummy image
import io
from fastapi.responses import FileResponse # Required for returning files
import cv2 # For OpenCV
import shutil # For file operations (though not used in Option B directly)
import wave # For placeholder speech/music/sfx audio

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

@app.post("/generate-image")
async def generate_image(prompt_data: ImagePrompt):
    prompt = prompt_data.prompt
    print(f"Received prompt: {prompt}")
    try:
        img = Image.new('RGB', (512, 512), color = 'blue')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        image_filename = "placeholder_image.png"
        image_path_on_server = os.path.join(GENERATED_IMAGES_DIR_SERVER, image_filename)
        with open(image_path_on_server, "wb") as f:
            f.write(img_byte_arr.getvalue())
        print(f"Placeholder image saved to {image_path_on_server}")
        print("Placeholder: Upscaling would be applied here (e.g., with Real-ESRGAN) if an upscaler was integrated.")
        upscaling_status_message = "pending_integration"
        base_resolution = "512x512"
        client_accessible_image_path = os.path.join("data/generated_images", image_filename)
        return {
            "message": "Image generated successfully (placeholder)",
            "image_path": client_accessible_image_path,
            "resolution": base_resolution,
            "upscaling_status": upscaling_status_message
        }
    except Exception as e:
        print(f"Error generating placeholder image: {e}")
        raise HTTPException(status_code=500, detail=f"Error in image generation: {str(e)}")

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

# --- Sound Effects (SFX) Generation ---
class SFXRequest(BaseModel):
    category: str
    description: str

GENERATED_AUDIO_SFX_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_audio/sfx")
os.makedirs(GENERATED_AUDIO_SFX_DIR_SERVER, exist_ok=True)

@app.post("/generate-sfx")
async def generate_sfx(request: SFXRequest):
    print(f"Received SFX request: category='{request.category}', description='{request.description[:50]}...'")

    # --- AudioLDM / MLX or Library Lookup Placeholder ---
    # TODO: Load AudioLDM model or implement SFX library lookup
    # For now, creating a short placeholder silent WAV file:
    output_filename = "placeholder_sfx.wav"
    output_path_server = os.path.join(GENERATED_AUDIO_SFX_DIR_SERVER, output_filename)
    output_path_client = os.path.join("data/generated_audio/sfx", output_filename) # Relative path for client

    sfx_duration = 0.5 # seconds

    try:
        with wave.open(output_path_server, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(44100)  # CD quality
            # Calculate total frames for the given duration
            num_frames_sfx = int(44100 * sfx_duration)
            # Create silent frame data
            silent_frame_sfx = b'\x00\x00'
            frames_data_sfx = silent_frame_sfx * num_frames_sfx
            wf.writeframes(frames_data_sfx)
        print(f"Placeholder SFX audio saved to {output_path_server} (Duration: {sfx_duration}s)")
        print(f"Concept: For SFX '{request.description}' in category '{request.category}'. Future: AudioLDM or library lookup.")
    except Exception as e:
        print(f"Error generating placeholder SFX audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create placeholder SFX audio: {str(e)}")
    # --- End of SFX Placeholder ---

    return {
        "message": "SFX generated successfully (placeholder)",
        "audio_path": output_path_client,
        "category_used": request.category,
        "description_logged": request.description
    }
