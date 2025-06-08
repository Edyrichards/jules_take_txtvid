from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from PIL import Image # For dummy image
import io
from fastapi.responses import FileResponse # Required for returning files

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ImagePrompt(BaseModel):
    prompt: str

# Ensure 'data/generated_images' directory exists
# Corrected path to be relative to the /app directory where the script runs
GENERATED_IMAGES_DIR = "/app/text_to_multimedia_ai_pipeline/data/generated_images"
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

@app.post("/generate-image")
async def generate_image(prompt_data: ImagePrompt):
    prompt = prompt_data.prompt
    print(f"Received prompt: {prompt}")

    # --- MLX Model Loading and Inference Placeholder ---
    # TODO: Load MLX Stable Diffusion model
    # TODO: Preprocess prompt for the model
    # TODO: Generate image using MLX model
    # For now, creating a placeholder image:
    try:
        img = Image.new('RGB', (512, 512), color = 'blue')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        image_filename = "placeholder_image.png"
        image_path_on_server = os.path.join(GENERATED_IMAGES_DIR, image_filename)

        with open(image_path_on_server, "wb") as f:
            f.write(img_byte_arr.getvalue())

        print(f"Placeholder image saved to {image_path_on_server}")
        # --- End of MLX Placeholder ---

        # --- Upscaling Placeholder ---
        print("Placeholder: Upscaling would be applied here (e.g., with Real-ESRGAN) if an upscaler was integrated.")
        upscaling_status_message = "pending_integration"
        base_resolution = "512x512" # Assuming this is the base generation size
        # --- End of Upscaling Placeholder ---

        # Return the path relative to the project root for client access
        client_accessible_path = os.path.join("data/generated_images", image_filename)
        return {
            "message": "Image generated successfully (placeholder)",
            "image_path": client_accessible_path, # Path for client
            "resolution": base_resolution,
            "upscaling_status": upscaling_status_message
        }
    except Exception as e:
        print(f"Error generating placeholder image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
