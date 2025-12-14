#!/bin/bash

# bapXcoder Installation Script
# Single executable file with our logo that handles everything
# Logo: ⬡ (Hexagon symbol to represent our brand)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_status "Detected OS: $OS"
}

# Check for dependencies
check_dependencies() {
    print_status "Checking for dependencies..."
    
    # Check for Python 3.8+
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        print_status "Found Python: $PYTHON_VERSION"
        
        # Check if Python version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_status "Python version is sufficient"
        else
            print_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is required but not found"
        exit 1
    fi
    
    # Check for git
    if command -v git &> /dev/null; then
        print_status "Found Git"
    else
        print_error "Git is required but not found"
        exit 1
    fi
    
    # Check for curl or wget
    if command -v curl &> /dev/null; then
        DOWNLOADER="curl"
        print_status "Found curl"
    elif command -v wget &> /dev/null; then
        DOWNLOADER="wget"
        print_status "Found wget"
    else
        print_error "Either curl or wget is required"
        exit 1
    fi
}

# Clone repository
clone_repository() {
    print_status "Cloning bapXcoder repository..."
    
    # Create temporary directory for installation
    TEMP_DIR=$(mktemp -d -t bapxcoder_XXXXXXXXXX)
    cd "$TEMP_DIR"
    
    git clone https://github.com/getwinharris/bapXcoder.git
    cd bapXcoder
    
    print_success "Repository cloned successfully"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Download model if not present
download_model() {
    print_status "Checking for model file..."
    
    MODEL_FILE="Qwen3VL-8B-Instruct-Q8_0.gguf"
    
    if [[ -f "$MODEL_FILE" ]]; then
        print_status "Model file already exists, skipping download"
    else
        print_status "Downloading Qwen3VL model..."
        if [[ "$DOWNLOADER" == "curl" ]]; then
            curl -L "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/Qwen3VL-8B-Instruct-Q8_0.gguf?download=true" -o "$MODEL_FILE"
        else
            wget "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/Qwen3VL-8B-Instruct-Q8_0.gguf?download=true" -O "$MODEL_FILE"
        fi
        print_success "Model downloaded successfully"
    fi
}

# Setup application
setup_app() {
    print_status "Setting up bapXcoder application..."
    
    # Install in development mode
    python3 -m pip install -e .
    
    print_success "Application setup complete"
}

# Start the web server
start_server() {
    print_status "Starting bapXcoder web server..."
    
    # Start the server in background
    python3 qwen3VL_local_cli.py &
    SERVER_PID=$!
    
    print_status "bapXcoder is running! Open your browser and go to http://localhost:7860"
    print_status "Press Ctrl+C to stop the server"
    
    # Wait for server process
    wait $SERVER_PID
}

# Main installation flow
main() {
    print_status "Starting bapXvector installation..."
    print_status "This will install bapXcoder with the Qwen3VL AI model locally"
    
    detect_os
    check_dependencies
    clone_repository
    install_dependencies
    download_model
    setup_app
    
    print_success "Installation complete!"
    print_status "Starting bapXcoder web interface..."
    
    start_server
}

# Handle cleanup on script exit
cleanup() {
    # Kill any background processes if needed
    pkill -P $$
    exit_code=$?
    print_status "Installation script finished with exit code: $exit_code"
    exit $exit_code
}

# Set trap to handle cleanup
trap cleanup EXIT INT TERM

# Run main function
main "$@"