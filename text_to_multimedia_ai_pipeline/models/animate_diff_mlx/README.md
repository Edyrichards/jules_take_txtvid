# MLX AnimateDiff Model Files

This directory is intended to store the MLX-compatible AnimateDiff model components, particularly the **Motion Module**, and any other specific files required by your chosen MLX AnimateDiff implementation.

AnimateDiff typically works by augmenting an existing Stable Diffusion (SD) model. Therefore, the image-to-video pipeline will also rely on the SD model components (UNet, VAE, Text Encoder, Tokenizer) that you set up in `models/stable_diffusion_mlx/`.

To use the image-to-video generation feature, you need to:

1.  **Obtain an MLX-Compatible Motion Module:**
    *   The core component of AnimateDiff is the Motion Module. You will need to find or convert a Motion Module to the MLX format (usually `.safetensors`).
    *   Check official or community MLX resources and AnimateDiff repositories for MLX-ported versions of Motion Modules. These might be trained for specific base SD models (e.g., SD 1.5).

2.  **Understand Model Compatibility:**
    *   Ensure the Motion Module you obtain is compatible with the base Stable Diffusion model components (UNet, VAE) you have set up in `models/stable_diffusion_mlx/`. Some Motion Modules are designed to work with specific versions or fine-tunes of SD.

3.  **Place Motion Module File(s) in This Directory:**
    *   Place the MLX-compatible Motion Module file(s) (e.g., `motion_module.safetensors`) directly into this `animate_diff_mlx` directory.
    *   The application's backend (`config_i2v.py`) is currently configured to look for AnimateDiff specific models in `models/animate_diff_mlx/`. The `mlx_animate_diff_utils.py` (which you need to implement) will load them from here.

4.  **Implement `backend/mlx_animate_diff_utils.py`:**
    *   As with Stable Diffusion, the file `backend/mlx_animate_diff_utils.py` currently contains **placeholder classes and functions**.
    *   **You MUST replace its content with the actual Python class definition for the Motion Module and the logic to load its weights.**
    *   This implementation should also handle how the Motion Module integrates with the Stable Diffusion UNet. Often, the Motion Module's layers are injected into or wrapped around parts of the SD UNet's forward pass. Your `mlx_animate_diff_utils.py` will need to reflect this integration.

**Example File Structure (Conceptual):**
```
models/
├── stable_diffusion_mlx/
│   ├── unet.safetensors
│   ├── vae.safetensors
│   └── ... (other SD files)
└── animate_diff_mlx/
    └── motion_module.safetensors
    └── (any other AnimateDiff specific files, if applicable)
```

**Note on `backend/mlx_image_to_video.py`:**
The pipeline logic in `backend/mlx_image_to_video.py` orchestrates the frame generation process. It assumes that the `mlx_animate_diff_utils.py` (once you implement it) correctly provides a functional Motion Module and handles its integration with the SD UNet. The frame generation loop in `mlx_image_to_video.py` might need adjustments depending on the specifics of your chosen AnimateDiff MLX implementation.
