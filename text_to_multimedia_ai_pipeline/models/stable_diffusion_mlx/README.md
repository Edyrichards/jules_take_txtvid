# MLX Stable Diffusion Model Files

This directory is intended to store the MLX-compatible Stable Diffusion model components.
To use the text-to-image generation feature of the application, you need to:

1.  **Download or Convert a Stable Diffusion Model to MLX Format:**
    *   You can find scripts and instructions for converting standard PyTorch Stable Diffusion checkpoints (e.g., from Hugging Face) to MLX format in the official Apple MLX examples repository: [https://github.com/ml-explore/mlx-examples/tree/main/stable_diffusion](https://github.com/ml-explore/mlx-examples/tree/main/stable_diffusion)
    *   Commonly, you'll need to convert/obtain:
        *   UNet model (e.g., `unet.safetensors`)
        *   VAE (Variational Autoencoder) model (e.g., `vae.safetensors` or `vae_decoder.safetensors`, `vae_encoder.safetensors`)
        *   Text Encoder model (e.g., `text_encoder.safetensors`)
        *   Tokenizer configuration files (e.g., `tokenizer_config.json`, `vocab.json`, `merges.txt` or similar, often bundled as `tokenizer.json` or within a `tokenizer` subfolder).
        *   Scheduler configuration (though the scheduler logic is often part of the pipeline code itself).

2.  **Quantize the Model (Recommended for M2):**
    *   The MLX examples often include scripts for quantizing the model components (e.g., to 4-bit or 8-bit precision). This significantly reduces memory usage and can improve speed on Apple Silicon. Follow the instructions in the MLX examples for quantization.

3.  **Place Files in This Directory:**
    *   Once converted and (optionally) quantized, place all the `.safetensors` files and tokenizer files directly into this `stable_diffusion_mlx` directory.
    *   The application's backend (`config_sd.py`) is currently configured to look for models in `models/stable_diffusion_mlx/`.

**Example File Structure (might vary based on exact SD version and conversion script):**
```
models/
└── stable_diffusion_mlx/
    ├── unet.safetensors
    ├── vae.safetensors
    ├── text_encoder.safetensors
    ├── tokenizer_config.json
    ├── vocab.json
    ├── merges.txt
    └── (other potential files like added_tokens.json, special_tokens_map.json)
```

**Note:** The Python code (`backend/mlx_utils.py`) that loads these components is currently a **placeholder**. You will need to replace its content with the actual model loading and pipeline logic from a working MLX Stable Diffusion example that matches the model files you've prepared. The placeholder `mlx_utils.py` defines the class structures (like `PlaceholderUNet`) but does not implement their full functionality or weight loading. The provided `mlx_stable_diffusion.py` attempts to use these placeholders.
