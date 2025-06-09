# backend/config_sd.py
# Configuration for MLX Stable Diffusion

# Path to the directory containing the MLX-converted Stable Diffusion model components
# (e.g., unet.safetensors, vae.safetensors, text_encoder.safetensors, tokenizer_config.json, etc.)
# User will need to download/convert these and place them here.
MODEL_PATH = "models/stable_diffusion_mlx" # Relative to project root (text_to_multimedia_ai_pipeline/)

# Default parameters for image generation
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
NUM_STEPS = 20  # Number of denoising steps (can be 20-50 for reasonable quality)
GUIDANCE_SCALE = 7.5  # How much the prompt should guide generation
OUTPUT_IMAGE_FORMAT = "PNG" # "JPEG" or "PNG"
