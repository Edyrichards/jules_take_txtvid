# Text-to-Multimedia AI Pipeline (M2 Optimized Prototype)

## Overview

Welcome! This project is a prototype for an ambitious Text-to-Multimedia AI Pipeline, designed to transform your text ideas into complete videos with synchronized audio. The ultimate goal is to create a tool optimized for Apple MacBook Pro M2 machines, focusing on efficiency and good-to-very-good results without requiring high-end cloud computing.

Think of it as your creative assistant: you provide the text, and it helps you build out the visual scenes, animations, voice-overs, music, and sound effects, finally assembling them into a finished video.

## Current Status: Fully Interactive Prototype

**Important Note for Beginners:** This version of the application is a **fully interactive prototype**. This means:

*   **The User Interface is Complete:** You can click through all the steps, input text, make selections, and see how the final application is intended to work.
*   **Backend Processes are Placeholders:** The actual Artificial Intelligence (AI) models for generating images, videos, audio, etc., are **not yet integrated**. When you click "Generate," the system currently creates quick placeholder files (like blue squares for images or silent audio files) to simulate the process.
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

**Step 0: Welcome & Project Setup**
1.  **Project Name (Conceptual):** You can type a name for your project here (e.g., "My First AI Video"). This is for organizational purposes in a future version.
2.  **Load Template (Conceptual):**
    *   This dropdown lets you choose a template to pre-fill some settings. Try selecting "Quick Cinematic Clip" or "Spoken Presentation Slide." You'll see a message that the template is applied.
    *   "None" uses default empty values.
3.  **Click "Start Project / Next"** to move to the image generation step.

**Step 1: Generate Image from Text**
1.  **Select image style:** Choose a visual style from the dropdown (e.g., "Photographic," "Cinematic"). If you applied a template, this might be pre-selected.
2.  **Enter your image prompt:** In the text area, describe the main scene or subject of your video. (e.g., "A serene beach at sunset, with palm trees"). If you used a template, a prompt might already be there. You can change it.
3.  **Click "Generate Image."**
    *   You'll see a spinner for a moment.
    *   A **placeholder image** (likely a simple colored square) will appear, along with a success message showing its placeholder path.
4.  If an image is displayed, the **"Next: Video Options"** button becomes active. Click it.
    *   You can also click "Back to Project Setup."

**Step 2: Convert Image to Video**
1.  **Review Image:** The placeholder image you "generated" in Step 1 is shown.
2.  **Select motion type:** Choose how you want this static image to be animated (e.g., "Slow Pan Right," "Slow Zoom In").
3.  **Click "Generate Video."**
    *   A spinner will appear.
    *   A **placeholder video** (which will look like your static placeholder image, but as a short video file) will be displayed.
4.  If a video is displayed, the **"Next: Audio Config"** button becomes active. Click it.
    *   You can also click "Back to Image Generation."

**Step 3: Configure Audio Elements**
This step has three tabs for different types of audio. All are optional.

*   **Text-to-Speech (TTS) Tab:**
    1.  **Text to Synthesize:** Type the narration or dialogue for your video.
    2.  **Select Voice:** Choose a voice type (e.g., "Male Young Professional").
    3.  **Select Emotion:** Choose an emotion for the voice.
    4.  **Click "Generate Speech."** A **placeholder audio player** (silent audio) will appear.
*   **Background Music Tab:**
    1.  **Select Music Style:** Choose a music style (e.g., "Ambient," "Upbeat").
    2.  **Duration (seconds):** Set how long the music should be.
    3.  **Click "Generate Music."** A **placeholder audio player** (silent audio of the specified duration) will appear.
*   **Sound Effects Tab:**
    1.  **Select SFX Category:** Choose a category (e.g., "Nature").
    2.  **Describe the sound effect:** Type a description (e.g., "wind blowing gently").
    3.  **Click "Generate SFX."** A **placeholder audio player** (short silent audio) will appear.
    4.  Note the caption about a pre-generated SFX library for future use.

Once done with audio (or if you skip it), click **"Next: Lip Sync."**
*   You can also click "Back to Video Options."

**Step 4: Apply Lip Sync**
This step conceptually synchronizes the generated speech (from TTS) with the video.
1.  **Prerequisites:** This step will only be fully active if you've generated both a video (Step 2) and speech audio (Step 3 - TTS). If not, it will show an informational message.
2.  **Review Inputs:** It will show the paths of the video and speech audio being used.
3.  **Click "Apply Lip Sync."**
    *   A spinner will appear.
    *   The **placeholder video will be redisplayed** (in a real version, this video would now have the character's lips moving in sync with the placeholder speech).
4.  If lip sync is "applied," the **"Next: Final Assembly"** button becomes active. Click it.
    *   You can also click "Back to Audio Configuration."

**Step 5: Assemble and Export Final Video**
This is the final step to combine everything.
1.  **Prerequisites:** Requires at least the (conceptually) lip-synced video and the speech audio.
2.  **Review Media:** It lists all the media items you've "generated" that will be included:
    *   Base Video (from lip sync step)
    *   Speech Audio
    *   Music Audio (if generated)
    *   Sound Effects (if generated - currently shows the path of the one SFX you could generate)
3.  **Export Options:**
    *   **Resolution:** Choose a video size (e.g., "720p").
    *   **Quality:** Select a quality level.
    *   **Format:** Choose the video file type (e.g., "MP4").
4.  **Click "Assemble and Export Video."**
    *   A spinner will appear.
    *   The **placeholder video will be displayed again**, representing the final assembled product.
    *   The export settings you chose will be shown.
5.  You can now click **"Start New Project"** to reset everything and go back to Step 0, or click "Back to Lip Sync."

## What to Expect (Placeholder Outputs)

*   **Images:** Will be simple colored squares.
*   **Videos:** Will be short video clips of the static placeholder images, or copies of previous placeholder videos.
*   **Audio (Speech, Music, SFX):** Will be silent audio files of appropriate (placeholder) durations.
*   **Lip Sync:** Will simply show the input video again, as no actual lip movement is generated.
*   **Final Assembly:** Will show the video from the lip sync stage again.

The key is to understand the *flow* and the *types of controls* you have at each stage.

## Future Development

The exciting part comes next:
*   Integrating real AI models for each generation step (Stable Diffusion for images, AnimateDiff for video, Coqui TTS for speech, MusicGen for music, Wav2Lip for lip sync).
*   Implementing the FFmpeg pipeline for actual audio mixing and video encoding, with M2 hardware acceleration.
*   Building out the "Project Save/Load" functionality.
*   Adding a real SFX library and potentially AudioLDM for on-demand SFX.
*   Performance tuning and optimization for MacBook Pro M2.

Thank you for exploring the Text-to-Multimedia AI Pipeline prototype! We hope this gives you a clear vision of its potential.
```
