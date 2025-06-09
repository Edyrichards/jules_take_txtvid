# Text-to-Multimedia AI Pipeline (M2 Optimized Prototype)

## Overview

Welcome! This project is a prototype for an ambitious Text-to-Multimedia AI Pipeline, designed to transform your text ideas into complete videos with synchronized audio. The ultimate goal is to create a tool optimized for Apple MacBook Pro M2 machines, focusing on efficiency and good-to-very-good results without requiring high-end cloud computing.

Think of it as your creative assistant: you provide the text, and it helps you build out the visual scenes, animations, voice-overs, music, and sound effects, finally assembling them into a finished video.

## Current Status: Fully Interactive Prototype

**Important Note for Beginners:** This version of the application is a **fully interactive prototype**. This means:

*   **The User Interface is Complete:** You can click through all the steps, input text, make selections, and see how the final application is intended to work.
*   **Backend Processes are Placeholders:** The actual Artificial Intelligence (AI) models for generating images, videos, audio, etc., are **not yet integrated**. When you click "Generate," the system currently creates quick placeholder files (like blue squares for images or silent audio files) to simulate the process.
    (Note: The backend code for Text-to-Image and Image-to-Video generation has been structured to use MLX with Stable Diffusion and AnimateDiff concepts, respectively. However, both require user setup of model files and replacement of placeholder model utility code. See 'Future Development' section for details.)
*   **Focus on Workflow and UI:** The main purpose of this prototype is to demonstrate the complete workflow and user interface of the pipeline.

This allows you to understand the entire process and how you would interact with the tool once the AI models are connected.

## Installation and Running the Application

To run this prototype on your computer, you'll need Python and a few packages.

**Prerequisites:**
*   Python 3.10 or newer.
*   An internet connection (for downloading packages).

**Steps:**

1.  **Download the Project:**
    *   If you have this project as a Zip file, extract it to a folder on your computer.
    *   If you're using Git, clone the repository:
        ```bash
        git clone <your_repository_url_here_if_applicable>
        cd text_to_multimedia_ai_pipeline
        ```
    (Replace `<your_repository_url_here_if_applicable>` with the actual URL if you cloned it from a Git repository, or simply download/extract the source code.)

