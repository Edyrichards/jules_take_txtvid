# backend/mlx_stable_diffusion.py
import os
import time
import numpy as np
import mlx.core as mx
from PIL import Image

from . import config_sd # Use . for relative import within package
from . import mlx_utils # Use . for relative import

# Ensure MPS is the default device for MLX operations
# This should ideally be set once at the application startup,
# but setting it here ensures it's attempted before model loading.
try:
    mx.set_default_device(mx.Device.mps)
    print("MLX default device set to MPS.")
except Exception as e:
    print(f"Could not set MLX default device to MPS: {e}. Will try to proceed with default.")


# --- Model Loading ---
# This is a global variable to hold the loaded models to avoid reloading on every call.
# In a real multi-user FastAPI app, you'd need a more robust way to manage this,
# perhaps with a class or application lifespan events.
_MODELS_LOADED = False
_TOKENIZER = None
_TEXT_ENCODER = None
_UNET = None
_VAE = None
_SCHEDULER = None

def ensure_models_loaded():
    global _MODELS_LOADED, _TOKENIZER, _TEXT_ENCODER, _UNET, _VAE, _SCHEDULER
    if not _MODELS_LOADED:
        print("Loading Stable Diffusion models for MLX...")
        # Construct absolute path for models if MODEL_PATH is relative to project root
        # Assuming backend/main.py is in text_to_multimedia_ai_pipeline/backend/
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        model_abs_path = os.path.join(project_root, config_sd.MODEL_PATH)

        if not os.path.isdir(model_abs_path):
            # Attempt to create the directory if it's missing, as per user instructions for other dirs
            print(f"Model directory {model_abs_path} not found. Attempting to create it.")
            os.makedirs(model_abs_path, exist_ok=True)
            # However, if the directory is empty, it's still an issue.
            # The FileNotFoundError below will be more specific if it remains empty or critical files are missing.
            # This creation step is more for consistency with other directory creations.
            # The user is ultimately responsible for populating it.
            # Raise a more informative error if essential files are missing after trying to load.

        try:
            _TOKENIZER, _TEXT_ENCODER, _UNET, _VAE, _SCHEDULER = mlx_utils.load_models(model_abs_path)
            _MODELS_LOADED = True
            print("Stable Diffusion models loaded (simulated by placeholder).")
        except Exception as e:
            # Catch any error during model loading (e.g., if files are missing despite dir existing)
            raise FileNotFoundError(
                f"Failed to load MLX Stable Diffusion models from: {model_abs_path}. "
                f"Ensure the directory exists, is populated with converted model files, and "
                f"that 'mlx_utils.py' reflects the correct loading logic for your model version. "
                f"Error: {e}"
            )
    # else:
        # print("Stable Diffusion models already loaded.")


