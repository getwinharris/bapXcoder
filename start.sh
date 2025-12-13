#!/bin/bash

# bapX Coder - AI-Powered IDE Installer Script
# This script installs all dependencies and launches the IDE

set -e  # Exit on any error

echo "==========================================="
echo "bapX Coder - AI-Powered IDE Installer"
echo "==========================================="
echo ""

# Check if we're on macOS or Linux
PLATFORM="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
fi

if [ "$PLATFORM" == "unknown" ]; then
    echo "Unsupported platform: $OSTYPE"
    exit 1
fi

echo "Detected platform: $PLATFORM"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$@" > /dev/null 2>&1
}

# Check for required tools
echo "Checking for required tools..."

if ! command_exists python3; then
    echo "Error: python3 is required but not found"
    if [ "$PLATFORM" == "macos" ]; then
        echo "Please install Python 3.8+ using Homebrew: brew install python3"
    else
        echo "Please install Python 3.8+ for your system"
    fi
    exit 1
fi

if ! command_exists pip3; then
    echo "Error: pip3 is required but not found"
    echo "Please install pip with Python"
    exit 1
fi

if ! command_exists git; then
    echo "Error: git is required but not found"
    if [ "$PLATFORM" == "macos" ]; then
        echo "Installing git with Homebrew..."
        if command_exists brew; then
            brew install git
        else
            echo "Please install git or Homebrew first"
            exit 1
        fi
    else
        echo "Please install git for your system"
        exit 1
    fi
fi

echo "✓ All required tools found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Using existing virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Function to download model with progress
download_model() {
    local model_url="$1"
    local model_file="$2"
    local expected_size="$3"
    
    echo "Downloading $model_file from Hugging Face..."
    echo "Expected size: $expected_size"
    
    # Check if model already exists
    if [ -f "$model_file" ]; then
        local existing_size=$(stat -f%z "$model_file" 2>/dev/null || stat -c%s "$model_file" 2>/dev/null || echo 0)
        local expected_bytes=$(echo "$expected_size" | awk '{if($2=="GB") print $1*1024*1024*1024; else if($2=="MB") print $1*1024*1024; else print $1}')
        
        echo "Found existing $model_file ($existing_size bytes)"
        
        if [ "$existing_size" -gt 0 ] && [ "$existing_size" -gt "$((expected_bytes * 90 / 100))" ]; then
            echo "Existing file appears complete, skipping download"
            return 0
        else
            echo "Existing file is incomplete, re-downloading..."
            rm -f "$model_file"
        fi
    fi
    
    # Download with progress tracking
    if command_exists wget; then
        wget --progress=bar --show-progress "$model_url" -O "$model_file"
    elif command_exists curl; then
        # Use curl with progress bar
        curl -L --progress-bar "$model_url" -o "$model_file"
    else
        echo "Error: Neither wget nor curl found. Please install one to download the model."
        exit 1
    fi
    
    # Verify download
    local final_size=$(stat -f%z "$model_file" 2>/dev/null || stat -c%s "$model_file" 2>/dev/null || echo 0)
    echo ""
    echo "Downloaded $model_file ($((final_size / 1024 / 1024)) MB)"
    
    return 0
}

# Download model if not present
MODEL_FILE="Qwen3VL-8B-Instruct-Q8_0.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/Qwen3VL-8B-Instruct-Q8_0.gguf?download=true"

if [ ! -f "$MODEL_FILE" ]; then
    echo "The bapX Coder model needs to be downloaded (~5-6GB)"
    echo "This is a one-time download for offline operation"
    echo ""
    
    read -p "Proceed with download? [Y/n]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [ -z "$REPLY" ]; then
        download_model "$MODEL_URL" "$MODEL_FILE" "5.8GB"
    else
        echo "Model download cancelled. The IDE requires the model to run."
        exit 1
    fi
else
    echo "✓ Model file found: $MODEL_FILE"
fi

echo ""
echo "==========================================="
echo "Installation completed successfully!"
echo "==========================================="
echo ""
echo "To start bapX Coder IDE:"
echo "  ./start.sh run"
echo ""
echo "Or activate the virtual environment and run:"
echo "  source venv/bin/activate"
echo "  python qwen3VL_local_cli.py"
echo ""

# If run argument is provided, start the IDE
if [ "$1" == "run" ]; then
    echo "Starting bapX Coder IDE..."
    python3 qwen3VL_local_cli.py
fi