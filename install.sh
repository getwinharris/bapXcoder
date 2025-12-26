#!/bin/bash

# bapXcoder System Installation Script
# Single executable installer with our logo that installs to system applications
# The entire application, including the hidden .IDEbapXcoder directory, gets moved to system apps
# Logo: ⬡ (Hexagon symbol representing our brand)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}bapXcoder System Installation${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Detect OS and set system app directory
detect_system_paths() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        SYSTEM_APPS_DIR="/opt/bapXcoder"
        INSTALLER_NAME="bapXcoder-Linux-installer.sh"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        SYSTEM_APPS_DIR="/Applications/bapXcoder.app"
        INSTALLER_NAME="bapXcoder-macOS-installer.sh"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        SYSTEM_APPS_DIR="/c/Program Files/bapXcoder"
        INSTALLER_NAME="bapXcoder-Windows-installer.sh"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_status "Detected OS: $OS"
    print_status "System installation directory: $SYSTEM_APPS_DIR"
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

# Clone repository to temporary location
clone_repository() {
    print_status "Preparing installation files..."

    # Create temporary directory for installation
    TEMP_DIR=$(mktemp -d -t bapxcoder_XXXXXXXXXX)
    cd "$TEMP_DIR"

    print_status "Downloading bapXcoder source code..."
    git clone https://github.com/getwinharris/bapXcoder.git
    cd bapXcoder

    # Ensure we have the .IDEbapXcoder directory with all core functionality
    if [[ ! -d ".IDEbapXcoder" ]]; then
        print_error "Critical error: .IDEbapXcoder directory not found in repository"
        exit 1
    fi

    print_success "Repository cloned with hidden .IDEbapXcoder directory"
    print_status "Hidden directory contains all AI validation, project management, and core functionality"
}

# Install Python dependencies locally first
install_dependencies() {
    print_status "Installing Python dependencies..."

    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

    print_success "Dependencies installed successfully"
}

# Skip model download since we're using Hugging Face connection
download_model() {
    print_status "Skipping local model download - using Hugging Face connection"
    print_status "Model will be accessed directly via llama.cpp from Hugging Face Hub"
}