def generate_image_with_mlx(prompt: str, negative_prompt: str = "", num_steps: int = None, guidance_scale: float = None):
    ensure_models_loaded() # This will raise FileNotFoundError if models can't be loaded

    if num_steps is None:
        num_steps = config_sd.NUM_STEPS
    if guidance_scale is None:
        guidance_scale = config_sd.GUIDANCE_SCALE

    height = config_sd.IMAGE_HEIGHT
    width = config_sd.IMAGE_WIDTH

    print(f"Generating image with MLX Stable Diffusion...")
    print(f"  Prompt: {prompt}")
    print(f"  Negative Prompt: {negative_prompt}")
    print(f"  Steps: {num_steps}, Guidance: {guidance_scale}, Size: {width}x{height}")

    # 1. Tokenize prompts
    prompts = [prompt]
    if negative_prompt:
        cfg_prompts = [negative_prompt, prompt]
    else:
        cfg_prompts = ["", prompt]

    text_inputs = _TOKENIZER(cfg_prompts, padding="max_length", max_length=77, truncation=True, return_tensors="np")
    text_input_ids = mx.array(text_inputs["input_ids"])

    # 2. Get text embeddings
    text_embeddings = _TEXT_ENCODER(text_input_ids)

    if guidance_scale > 1.0:
        uncond_embeddings, cond_embeddings = mx.split(text_embeddings, 2)
    else:
        uncond_embeddings = None
        cond_embeddings = text_embeddings[1:2] if negative_prompt else text_embeddings[0:1]

    # 3. Prepare latents
    latents_shape = (1, 4, height // 8, width // 8)
    latents = mx.random.normal(latents_shape)

    # 4. Denoising loop
    _SCHEDULER.set_timesteps(num_steps)
    timesteps = _SCHEDULER.timesteps

    print(f"Starting denoising loop for {len(timesteps)} timesteps...")
    for i, t in enumerate(timesteps):
        # print(f"  Step {i+1}/{len(timesteps)}, Timestep: {t.item()}") # Can be too verbose

        if guidance_scale > 1.0 and uncond_embeddings is not None:
            latent_model_input = mx.concatenate([latents] * 2)
            timestep_input = mx.broadcast_to(t, (2,))
            current_text_embeddings = mx.concatenate([uncond_embeddings, cond_embeddings])
        else:
            latent_model_input = latents
            timestep_input = t
            current_text_embeddings = cond_embeddings

        noise_pred = _UNET(latent_model_input, timestep_input, current_text_embeddings)

        if guidance_scale > 1.0 and uncond_embeddings is not None:
            noise_pred_uncond, noise_pred_text = mx.split(noise_pred, 2)
            noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

        # Ensure scheduler_output is a dictionary and get the sample
        scheduler_output = _SCHEDULER.step(noise_pred, t, latents)
        latents = scheduler_output["pred_original_sample"] # Accessing by key

    print("Denoising loop finished.")
    mx.eval(latents)

    # 5. Decode latents to image
    latents = (1 / 0.18215) * latents
    image = _VAE.decode(latents)
    mx.eval(image)
    print("Image decoded by VAE (simulated).")

    # 6. Post-process image
    image_np = np.array(image * 0.5 + 0.5, copy=False)
    image_np = np.clip(image_np, 0, 1)
    image_np = (image_np * 255).astype(np.uint8)

    if image_np.shape[0] == 1:
        image_np = image_np[0]

    if image_np.shape[0] == 3:
        image_np = image_np.transpose(1, 2, 0)

    pil_image = Image.fromarray(image_np)
    print("Image post-processed and converted to PIL Image.")

    return pil_image

if __name__ == "__main__":
    print("Testing MLX Stable Diffusion generation (placeholder version)...")

    # Adjust MODEL_PATH for standalone test if it's project-root relative
    # This script is in backend/, so MODEL_PATH needs to be relative to backend/ or absolute
    # config_sd.MODEL_PATH is "models/stable_diffusion_mlx" (project root relative)
    # So from backend/, it should be "../models/stable_diffusion_mlx"

    original_model_path = config_sd.MODEL_PATH
    adjusted_model_path = os.path.join("..", original_model_path)

    if not os.path.exists(config_sd.MODEL_PATH) and os.path.exists(adjusted_model_path):
        # This modification of config_sd.MODEL_PATH is temporary for this test block
        # A better way would be to pass the path to ensure_models_loaded if it differs
        print(f"Original MODEL_PATH '{config_sd.MODEL_PATH}' not found from 'backend/' directory.")
        print(f"Temporarily trying adjusted path for standalone test: '{adjusted_model_path}'")
        # For the purpose of this __main__ block, we can't directly change config_sd.MODEL_PATH
        # in a way that ensure_models_loaded() will see without re-importing or passing directly.
        # Instead, ensure_models_loaded() itself constructs the path relative to its own location.
        # The current ensure_models_loaded() logic should correctly find it if MODEL_PATH is project-relative.
        pass # ensure_models_loaded() handles path construction from project root

    try:
        test_prompt = "A red apple on a wooden table, photorealistic"
        start_time = time.time()
        # Forcing ensure_models_loaded here to catch errors if path is wrong for standalone
        ensure_models_loaded()
        img = generate_image_with_mlx(test_prompt) # This will call ensure_models_loaded again if not for the global
        end_time = time.time()

        # Create a 'generated_test_images' directory if it doesn't exist
        # This is for the output of this standalone test script.
        test_output_dir = "generated_test_images"
        os.makedirs(test_output_dir, exist_ok=True)
        test_image_path = os.path.join(test_output_dir, "test_generated_image_mlx.png")

        img.save(test_image_path)
        print(f"Test image saved to {test_image_path} (Execution time: {end_time - start_time:.2f}s)")
    except Exception as e:
        print(f"Error during standalone test: {e}")
        import traceback
        traceback.print_exc()
