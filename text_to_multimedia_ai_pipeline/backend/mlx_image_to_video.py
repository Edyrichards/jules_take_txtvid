# backend/mlx_image_to_video.py
import os
import time
import numpy as np
import mlx.core as mx
from PIL import Image
import cv2 # For compiling frames to video

from . import config_i2v
from . import mlx_animate_diff_utils as ad_utils

# It's common for AnimateDiff to leverage components from a base Stable Diffusion model
# (like VAE, Text Encoder, Tokenizer, and even the UNet which gets augmented by the Motion Module).
# So, we might need to ensure those are loaded or accessible.
# For this placeholder, we'll assume some of these are implicitly available via mlx_utils (SD ones)
# or that AnimateDiff utils would handle their specific versions.
from . import mlx_utils as sd_utils # For VAE, and potentially UNet if not fully self-contained in AD
from . import config_sd # To potentially get SD model path if AD uses its components

_AD_MODELS_LOADED = False
_MOTION_MODULE = None
_SD_UNET_FOR_AD = None # UNet from SD, to be augmented by MotionModule
_SD_VAE_FOR_AD = None  # VAE from SD
# Other components like Text Encoder and Tokenizer from SD would also be needed.
_TOKENIZER_FOR_AD = None
_TEXT_ENCODER_FOR_AD = None
_SCHEDULER_FOR_AD = None


def ensure_ad_models_loaded():
    global _AD_MODELS_LOADED, _MOTION_MODULE, _SD_UNET_FOR_AD, _SD_VAE_FOR_AD
    global _TOKENIZER_FOR_AD, _TEXT_ENCODER_FOR_AD, _SCHEDULER_FOR_AD

    if not _AD_MODELS_LOADED:
        print("Loading AnimateDiff MLX models (placeholder)...")
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        ad_model_abs_path = os.path.join(project_root, config_i2v.MODEL_PATH)
        sd_model_abs_path = os.path.join(project_root, config_sd.MODEL_PATH) # For base SD components

        if not os.path.isdir(ad_model_abs_path):
            os.makedirs(ad_model_abs_path, exist_ok=True) # Create if not exists, similar to SD
            # Raise FileNotFoundError if critical files are missing later, or if user must populate this manually
            print(f"AnimateDiff model directory was created at: {ad_model_abs_path}. It needs to be populated.")

        if not os.path.isdir(sd_model_abs_path): # Also check for SD model path
            # This implies that the Stable Diffusion models (which AnimateDiff might depend on) are also missing.
            # The /generate-image endpoint would also fail.
            raise FileNotFoundError(
               f"Base Stable Diffusion model directory for AnimateDiff not found at: {sd_model_abs_path}. "
               f"AnimateDiff often relies on components from a base SD model. "
               f"Ensure this path is correct in 'config_sd.MODEL_PATH' and models are present."
            )

        try:
            # Load base SD components (reusing from mlx_utils placeholder)
            _TOKENIZER_FOR_AD, _TEXT_ENCODER_FOR_AD, base_sd_unet, base_sd_vae, _SCHEDULER_FOR_AD = sd_utils.load_models(sd_model_abs_path)
            _SD_UNET_FOR_AD = base_sd_unet
            _SD_VAE_FOR_AD = base_sd_vae

            # Load AnimateDiff specific models (Motion Module)
            _MOTION_MODULE = ad_utils.load_animate_diff_models(ad_model_abs_path, _SD_UNET_FOR_AD, _SD_VAE_FOR_AD)

            _AD_MODELS_LOADED = True
            print("AnimateDiff models and associated SD components loaded (simulated by placeholder).")
        except Exception as e:
            raise FileNotFoundError(
                f"Failed to load AnimateDiff or its base SD models. "
                f"Ensure directories exist and are populated: '{ad_model_abs_path}' and '{sd_model_abs_path}'. "
                f"Also ensure 'mlx_utils.py' and 'mlx_animate_diff_utils.py' are correctly set up for your model versions. "
                f"Error: {e}"
            )