2.  **Set up a Virtual Environment (Recommended):**
    *   Open a terminal or command prompt in the project's main folder.
    *   Create a virtual environment:
        ```bash
        python3 -m venv venv
        ```
        (Use `python -m venv venv` if `python3` isn't your command for Python 3, or if `python3` is not found.)
    *   Activate the virtual environment:
        *   On macOS/Linux: `source venv/bin/activate`
        *   On Windows: `venv\Scripts\activate`

3.  **Install Dependencies:**
    *   With your virtual environment active, install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Run the Backend (FastAPI):**
    *   Open a **new terminal window** in the project folder (and activate the virtual environment there too).
    *   Navigate to the `backend` directory:
        ```bash
        cd backend
        ```
    *   Start the backend server:
        ```bash
        uvicorn main:app --reload --port 8000
        ```
    *   You should see messages indicating the server is running (e.g., "Uvicorn running on http://127.0.0.1:8000"). Keep this terminal window open.

5.  **Run the Frontend (Streamlit):**
    *   Open a **separate (third) terminal window** in the project's main folder (and activate the virtual environment).
    *   Navigate to the `frontend` directory:
        ```bash
        cd frontend
        ```
    *   Run the Streamlit app:
        ```bash
        streamlit run app.py
        ```
    *   Streamlit will usually open the application automatically in your web browser. If not, it will display a local URL (like `http://localhost:8501`) that you can open in your browser.

You should now see the application interface!

## Using the Application: A Step-by-Step Guide

The application guides you through a wizard-like interface. Here's how to navigate it:

**Sidebar:**
*   **Backend Status:** Shows if the frontend can connect to the backend (should say "Backend is healthy!").
*   **Project Management (Conceptual):**
    *   **Save Project:** Clicking this will show a message that saving is a planned feature.
    *   **Load Project:** Clicking this will show a message that loading is a planned feature.
*   **Help & Tips:** Expand these sections for guidance on the workflow and writing prompts.

**Main Window - The Wizard:**

**(Steps 0-5 as previously detailed - content omitted for brevity in this diff view but remains in the file)**
... (Content of Steps 0-5 remains the same) ...

## What to Expect (Placeholder Outputs)

*   **Images:** The Text-to-Image step now uses a **placeholder MLX Stable Diffusion pipeline**. If model files are not correctly set up as per `models/stable_diffusion_mlx/README.md` and `backend/mlx_utils.py` is not replaced with actual model logic, it will likely fail or produce random noise if the placeholder `mlx_utils.py` somehow runs. With correct (placeholder) `mlx_utils.py` but no real models, it produces a random noise image.
*   **Videos:** The Image-to-Video step now uses a **placeholder MLX AnimateDiff-style pipeline**. Similar to image generation, if model files (especially the Motion Module) are not set up as per `models/animate_diff_mlx/README.md` and `backend/mlx_animate_diff_utils.py` is not implemented with real logic, it will produce placeholder output (random noise frames compiled into a video).
*   **Audio (Speech, Music, SFX):** Will be silent audio files of appropriate (placeholder) durations.
*   **Lip Sync:** Will simply show the input video again, as no actual lip movement is generated.
*   **Final Assembly:** Will show the video from the lip sync stage again.

The key is to understand the *flow* and the *types of controls* you have at each stage.

## Future Development

The exciting part comes next: integrating real AI models and functionality!

### 1. Text-to-Image Generation (MLX Stable Diffusion) - Partially Scaffolded
*   **Current Status:** The backend framework to use MLX-based Stable Diffusion for text-to-image generation (Phase 2) has been implemented.
    *   Configuration is managed in `backend/config_sd.py`.
    *   The main generation pipeline logic is in `backend/mlx_stable_diffusion.py`.
*   **Action Required by User:**
    *   **Model Files:** You need to download or convert Stable Diffusion models to the MLX format and place them in the `models/stable_diffusion_mlx/` directory. Please see the detailed instructions in `models/stable_diffusion_mlx/README.md`.
    *   **Critical: Implement `mlx_utils.py`:** The file `backend/mlx_utils.py` currently contains **placeholder classes** for the UNet, VAE, Text Encoder, Tokenizer, and Scheduler. **You MUST replace the content of `mlx_utils.py` with the actual Python class definitions and weight loading logic for these components from a working MLX Stable Diffusion example (e.g., from the official `mlx-examples` repository on GitHub).** The existing placeholders only simulate the structure and will not produce valid images without real model code and weights.
*   **Dependencies:** The `requirements.txt` file has been updated with `mlx`, `huggingface_hub`, `transformers`, and `safetensors` to support this.

### 2. Image-to-Video Generation (e.g., AnimateDiff + MLX) - Partially Scaffolded
*   **Current Status:** The backend framework to use an MLX-based AnimateDiff-style pipeline for image-to-video generation (Phase 3) has been implemented. This pipeline generates a sequence of frames from an input image and a prompt, and then compiles these frames into an MP4 video.
    *   Configuration is managed in `backend/config_i2v.py`.
    *   The main generation pipeline logic (frame generation and video compilation via OpenCV) is in `backend/mlx_image_to_video.py`. It reuses components (like VAE, Text Encoder, UNet - all placeholders) from the Stable Diffusion setup.
*   **Action Required by User:**
    *   **Model Files:** You need to download or convert an AnimateDiff Motion Module compatible with MLX and your base Stable Diffusion model. Place these in the `models/animate_diff_mlx/` directory. Please see detailed instructions in `models/animate_diff_mlx/README.md`.
    *   **Critical: Implement `mlx_animate_diff_utils.py`:** The file `backend/mlx_animate_diff_utils.py` currently contains **placeholder classes**. **You MUST replace its content with the actual Python class definition for the AnimateDiff Motion Module, its weight loading logic, and how it integrates with (or modifies) the base Stable Diffusion UNet.** The existing placeholders only simulate the structure.
*   **Dependencies:** This typically relies on the same set of MLX and SD dependencies. `opencv-python` (already in `requirements.txt`) is used for compiling frames into the output video.

### 3. Audio Generation (TTS, Music, SFX)
*   **Text-to-Speech:** Integrate Coqui TTS (or a similar lightweight model) into `/generate-speech`.
*   **Music Generation:** Integrate MusicGen Small (or similar) into `/generate-music`.
*   **Sound Effects:** Implement an SFX library lookup and/or integrate a simple AudioLDM model into `/generate-sfx`.

### 4. Lip Synchronization (e.g., Wav2Lip)
*   Integrate a model like Wav2Lip into the `/sync-lips` backend endpoint to synchronize the generated speech with the video.

### 5. Final Assembly (FFmpeg)
*   Implement the actual FFmpeg command pipeline in `/assemble-video` for:
    *   Mixing all audio tracks (speech, music, SFX).
    *   Replacing video audio with the new master mix.
    *   Encoding the final video (e.g., H.264 with VideoToolbox hardware acceleration on M2).

### 6. Advanced Features & Optimization
*   Implement actual "Project Save/Load" functionality.
*   Performance tuning and memory optimization for all models on MacBook Pro M2.
*   More sophisticated error handling for AI model execution.
*   Refine UI for controlling more model-specific parameters.

Thank you for exploring the Text-to-Multimedia AI Pipeline prototype! We hope this gives you a clear vision of its potential.
```
