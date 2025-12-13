#!/usr/bin/env python3
"""
bapXcoder: A standalone AI-powered IDE with integrated CLI and offline model
"""
import argparse
import sys
import os
from pathlib import Path
import configparser
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import subprocess
import threading
import json
import time
import webbrowser
def load_config():
    """Load configuration from config.ini file"""
    config = configparser.ConfigParser()
    config_path = Path("config.ini")
    
    if config_path.exists():
        config.read(config_path)
        return config
    else:
        # Return default values if config doesn't exist
        config['model'] = {'model_path': 'Qwen3VL-8B-Instruct-Q8_0.gguf'}
        config['defaults'] = {
            'max_tokens': '512',
            'temperature': '0.7',
            'threads': '4',
            'context_size': '4096',
            'gpu_layers': '0'
        }
        config['server'] = {
            'host': '127.0.0.1',
            'port': '7860'
        }
        return config
def ensure_model_exists(model_path):
    """Check if model exists, and if not, prompt user to download it"""
    model_file = Path(model_path)

    if not model_file.exists():
        print(f"Model file not found: {model_path}")
        print("\nThe Qwen3VL model needs to be downloaded (~5-6GB).")

        download_choice = input("Would you like to download it now? (Y/n): ").lower().strip()

        if download_choice == "" or download_choice == "y":
            return download_model_with_progress(model_path)

    return True

def download_model_with_progress(model_path):
    """Download the model with progress bar and verification"""
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("Installing required download dependencies (tqdm, requests)...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "tqdm", "requests"], check=True)
        import requests
        from tqdm import tqdm

def ensure_model_exists(model_path):
    """Check if model exists, and if not, prompt user to download it"""
    model_file = Path(model_path)
    
    if not model_file.exists():
        print(f"Model file not found: {model_path}")
        print("\nThe Qwen3VL model needs to be downloaded (~5-6GB).")
        
        download_choice = input("Would you like to download it now? (Y/n): ").lower().strip()
        
        if download_choice == '' or download_choice == 'y':
            return download_model_with_progress(model_path)
    
    return True

def download_model_with_progress(model_path):
    """Download the model with progress bar and verification"""
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("Installing required download dependencies (tqdm, requests)...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "tqdm", "requests"], check=True)
        import requests
        from tqdm import tqdm

    model_filename = os.path.basename(model_path)

    # Define the model URL (using the canonical Hugging Face URL)
    model_url = "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/Qwen3VL-8B-Instruct-Q8_0.gguf?download=true"

    print(f"Downloading {model_filename} from Hugging Face (~5.8GB)...")

    try:
        # Create temporary file for download
        temp_filename = model_path + ".tmp"

        # First, get the file size to show progress
        response = requests.head(model_url)
        total_size = int(response.headers.get("content-length", 0))

        print(f"Total size: {total_size / (1024**3):.2f} GB")

        # Start download with progress bar
        response = requests.get(model_url, stream=True)
        response.raise_for_status()

        with open(temp_filename, "wb") as file, tqdm(
            desc=model_filename,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        # Rename temporary file to final name
        os.rename(temp_filename, model_path)

        # Verify the download
        final_size = os.path.getsize(model_path)
        print(f"\nModel downloaded successfully! Size: {final_size / (1024**3):.2f} GB")

        # Basic integrity check - ensure file looks like a valid GGUF file
        try:
            with open(model_path, "rb") as f:
                # Read first few bytes to check for GGUF signature
                header = f.read(16)
                if b"GGUF" not in header:
                    print("Warning: Downloaded file may not be a valid GGUF file")
                    return False
                else:
                    print("Model file integrity verified.")
                    return True
        except Exception as e:
            print(f"Error verifying model file: {e}")
            return False

    except Exception as e:
        print(f"Error downloading model: {e}")
        # Clean up temp file if it exists
        temp_filename = model_path + ".tmp"
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return False


def encode_content(content, encoding_type='utf-8'):
    """
    Encode content using various encoding schemes
    Supported encodings: utf-8, ascii, base64, hex, etc.
    """
    if encoding_type.lower() == 'base64':
        import base64
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        return base64.b64encode(content_bytes).decode('ascii')
    elif encoding_type.lower() == 'ascii':
        if isinstance(content, bytes):
            return content.decode('ascii', errors='ignore')
        return content.encode('ascii', errors='ignore').decode('ascii')
    elif encoding_type.lower() == 'unicode':
        if isinstance(content, str):
            return content
        return content.decode('utf-8', errors='replace')
    elif encoding_type.lower() == 'hex':
        if isinstance(content, str):
            return content.encode('utf-8').hex()
        return content.hex()
    elif encoding_type.lower() == 'utf-8':
        if isinstance(content, bytes):
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                # Try other common encodings if UTF-8 fails
                for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        return content.decode(enc)
                    except UnicodeDecodeError:
                        continue
                # If all fail, use utf-8 with error replacement
                return content.decode('utf-8', errors='replace')
        return content
    else:
        # Default to the specified encoding type
        if isinstance(content, bytes):
            try:
                return content.decode(encoding_type)
            except (UnicodeDecodeError, LookupError):
                return content.decode('utf-8', errors='replace')
        else:
            try:
                return content.encode(encoding_type).decode(encoding_type)
            except (UnicodeEncodeError, LookupError):
                return content


def decode_content(encoded_content, encoding_type='utf-8'):












            




    """
    Encode content using various encoding schemes
    Supported encodings: utf-8, ascii, base64, hex, etc.
    """
    if encoding_type.lower() == 'base64':
        import base64
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        return base64.b64encode(content_bytes).decode('ascii')
    elif encoding_type.lower() == 'ascii':
        if isinstance(content, bytes):
            return content.decode('ascii', errors='ignore')
        return content.encode('ascii', errors='ignore').decode('ascii')
    elif encoding_type.lower() == 'unicode':
        if isinstance(content, str):
            return content
        return content.decode('utf-8', errors='replace')
    elif encoding_type.lower() == 'hex':
        if isinstance(content, str):
            return content.encode('utf-8').hex()
        return content.hex()
    elif encoding_type.lower() == 'utf-8':
        if isinstance(content, bytes):
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                # Try other common encodings if UTF-8 fails
                for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        return content.decode(enc)
                    except UnicodeDecodeError:
                        continue
                # If all fail, use utf-8 with error replacement
                return content.decode('utf-8', errors='replace')
        return content
    else:
        # Default to the specified encoding type
        if isinstance(content, bytes):
            try:
                return content.decode(encoding_type)
            except (UnicodeDecodeError, LookupError):
                return content.decode('utf-8', errors='replace')
        else:
            try:
                return content.encode(encoding_type).decode(encoding_type)
            except (UnicodeEncodeError, LookupError):
                return content


