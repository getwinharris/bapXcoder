#!/usr/bin/env python3
"""
bapXcoder Installation Wizard
Automatically detects and installs missing dependencies with user consent
"""

import sys
import os
import subprocess
import platform
import json
from pathlib import Path

import platform
import psutil
import shutil

def check_python_version():
    """Check if Python version meets requirements"""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required. Current version: {sys.version_info.major}.{sys.version_info.minor}")
        return False
    else:
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True

def check_package_installed(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name.replace('-', '_').replace('.', '_'))
        return True
    except ImportError:
        return False

def get_package_version(package_name):
    """Get the version of an installed Python package"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
        return "Unknown"
    except:
        return "Unknown"

def check_system_requirements():
    """Check system requirements"""
    print("\nSystem Requirements Check:")
    print("=" * 1)

    # Check OS
    print(f"OS: {platform.system()} {platform.release()}")

    # Check available memory (approximately)
    try:
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"RAM: {memory_gb:.1f} GB")
        if memory_gb < 8:
            print("! Recommended: 8GB+ RAM for running Qwen3VL model")
        else:
            print("✓ Sufficient RAM for model")
    except ImportError:
        print("ℹ Memory check requires psutil")

    # Check disk space (approximately)
    try:
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        print(f"Free Disk Space: {free_gb:.1f} GB")
        if free_gb < 10:  # Need space for model + app
            print("! Recommended: 10GB+ free space for complete setup")
        else:
            print("✓ Sufficient disk space for setup")
    except:
        print("ℹ Could not determine available disk space")

def check_dependencies():
    """Check for required dependencies"""
    print("\nDependency Check:")
    print("=" * 1)

    required_deps = {
        'flask': 'Flask web framework',
        'flask_socketio': 'WebSocket support',
        'requests': 'HTTP requests',
        'tqdm': 'Download progress bars',
        'configparser': 'Configuration management'
    }

    missing_deps = []
    for dep, description in required_deps.items():
        if check_package_installed(dep):
            version = get_package_version(dep.split('.')[0])  # Get main package name
            print(f"✓ {dep} - {description}")
        else:
            print(f"❌ {dep} - {description}")
            missing_deps.append(dep)

    # Check for llama_cpp separately as it might be installed differently
    try:
        import llama_cpp
        print("✓ llama-cpp-python - Local LLM inference")
    except ImportError:
        print("❌ llama-cpp-python - Local LLM inference")
        missing_deps.append('llama-cpp-python')

    # Check for psutil
    try:
        import psutil
        print("✓ psutil - System monitoring")
    except ImportError:
        print("❌ psutil - System monitoring (needed for memory checks)")
        missing_deps.append('psutil')

    return missing_deps

def install_dependencies(missing_deps):
    """Install missing dependencies with user permission"""
    if not missing_deps:
        print("\n✓ All dependencies are already installed!")
        return True

    print(f"\nFound {len(missing_deps)} missing dependencies:")
    for dep in missing_deps:
        print(f"  - {dep}")

    response = input(f"\nWould you like to install these {len(missing_deps)} dependencies? (Y/n): ")
    if response.lower() == 'y' or response == '':
        print("\nInstalling dependencies...")
        for dep in missing_deps:
            try:
                print(f"Installing {dep}...")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✓ {dep} installed successfully")
                else:
                    print(f"❌ Failed to install {dep}: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Error installing {dep}: {e}")
                return False

        print(f"\n✓ Successfully installed dependencies!")
        return True
    else:
        print("\n❌ Installation cancelled by user. Dependencies are required to run bapXcoder.")
        return False

def check_model_file():
    """Check if model file exists"""
    print("\nModel File Check:")
    print("=" * 1)

    model_file = "Qwen3VL-8B-Instruct-Q8_0.gguf"
    model_path = Path(model_file)

    if model_path.exists():
        size_gb = model_path.stat().st_size / (1024**3)
        print(f"✓ Model file found: {size_gb:.2f} GB")
        return True
    else:
        print("ℹ Model file not found - will be downloaded on first run (~8.76GB)")
        return False

def main():
    print("bapXcoder Installation Wizard")
    print("=" * 1)
    print("This will check your system and install required dependencies")

    # Check Python version
    if not check_python_version():
        print("\n❌ Python 3.8+ is required to run bapXcoder.")
        return False

    # Check system requirements
    check_system_requirements()

    # Check dependencies
    missing_deps = check_dependencies()

    # Install missing dependencies if any
    if missing_deps:
        if not install_dependencies(missing_deps):
            print("\n❌ Failed to install dependencies. Installation incomplete.")
            return False
    else:
        print("\n✓ All dependencies are already installed!")

    # Check model file
    check_model_file()

    print("\n" + "=" * 1)
    print("✓ System check complete!")
    print("✓ Dependencies verified/installed!")
    print("✓ Ready to run bapXcoder IDE!")
    print("\nTo start the IDE, run: python qwen3VL_local_cli.py")
    print("Then open your browser to: http://localhost:7860")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)