def generate_video_frames_with_mlx(input_pil_image: Image.Image, prompt: str, negative_prompt: str = "", num_frames: int = None, fps: int = None):
    ensure_ad_models_loaded()

    if num_frames is None: num_frames = config_i2v.NUM_FRAMES
    # fps is for output video compilation, not directly used in generation loop here usually

    height = config_i2v.IMAGE_HEIGHT # Output video frame height
    width = config_i2v.IMAGE_WIDTH   # Output video frame width
    num_inference_steps = config_sd.NUM_STEPS
    guidance_scale = config_sd.GUIDANCE_SCALE

    print(f"Generating video frames with MLX AnimateDiff (placeholder)...")
    print(f"  Input image size (used for conditioning, if any): {input_pil_image.width}x{input_pil_image.height}")
    print(f"  Output video frame size: {width}x{height}")
    print(f"  Prompt: {prompt}")
    print(f"  Num Frames: {num_frames}, Target Output FPS: {fps if fps else config_i2v.FPS}")

    # 1. Preprocess input image (conceptual, not used in this placeholder's diffusion)
    # In a real pipeline, the input_pil_image might be encoded to latents to condition the start of the video.
    # For this placeholder, we are starting from pure noise for all frames.
    print(f"  Input image conceptually processed. Starting video from noise.")

    # 2. Tokenize prompts
    cfg_prompts = [negative_prompt if negative_prompt else "", prompt]
    text_inputs = _TOKENIZER_FOR_AD(cfg_prompts, padding="max_length", max_length=77, truncation=True, return_tensors="np")
    text_input_ids = mx.array(text_inputs["input_ids"])
    text_embeddings = _TEXT_ENCODER_FOR_AD(text_input_ids)

    if guidance_scale > 1.0:
        uncond_embeddings, cond_embeddings = mx.split(text_embeddings, 2)
    else: # Should not happen if guidance_scale has a default > 1
        uncond_embeddings = _TEXT_ENCODER_FOR_AD(_TOKENIZER_FOR_AD([""], padding="max_length", max_length=77, truncation=True, return_tensors="mx")["input_ids"])
        cond_embeddings = text_embeddings[0:1] # Take only the prompt embedding

    # 3. Prepare latents for video (num_frames) - starting from pure noise
    video_latents_shape = (1, num_frames, 4, height // 8, width // 8) # B, F, C, H_lat, W_lat
    current_latents_video = mx.random.normal(video_latents_shape)

    # 4. Denoising loop for video frames
    _SCHEDULER_FOR_AD.set_timesteps(num_inference_steps)
    timesteps = _SCHEDULER_FOR_AD.timesteps

    print(f"Starting video denoising loop for {len(timesteps)} timesteps, generating {num_frames} frames...")
    for i, t in enumerate(timesteps):
        # print(f"  Video Step {i+1}/{len(timesteps)}, Timestep: {t.item()}") # Verbose

        batch_size_frames = current_latents_video.shape[0] * current_latents_video.shape[1] # B * F = 1 * num_frames
        input_latents_flat = current_latents_video.reshape(batch_size_frames, current_latents_video.shape[2], current_latents_video.shape[3], current_latents_video.shape[4])

        # Text embeddings need to be (batch_size_frames, seq_len, embed_dim) for the UNet
        # Current cond_embeddings and uncond_embeddings are (1, seq_len, embed_dim)
        current_cond_embeddings_repeated = mx.repeat(cond_embeddings, repeats=num_frames, axis=0)
        current_uncond_embeddings_repeated = mx.repeat(uncond_embeddings, repeats=num_frames, axis=0) if uncond_embeddings is not None else None

        if guidance_scale > 1.0 and current_uncond_embeddings_repeated is not None:
            latent_model_input = mx.concatenate([input_latents_flat] * 2) # Double batch for CFG
            timestep_input = mx.broadcast_to(t, (batch_size_frames * 2,))
            # Text embeddings for UNet: [unconditional repeated for all frames, conditional repeated for all frames]
            current_text_embeds_unet = mx.concatenate([current_uncond_embeddings_repeated, current_cond_embeddings_repeated])
        else:
            latent_model_input = input_latents_flat
            timestep_input = mx.broadcast_to(t, (batch_size_frames,))
            current_text_embeds_unet = current_cond_embeddings_repeated

        # Placeholder UNet (from SD utils) is called. MotionModule interaction is abstracted.
        # In a real AnimateDiff, MotionModule's features are injected inside the UNet.
        # For this placeholder, _MOTION_MODULE is loaded but not explicitly called here,
        # assuming its effect is part of the conceptual _SD_UNET_FOR_AD if it were a real model.
        noise_pred_flat = _SD_UNET_FOR_AD(latent_model_input, timestep_input, current_text_embeds_unet)

        if guidance_scale > 1.0 and current_uncond_embeddings_repeated is not None:
            noise_pred_uncond_flat, noise_pred_text_flat = mx.split(noise_pred_flat, 2)
            noise_pred_flat = noise_pred_uncond_flat + guidance_scale * (noise_pred_text_flat - noise_pred_uncond_flat)

        scheduler_output = _SCHEDULER_FOR_AD.step(noise_pred_flat, t, input_latents_flat)
        processed_latents_flat = scheduler_output["pred_original_sample"]
        current_latents_video = processed_latents_flat.reshape(current_latents_video.shape)

    print("Video denoising loop finished (placeholder).")
    mx.eval(current_latents_video)

    # 5. Decode each frame's latents using VAE
    generated_frames_pil = []
    print(f"Decoding {num_frames} video frames using VAE (placeholder)...")
    for frame_idx in range(num_frames):
        latent_frame = current_latents_video[:, frame_idx, :, :, :]
        latent_frame = (1 / 0.18215) * latent_frame # VAE scaling (use actual from config if different)

        image_frame_tensor = _SD_VAE_FOR_AD.decode(latent_frame)
        mx.eval(image_frame_tensor)

        image_np = np.array(image_frame_tensor * 0.5 + 0.5, copy=False)
        image_np = np.clip(image_np, 0, 1)
        image_np = (image_np * 255).astype(np.uint8)

        if image_np.shape[0] == 1: image_np = image_np[0]
        if image_np.shape[0] == 3: image_np = image_np.transpose(1, 2, 0)

        pil_frame = Image.fromarray(image_np)
        generated_frames_pil.append(pil_frame)

    print("All video frames decoded.")
    return generated_frames_pil


def compile_frames_to_video(frames_pil: list, output_path_server: str, fps: int):
    if not frames_pil:
        raise ValueError("Frame list is empty, cannot compile video.")

    first_frame_np = np.array(frames_pil[0].convert("RGB"))
    height, width, _ = first_frame_np.shape # Get dimensions from first frame

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path_server, fourcc, fps, (width, height))

    if not video_writer.isOpened():
        raise IOError(f"Could not open video writer for path: {output_path_server}")

    print(f"Compiling {len(frames_pil)} frames into video at {output_path_server} with FPS={fps}...")
    for frame_pil in frames_pil:
        frame_bgr = cv2.cvtColor(np.array(frame_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        video_writer.write(frame_bgr)

    video_writer.release()
    print("Video compilation complete.")


if __name__ == "__main__":
    print("Testing MLX AnimateDiff video generation (placeholder version)...")

    # Path adjustments for standalone execution from 'backend/' directory
    original_i2v_model_path = config_i2v.MODEL_PATH
    adjusted_i2v_model_path = os.path.join("..", original_i2v_model_path)
    if not os.path.exists(config_i2v.MODEL_PATH) and os.path.exists(adjusted_i2v_model_path):
        # This is tricky; ensure_ad_models_loaded uses config_i2v.MODEL_PATH directly.
        # For a true standalone test, one might need to set an environment variable or pass path.
        # The current ensure_ad_models_loaded logic will construct path from project root.
        pass

    original_sd_model_path = config_sd.MODEL_PATH
    adjusted_sd_model_path = os.path.join("..", original_sd_model_path)
    if not os.path.exists(config_sd.MODEL_PATH) and os.path.exists(adjusted_sd_model_path):
        pass

    try:
        dummy_input_image = Image.new("RGB", (config_i2v.IMAGE_WIDTH, config_i2v.IMAGE_HEIGHT), color="purple")
        test_prompt = "A purple square pulsating"

        start_time = time.time()
        # ensure_ad_models_loaded() # Called by generate_video_frames_with_mlx
        frames = generate_video_frames_with_mlx(dummy_input_image, test_prompt)
        compilation_start_time = time.time()
        if frames:
            test_output_dir = os.path.join("..", "data", "generated_videos") # Save in project's data folder
            os.makedirs(test_output_dir, exist_ok=True)
            video_save_path = os.path.join(test_output_dir, "test_i2v_mlx_placeholder.mp4")
            compile_frames_to_video(frames, video_save_path, config_i2v.FPS)
            print(f"Test video saved to {video_save_path}")
        end_time = time.time()
        print(f"Test video generation total time: {end_time - start_time:.2f}s (Frames gen: {compilation_start_time-start_time:.2f}s, Compile: {end_time-compilation_start_time:.2f}s)")
    except Exception as e:
        print(f"Error during standalone AnimateDiff test: {e}")
        import traceback
        traceback.print_exc()
