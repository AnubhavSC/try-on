# AI Virtual Try-On

A photorealistic virtual try-on application powered by custom AI models. This tool allows you to upload a person's image and a clothing item to visualize how the clothing fits on the person.

## Features

- **High-Fidelity Try-On**: Replaces clothing while preserving body pose, lighting, and shadows.
- **Secure Processing**: Images are processed securely.
- **Simple UI**: Easy-to-use interface for quick results.

## Prerequisites

- Python 3.8 or higher installed on your system.

## Setup Guide

1.  **Clone or Download** this repository to your local machine.

2.  **Navigate** to the project directory:
    ```bash
    cd path/to/TRYON
    ```

3.  **Install Dependencies**:
    Run the following command to install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    You have two options for providing your API key:
    
    *   **Option A (Recommended for Devs):** Create a `.env` file in the root directory:
        ```env
        NANOBANANA_API_KEY=your_api_key_here
        ```
    *   **Option B (Easy):** Run the app without a `.env` file. The app will ask you to enter your API key in the browser, and it will be saved safely in your browser's local storage.


## Running the Application

To start the application, run:

```bash
streamlit run app.py
```

The application will open automatically in your default web browser (usually at `http://localhost:8501`).

## Usage

1.  **Upload Person**: Upload a clear photo of the person.
2.  **Upload Cloth**: Upload a photo of the clothing item you want to try on.
3.  **Generate**: Click the "Generate Result" button.
4.  **Wait**: The AI will process the images (this may take a minute) and display the result.

## Troubleshooting

-   **Upload Failed**: If you see an upload error, ensure your internet connection is active, as the app temporarily hosts images for processing.
-   **API Error**: Check if your API key in `.env` is correct and active.

## Resources

-   [NanoBanana API](https://nanobananaapi.ai/)

## Credits

-   **Developer**: Anubhav Aka hex47i
-   **Website**: [anubhavnath.dev](https://anubhavnath.dev)

## Tech Stack

-   **Libraries**: Streamlit, Requests, Pillow
-   **APIs**: NanoBanana API, Tmpfiles.org

