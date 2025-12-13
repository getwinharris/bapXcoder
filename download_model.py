#!/usr/bin/env python3
"""
Script to download the Qwen3VL model from Hugging Face for bapXcoder
"""

import os
import sys
import requests
from pathlib import Path

def download_file(url, filename, chunk_size=8192):
    """Download a file from URL with progress indicator"""
    print(f"Downloading {filename} from {url}...")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)

                if total_size > 0:
                    percent = (downloaded_size / total_size) * 100
                    progress = '=' * (downloaded_size * 50 // total_size)
                    sys.stdout.write(f'\r[{progress:<50}] {percent:.1f}%')
                    sys.stdout.flush()

    print(f"\nDownload completed: {filename}")

def main():
    model_url = "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/Qwen3VL-8B-Instruct-Q8_0.gguf?download=true"
    model_filename = "Qwen3VL-8B-Instruct-Q8_0.gguf"

    print("bapXcoder Model Download")
    print("=" * 30)
    print(f"This will download the Qwen3VL model (~5-6GB) to {model_filename}")
    print("This is needed for the AI-powered IDE to work offline.")

    # Check if model already exists
    model_path = Path(model_filename)
    if model_path.exists():
        print(f"\nModel file {model_filename} already exists.")
        response = input("Do you want to re-download it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping download.")
            return

    try:
        download_file(model_url, model_filename)
        print(f"\nModel successfully downloaded to {model_filename}")

        # Verify file size
        size_gb = model_path.stat().st_size / (1024**3)
        print(f"Model size: {size_gb:.2f} GB")

        print("\nSetup complete! You can now start the IDE.")
        print("Run: python qwen3VL_local_cli.py")
        print("Then open your browser to http://localhost:7860")

    except Exception as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()