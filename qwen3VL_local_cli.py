#!/usr/bin/env python3
"""
bapXcoder: A standalone AI-powered IDE with integrated CLI and offline model
"""

import argparse
import sys
import os
from pathlib import Path
import configparser
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import threading
import json
import time

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
        
        if download_choice == '' or download_choice == 'y':
            print("Downloading model...")
            try:
                result = subprocess.run([sys.executable, "download_model.py"], check=True)
                if result.returncode == 0:
                    print("Model download completed successfully!")
                    return True
                else:
                    print("Model download failed.")
                    return False
            except subprocess.CalledProcessError:
                print("Model download failed. Please run 'python download_model.py' manually.")
                return False
            except FileNotFoundError:
                print("download_model.py not found. Please download the model manually.")
                return False
        else:
            print("Model download cancelled.")
            print("Please download the model manually or run 'python download_model.py'")
            return False
    
    return True

def print_help():
    print("""
bapXcoder - Standalone AI-powered IDE with integrated CLI
==========================================================

This IDE allows you to run the Qwen3VL model locally with integrated development tools.
Repository: https://github.com/getwinharris/bapXcoder

Prerequisites:
1. Install llama.cpp: pip install llama-cpp-python flask flask-socketio
2. Install this tool: pip install -e .
3. Have your model file: Qwen3VL-8B-Instruct-Q8_0.gguf (downloaded during setup)

Basic Usage:
  python qwen3VL_local_cli.py  # Start the web-based IDE
  Open your browser to http://localhost:7860

Options:
  --model PATH          Path to GGUF model file (default: Qwen3VL-8B-Instruct-Q8_0.gguf)
  --host HOST           Host address (default: 127.0.0.1)
  --port PORT           Port to run the web interface (default: 7860)
  --max-tokens N        Maximum tokens to generate (default: 512)
  --temperature T       Sampling temperature (default: 0.7)
  --threads N           Number of CPU threads (default: 4)
  --context-size N      Context size in tokens (default: 4096)
  --gpu-layers N        Number of GPU layers (0 for CPU only, default: 0)
  --help                Show this help message

Examples:
  # Start the IDE
  python qwen3VL_local_cli.py
  
  # Start the IDE on a custom port
  python qwen3VL_local_cli.py --port 8080
  
  # Using GPU acceleration
  python qwen3VL_local_cli.py --gpu-layers 20
    """)

class Qwen3VLRunner:
    def __init__(self, model_path, temperature=0.7, threads=4, context_size=4096, gpu_layers=0):
        self.model_path = model_path
        self.temperature = temperature
        self.threads = threads
        self.context_size = context_size
        self.gpu_layers = gpu_layers
        self.model = None
        self.chat_history = []
        
        # Try to import llama-cpp-python
        try:
            from llama_cpp import Llama
            self.Llama = Llama
        except ImportError:
            print("Error: llama-cpp-python is not installed.")
            print("Please install it with one of these commands:")
            print("  pip install llama-cpp-python")
            print("  # For GPU acceleration (if you have CUDA):")
            print("  CMAKE_ARGS=\"-DLLAMA_CUBLAS=on\" pip install llama-cpp-python")
            print("  # For Apple Silicon (if you have Metal):")
            print("  CMAKE_ARGS=\"-DLLAMA_METAL=on\" pip install llama-cpp-python")
            print("  # For AMD GPU:")
            print("  CMAKE_ARGS=\"-DLLAMA_HIPBLAS=on\" pip install llama-cpp-python")
            sys.exit(1)
        
        print(f"Loading model from {self.model_path}...")
        print(f"Config: Context={self.context_size}, Threads={self.threads}, GPU layers={self.gpu_layers}")
        try:
            self.model = self.Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                n_threads=self.threads,
                n_gpu_layers=self.gpu_layers,
                verbose=False
            )
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            sys.exit(1)

    def run_prompt(self, prompt, max_tokens=512):
        """Run a single prompt and return the response"""
        # Include the bapX Coder persona in the prompt
        system_prompt = "You are bapX Coder, an advanced AI programming assistant. You are helpful, creative, and insightful. You can analyze code, images (OCR), perform web searches, and help with Git operations. Always respond as bapX Coder with expertise and precision. "

        # Format the prompt for the model with the persona
        formatted_prompt = f"<|system|>{system_prompt}\n<|user|>{prompt}\n<|assistant|>"

        try:
            response = self.model(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=self.temperature,
                stop=["\n<|assistant|>", "\nUser:", "\nAssistant:", "</s>", "\n<|"],
                echo=False
            )
            result = response['choices'][0]['text'].strip()

            # Clean up the response to remove any trailing assistant/User markers
            if result.startswith('<|assistant|>'):
                result = result[len('<|assistant|>'):].strip()
            elif '<|assistant|>' in result:
                result = result.split('<|assistant|>')[0].strip()

            return result
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: Could not generate response ({str(e)})"

    def run_interactive(self, max_tokens=512):
        """Run in interactive chat mode"""
        print("\nbapXcoder Interactive Mode")
        print("Type 'quit' or 'exit' to exit")
        print("Type 'help' for commands")
        print("-" * 40)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("\nCommands:")
                    print("  quit/exit/q - Exit the program")
                    print("  help - Show this help")
                    print("  reset - Reset conversation history")
                    print("  clear - Clear screen")
                    continue
                elif user_input.lower() == 'reset':
                    self.chat_history = []
                    print("Conversation history reset.")
                    continue
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif not user_input:
                    continue

                # Build the full prompt with history
                full_prompt = self._build_prompt(user_input)

                print("\nbapXcoder: ", end="", flush=True)

                # Generate response with streaming
                response = self.model(
                    full_prompt,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                    echo=False,
                    stream=True
                )

                full_response = ""
                for chunk in response:
                    text = chunk['choices'][0]['text']
                    print(text, end="", flush=True)
                    full_response += text
                    if text in ['\n\n', '</s>']:
                        break

                print()  # New line after response

                # Update chat history
                self.chat_history.append({"role": "user", "content": user_input})
                self.chat_history.append({"role": "assistant", "content": full_response})

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")

    def _build_prompt(self, user_input):
        """Build the full prompt with chat history"""
        # Include the bapX Coder persona in the prompt
        prompt = "You are bapX Coder, an advanced AI programming assistant. You are helpful, creative, and insightful. You can analyze code, images (OCR), perform web searches, and help with Git operations. Always respond as bapX Coder with expertise and precision.\n\n"

        for msg in self.chat_history[-4:]:  # Use last 4 exchanges to keep context manageable
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                prompt += f"<|user|>{content}\n"
            else:
                prompt += f"<|assistant|>{content}\n"

        prompt += f"<|user|>{user_input}\n<|assistant|>"
        return prompt