# Move the entire application to system applications directory
move_to_system_apps() {
    print_status "Installing bapXcoder to system applications directory: $SYSTEM_APPS_DIR"
    
    # Create system app directory with proper permissions
    if [[ "$OS" == "macos" ]]; then
        # Create macOS application bundle structure
        sudo mkdir -p "$SYSTEM_APPS_DIR/Contents/MacOS"
        sudo mkdir -p "$SYSTEM_APPS_DIR/Contents/Resources"
        sudo mkdir -p "$SYSTEM_APPS_DIR/Contents/Frameworks"

        # Copy all application files to Resources directory (including .IDEbapXcoder)
        sudo cp -r . "$SYSTEM_APPS_DIR/Contents/Resources/"

        # Create minimal executable that runs the application
        sudo tee "$SYSTEM_APPS_DIR/Contents/MacOS/bapXcoder" > /dev/null << 'MACOS_EXEC'
#!/bin/bash
# bapXcoder macOS Application Launcher
APP_ROOT="$(cd "$(dirname "$0")/../Resources" && pwd)"

# Set environment variables for the application
export PYTHONPATH="$APP_ROOT:$PYTHONPATH"
export PYTHONIOENCODING=utf-8

echo "Starting bapXcoder IDE..."
echo "Hidden .IDEbapXcoder directory path: $APP_ROOT/.IDEbapXcoder"

cd "$APP_ROOT"
python3 ./.IDEbapXcoder/qwen3VL_local_cli.py
MACOS_EXEC
        sudo chmod +x "$SYSTEM_APPS_DIR/Contents/MacOS/bapXcoder"

        # Create minimal Info.plist
        sudo tee "$SYSTEM_APPS_DIR/Contents/Info.plist" > /dev/null << 'INFO_PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>bapXcoder</string>
    <key>CFBundleIdentifier</key>
    <string>com.bapxcoder.ide</string>
    <key>CFBundleName</key>
    <string>bapXcoder</string>
    <key>CFBundleDisplayName</key>
    <string>bapXcoder AI IDE</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
INFO_PLIST

    elif [[ "$OS" == "linux" ]]; then
        # For Linux, install in /opt or user directory
        sudo mkdir -p "$SYSTEM_APPS_DIR"

        # Copy the entire application with the hidden .IDEbapXcoder directory
        sudo cp -r ./* "$SYSTEM_APPS_DIR/"
        # Also copy hidden files/directories like .IDEbapXcoder
        sudo find . -maxdepth 1 -name ".*" -not -name "." -not -name ".." -exec cp -r '{}' "$SYSTEM_APPS_DIR/" \; 2>/dev/null || true

        # Create system-wide launcher script
        LAUNCHER_PATH="/usr/local/bin/bapXcoder"
        sudo tee "$LAUNCHER_PATH" > /dev/null << 'LINUX_EXEC'
#!/bin/bash
# bapXcoder Linux Launcher
APP_DIR="/opt/bapXcoder"

if [[ -d "$APP_DIR" ]]; then
    cd "$APP_DIR"
    echo "Starting bapXcoder IDE..."
    echo "Hidden .IDEbapXcoder directory path: $APP_DIR/.IDEbapXcoder"
    python3 ./.IDEbapXcoder/qwen3VL_local_cli.py
else
    echo "Error: bapXcoder not found in $APP_DIR"
    exit 1
fi
LINUX_EXEC
        sudo chmod +x "$LAUNCHER_PATH"

        # Create desktop entry for GUI access
        DESKTOP_ENTRY_PATH="/usr/local/share/applications/bapXcoder.desktop"
        sudo tee "$DESKTOP_ENTRY_PATH" > /dev/null << 'DESKTOP_ENTRY'
[Desktop Entry]
Version=1.0
Type=Application
Name=bapXcoder
Comment=AI-Powered IDE with Project Memory
Exec=sh -c 'cd /opt/bapXcoder && python3 ./.IDEbapXcoder/qwen3VL_local_cli.py'
Icon=applications-development
Terminal=false
Categories=Development;IDE;
StartupNotify=true
DESKTOP_ENTRY
        sudo chmod +x "$DESKTOP_ENTRY_PATH"

    else
        # For Windows (MSYS/Cygwin), install in program files
        mkdir -p "$SYSTEM_APPS_DIR"

        # Copy the entire application with the hidden .IDEbapXcoder directory
        cp -r ./* "$SYSTEM_APPS_DIR/"
        # Also copy hidden files/directories like .IDEbapXcoder
        find . -maxdepth 1 -name ".*" -not -name "." -not -name ".." -exec cp -r '{}' "$SYSTEM_APPS_DIR/" \; 2>/dev/null || true

        # Create Windows batch file
        STARTER_FILE="$SYSTEM_APPS_DIR/start_bapXcoder.bat"
        tee "$STARTER_FILE" > /dev/null << 'WINDOWS_BATCH'
@echo off
cd /d "%~dp0"
echo Starting bapXcoder IDE...
echo Hidden .IDEbapXcoder directory path: %~dp0\.IDEbapXcoder
python .\.IDEbapXcoder\qwen3VL_local_cli.py
pause
WINDOWS_BATCH
    fi

    print_success "bapXcoder installed to: $SYSTEM_APPS_DIR"
    print_status "Hidden .IDEbapXcoder directory is now embedded in the system application"
}

# Setup application in system
setup_system_app() {
    print_status "Setting up bapXcoder in system applications..."
    
    # Install Python dependencies in the local temp directory first
    python3 -m pip install -e .

    # Now move the entire application with all hidden files to the system directory
    move_to_system_apps

    print_success "Application setup complete in system directory"
}

# Main installation flow
main() {
    print_header
    print_status "Starting bapXcoder installation with system path integration..."
    print_status "This will install bapXcoder to system applications with bapXcoder AI model"
    print_status "The hidden .IDEbapXcoder directory will be embedded inside the system app"
    
    detect_system_paths
    check_dependencies
    clone_repository
    install_dependencies
    download_model
    setup_system_app

    print_success "✓ Installation complete!"
    print_success "✓ bapXcoder is now installed in your system applications directory"
    print_status "✓ Hidden .IDEbapXcoder directory contains all core functionality"
    print_status "✓ Run bapXcoder from your system applications menu"
    print_status ""
    if [[ "$OS" == "macos" ]]; then
        print_status "To start bapXcoder:"
        print_status "  - Double-click the bapXcoder app in your Applications folder"
    elif [[ "$OS" == "linux" ]]; then
        print_status "To start bapXcoder:"
        print_status "  - Run 'bapXcoder' from terminal"
        print_status "  - Or find 'bapXcoder' in your application menu"
    else
        print_status "To start bapXcoder:"
        print_status "  - Run the start_bapXcoder.bat file in the installation directory"
    fi
}

# Handle cleanup on script exit
cleanup() {
    # Clean up temporary installation directory
    if [[ -n "$TEMP_DIR" ]] && [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR" 2>/dev/null || true
    fi
    
    exit_code=$?
    print_status "Installation finished with exit code: $exit_code"
    exit $exit_code
}

# Set trap to handle cleanup
trap cleanup EXIT INT TERM

# Run main function
main "$@"