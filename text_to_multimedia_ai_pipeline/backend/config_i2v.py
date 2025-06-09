# backend/config_i2v.py
# Configuration for MLX Image-to-Video (conceptually AnimateDiff)

# Path to the directory containing the MLX-converted AnimateDiff model components
# (e.g., motion_module.safetensors, and potentially its own UNet, VAE if different from SD)
# User will need to download/convert these and place them here.
MODEL_PATH = "models/animate_diff_mlx" # Relative to project root

# Default parameters for video generation
NUM_FRAMES = 16 # Number of frames to generate for the video
FPS = 8         # Frames per second for the output video
IMAGE_WIDTH = 512 # Should ideally match the input image or be configurable
IMAGE_HEIGHT = 512
OUTPUT_VIDEO_FORMAT = "MP4"
