#!/bin/bash

# bapXcoder IDE Startup Script
# Launches the AI-powered development environment with Qwen2.5-Coder model

echo "🚀 Starting bapXcoder IDE with Qwen2.5-Coder model..."
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking for required packages..."
required_packages=("flask" "flask_socketio" "llama_cpp_python" "requests" "huggingface_hub" "tqdm")
missing_packages=()

for package in "${required_packages[@]}"; do
    if ! python3 -c "import $package" &> /dev/null; then
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -ne 0 ]; then
    echo "❌ Missing required packages: ${missing_packages[*]}"
    echo "Installing missing packages..."
    pip3 install "${missing_packages[@]}" || {
        echo "❌ Failed to install required packages"
        exit 1
    }
fi

# Check if model exists
echo "🔍 Checking for AI model..."
if [ ! -f "Qwen2.5-Coder-7B-Instruct-Q8_0.gguf" ]; then
    echo "⚠️  Qwen2.5-Coder model not found. Downloading automatically..."
    python3 download_model.py || {
        echo "❌ Failed to download model"
        exit 1
    }
fi

# Start the bapXcoder IDE
echo "🎮 Launching bapXcoder IDE with Trae.ai SOLO-inspired multi-agent system..."
echo "🌐 Interface will be available at: http://localhost:7860"
echo "💬 For help, visit: https://getwinharris.github.io/bapXcoder/"
echo ""

python3 bapxcoder_local_cli.py --model "Qwen2.5-Coder-7B-Instruct-Q8_0.gguf" --temperature 0.7 --max-tokens 1024 --threads 4 --context-size 8192 --gpu-layers 0

echo ""
echo "👋 bapXcoder IDE session ended."