def main():
    config = load_config()
    
    # Get default values from config
    default_model_path = config.get('model', 'model_path', fallback='Qwen3VL-8B-Instruct-Q8_0.gguf')
    default_max_tokens = config.getint('defaults', 'max_tokens', fallback=512)
    default_temperature = config.getfloat('defaults', 'temperature', fallback=0.7)
    default_host = config.get('server', 'host', fallback='127.0.0.1')
    default_port = config.getint('server', 'port', fallback=7860)
    
    parser = argparse.ArgumentParser(description="bapXcoder: Standalone AI-powered IDE with integrated CLI")
    parser.add_argument("--model", type=str, default=default_model_path, help="Path to the GGUF model file")
    parser.add_argument("--host", type=str, default=default_host, help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=default_port, help="Port to run the web interface (default: 7860)")
    parser.add_argument("--max-tokens", type=int, default=default_max_tokens, help="Maximum tokens to generate")
    parser.add_argument("--temperature", type=float, default=default_temperature, help="Sampling temperature")
    parser.add_argument("--threads", type=int, default=config.getint('defaults', 'threads', fallback=4), help="Number of CPU threads")
    parser.add_argument("--context-size", type=int, default=config.getint('defaults', 'context_size', fallback=4096), help="Context size in tokens")
    parser.add_argument("--gpu-layers", type=int, default=config.getint('defaults', 'gpu_layers', fallback=0), help="Number of GPU layers (0 for CPU only)")
    parser.add_argument("--help", "-h", action="store_true", help="Show this help message")
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
        return
    
    # Check if model exists, download if needed
    if not ensure_model_exists(args.model):
        print("Cannot proceed without the model file.")
        sys.exit(1)
    
    # Start the web-based IDE
    start_ide(args)

def start_ide(args):
    """Start the web-based IDE with Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bapxcoder-secret-key'
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize the model runner
    model_runner = Qwen3VLRunner(
        args.model,
        args.temperature,
        args.threads,
        args.context_size,
        args.gpu_layers
    )
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('status', {'msg': 'Connected to bapXcoder IDE'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle chat messages from the frontend"""
        message = data.get('message', '')
        has_file = data.get('hasFile', False)
        file_name = data.get('fileName', '')
        file_type = data.get('fileType', '')

        # If there's a file attachment, include that in the processing
        if has_file:
            if file_type.startswith('image/'):
                # This would in a real implementation process the image
                message = f"[Image Analysis Request] The user has attached an image: {file_name}. {message}"
            else:
                message = f"[File Analysis Request] The user has attached a file: {file_name}. {message}"

        response = model_runner.run_prompt(message, args.max_tokens)
        emit('chat_response', {'response': response})

    @socketio.on('web_search')
    def handle_web_search(data):
        """Handle web search requests from the frontend"""
        query = data.get('query', '')

        # In a real implementation, this would perform actual web search
        # For now, we'll simulate by asking the model to search for information
        search_prompt = f"Please provide information about: {query}. This is a web search request."
        response = model_runner.run_prompt(search_prompt, args.max_tokens)
        emit('chat_response', {'response': f"Web search results for '{query}':\n\n{response}"})
    
    @socketio.on('execute_command')
    def handle_execute_command(data):
        """Handle terminal commands from the frontend"""
        command = data.get('command', '')
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            emit('command_output', {
                'command': command,
                'output': output,
                'returncode': result.returncode
            })
        except subprocess.TimeoutExpired:
            emit('command_output', {
                'command': command,
                'output': 'Command timed out after 30 seconds',
                'returncode': -1
            })
        except Exception as e:
            emit('command_output', {
                'command': command,
                'output': f'Error: {str(e)}',
                'returncode': -1
            })
    
    print(f"Starting bapXcoder IDE at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    socketio.run(app, host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()