#!/usr/bin/env python3
"""
Test script to verify that bapXcoder environment is set up properly
"""

import sys
from pathlib import Path

def test_model_path():
    # Check if the model file exists in the current directory
    model_path = Path("Qwen3VL-8B-Instruct-Q8_0.gguf")

    if model_path.exists():
        print(f"✓ Model file found: {model_path}")
        print(f"  Size: {model_path.stat().st_size / (1024**3):.2f} GB")
    else:
        print(f"✗ Model file NOT found at: {model_path}")
        print("  You need to download the model first:")
        print("  python download_model.py")
        print("  OR run the IDE which will prompt for download if missing")
        return False

    return True

def test_dependencies():
    """Test that all required dependencies are installed"""
    deps_ok = True

    # Test llama-cpp-python
    try:
        from llama_cpp import Llama
        print("✓ llama-cpp-python is installed correctly")
    except ImportError:
        print("✗ llama-cpp-python is not installed")
        print("  Install it with: pip install llama-cpp-python")
        print("  For GPU support: CMAKE_ARGS=\"-DLLAMA_CUBLAS=on\" pip install llama-cpp-python")
        deps_ok = False
    except Exception as e:
        print(f"✗ Error importing llama-cpp-python: {e}")
        deps_ok = False

    # Test Flask
    try:
        import flask
        print("✓ Flask is installed correctly")
    except ImportError:
        print("✗ Flask is not installed")
        print("  Install it with: pip install flask")
        deps_ok = False
    except Exception as e:
        print(f"✗ Error importing Flask: {e}")
        deps_ok = False

    # Test Flask-SocketIO
    try:
        import socketio
        print("✓ Flask-SocketIO is installed correctly")
    except ImportError:
        print("✗ Flask-SocketIO is not installed")
        print("  Install it with: pip install flask-socketio")
        deps_ok = False
    except Exception as e:
        print(f"✗ Error importing Flask-SocketIO: {e}")
        deps_ok = False

    # Test requests
    try:
        import requests
        print("✓ requests is installed correctly")
    except ImportError:
        print("✗ requests is not installed")
        print("  Install it with: pip install requests")
        deps_ok = False
    except Exception as e:
        print(f"✗ Error importing requests: {e}")
        deps_ok = False

    return deps_ok

if __name__ == "__main__":
    print("bapXcoder - Environment Test")
    print("="*50)

    model_ok = test_model_path()
    deps_ok = test_dependencies()

    print("\n" + "="*50)
    if model_ok and deps_ok:
        print("✓ All checks passed! You can start the IDE.")
        print("\nTo start the IDE:")
        print("  python qwen3VL_local_cli.py")
        print("  Then open your browser to http://localhost:7860")
    else:
        print("✗ Some checks failed. Please fix the issues before running the IDE.")
        sys.exit(1)