#!/usr/bin/env python3
"""
Test script to verify that the model file can be loaded properly
"""

import sys
from pathlib import Path

def test_model_path():
    # Check if the model file exists in the current directory (as it should be in the repo)
    model_path = Path("Qwen3VL-8B-Instruct-Q8_0.gguf")

    if model_path.exists():
        print(f"✓ Model file found: {model_path}")
        print(f"  Size: {model_path.stat().st_size / (1024**3):.2f} GB")
    else:
        print(f"✗ Model file NOT found at: {model_path}")
        print("  Please ensure you have cloned the complete repository with the model file")
        print("  The model file Qwen3VL-8B-Instruct-Q8_0.gguf should be in this directory")
        return False

    return True

def test_llama_cpp():
    try:
        from llama_cpp import Llama
        print("✓ llama-cpp-python is installed correctly")
        return True
    except ImportError:
        print("✗ llama-cpp-python is not installed")
        print("  Install it with: pip install llama-cpp-python")
        print("  For GPU support: CMAKE_ARGS=\"-DLLAMA_CUBLAS=on\" pip install llama-cpp-python")
        return False
    except Exception as e:
        print(f"✗ Error importing llama-cpp-python: {e}")
        return False

if __name__ == "__main__":
    print("qwen3VL-Local-CLI - Environment Test")
    print("="*50)
    
    model_ok = test_model_path()
    llama_ok = test_llama_cpp()
    
    print("\n" + "="*50)
    if model_ok and llama_ok:
        print("✓ All checks passed! You can run the CLI tool.")
        print("\nTo start interactive mode:")
        print("  python qwen3VL_local_cli.py -i")
        print("\nTo run a single prompt:")
        print("  python qwen3VL_local_cli.py --prompt \"Your question here\"")
    else:
        print("✗ Some checks failed. Please fix the issues before running the CLI tool.")
        sys.exit(1)