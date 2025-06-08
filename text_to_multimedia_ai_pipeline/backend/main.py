from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from PIL import Image # For dummy image
import io
from fastapi.responses import FileResponse # Required for returning files
import cv2 # For OpenCV
import shutil # For file operations (though not used in Option B directly)

app = FastAPI()

# --- Project Root Path (for resolving relative paths from client) ---
# The /app directory is the root in the sandbox.
# Files are stored in /app/text_to_multimedia_ai_pipeline/data/...
PROJECT_ROOT_DIR = "/app/text_to_multimedia_ai_pipeline"

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ImagePrompt(BaseModel):
    prompt: str

# Ensure 'data/generated_images' directory exists (server-side path)
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
        # Server-side path for saving the image
        image_path_on_server = os.path.join(GENERATED_IMAGES_DIR_SERVER, image_filename)

        with open(image_path_on_server, "wb") as f:
            f.write(img_byte_arr.getvalue())
        print(f"Placeholder image saved to {image_path_on_server}")

        print("Placeholder: Upscaling would be applied here (e.g., with Real-ESRGAN) if an upscaler was integrated.")
        upscaling_status_message = "pending_integration"
        base_resolution = "512x512"

        # Client-accessible path (relative to project root)
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

# --- Video Generation ---
class VideoRequest(BaseModel):
    image_path: str # Relative path from project root, e.g., "data/generated_images/placeholder.png"
    motion_type: str

# Ensure 'data/generated_videos' directory exists (server-side path)
GENERATED_VIDEOS_DIR_SERVER = os.path.join(PROJECT_ROOT_DIR, "data/generated_videos")
os.makedirs(GENERATED_VIDEOS_DIR_SERVER, exist_ok=True)

@app.post("/generate-video")
async def generate_video(request: VideoRequest):
    print(f"Received video request: image_path='{request.image_path}', motion_type='{request.motion_type}'")

    # Convert client-provided relative image_path to an absolute server-side path
    actual_image_path_on_server = os.path.join(PROJECT_ROOT_DIR, request.image_path)

    if not os.path.exists(actual_image_path_on_server):
        print(f"Error: Input image not found at {actual_image_path_on_server}")
        raise HTTPException(status_code=404, detail=f"Input image not found: {request.image_path}")

    # --- AnimateDiff/MLX Placeholder ---
    # TODO: Load AnimateDiff model using MLX
    # TODO: Process image and motion_type to generate video frames
    # For now, creating a placeholder video from the image:
    output_video_filename = "placeholder_video.mp4"
    # Server-side path for saving the video
    output_video_path_on_server = os.path.join(GENERATED_VIDEOS_DIR_SERVER, output_video_filename)

    try:
        img_cv = cv2.imread(actual_image_path_on_server)
        if img_cv is None:
            # This can happen if the image file is corrupted or not a valid image format for OpenCV
            print(f"Error: cv2.imread failed to load image from {actual_image_path_on_server}")
            raise HTTPException(status_code=500, detail=f"Could not read image data from {request.image_path} using OpenCV.")

        height, width, _ = img_cv.shape # Don't need layers
        fps = 1
        duration_seconds = 1
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        video_writer = cv2.VideoWriter(output_video_path_on_server, fourcc, fps, (width, height))
        if not video_writer.isOpened():
            # This can happen if there are issues with codec or permissions
            print(f"Error: cv2.VideoWriter failed to open for path {output_video_path_on_server}")
            raise HTTPException(status_code=500, detail="Failed to initialize video writer.")

        for _ in range(fps * duration_seconds):
            video_writer.write(img_cv)
        video_writer.release()
        print(f"Placeholder video saved to {output_video_path_on_server}")

        # --- Post-processing Placeholders ---
        print("Placeholder: Frame interpolation (e.g., RIFE) would be applied here for smoothness if integrated.")
        frame_interpolation_status = "pending_integration"
        print("Placeholder: Video upscaling (e.g., lightweight video ESRGAN) would be applied here if integrated.")
        video_upscaling_status = "pending_integration"
        # --- End of Post-processing Placeholders ---

    except Exception as e:
        print(f"Error generating placeholder video with OpenCV: {e}")
        # Raise HTTPException to ensure a proper JSON error response is sent to the client
        raise HTTPException(status_code=500, detail=f"Failed to create placeholder video: {str(e)}")
    # --- End of AnimateDiff Placeholder ---

    # Client-accessible path (relative to project root)
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
