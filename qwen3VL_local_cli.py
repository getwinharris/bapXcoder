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

    print(f"Downloading {model_filename} from Hugging Face (~8.76GB)...")

    try:
        # Create temporary file for download
        temp_filename = model_path + ".tmp"

        # First, get the file size to show progress
        print("Connecting to Hugging Face servers...")
        response = requests.head(model_url)
        total_size = int(response.headers.get("content-length", 0))

        print(f"Total size: {total_size / (1024**3):.2f} GB")
        print("Starting download...")

        # Start download with progress bar using proper 65536-byte chunks
        response = requests.get(model_url, stream=True)
        response.raise_for_status()

        with open(temp_filename, "wb") as file, tqdm(
            desc=model_filename,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=65536):  # 65536-byte chunks as requested
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


def decode_content(encoded_content, encoding_type='utf-8'):
    """
    Decode content from various encoding schemes
    Supported encodings: utf-8, ascii, base64, hex, etc.
    """
    if encoding_type.lower() == 'base64':
        import base64
        if isinstance(encoded_content, str):
            encoded_bytes = encoded_content.encode('ascii')
        else:
            encoded_bytes = encoded_content
        return base64.b64decode(encoded_bytes).decode('utf-8', errors='replace')
    elif encoding_type.lower() == 'hex':
        if isinstance(encoded_content, str):
            return bytes.fromhex(encoded_content).decode('utf-8', errors='replace')
        return encoded_content.decode('utf-8', errors='replace')
    elif encoding_type.lower() in ['ascii', 'unicode', 'utf-8']:
        # For these encodings, just return the content as-is if it's already decoded
        if isinstance(encoded_content, bytes):
            return encoded_content.decode('utf-8', errors='replace')
        return encoded_content
    else:
        # For other encodings, try to decode
        if isinstance(encoded_content, bytes):
            try:
                return encoded_content.decode(encoding_type)
            except (UnicodeDecodeError, LookupError):
                return encoded_content.decode('utf-8', errors='replace')
        else:
            return encoded_content

if __name__ == "__main__":

def check_installation():
    """Run installation check before starting IDE"""
    print("Checking bapXcoder installation...")
    print("-" * 30)
    
    # Check dependencies
    missing_deps = []
    required_deps = [
        'flask', 'flask_socketio', 'requests', 
        'tqdm', 'configparser'
    ]
    
    # Check if llm-cpp-python is available
    try:
        import llama_cpp
    except ImportError:
        missing_deps.append('llama-cpp-python')
    
    for dep in ['flask', 'flask_socketio', 'requests', 'tqdm', 'configparser']:
        try:
            __import__(dep.replace('-', '_').replace('.', '_'))
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\nFound {len(missing_deps)} missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        
        response = input(f"\nWould you like to install these dependencies? (Y/n): ")
        if response.lower() == 'y' or response == '':
            print("\nInstalling dependencies...")
            for dep in missing_deps:
                pip_name = dep
                if dep == 'flask_socketio':
                    pip_name = 'flask-socketio'
                
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', pip_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✓ {dep} installed successfully")
                else:
                    print(f"❌ Failed to install {dep}: {result.stderr}")
                    return False
            print(f"\n✓ Successfully installed dependencies!")
        else:
            print("Installation cancelled. Dependencies are required.")
            return False
    else:
        print("✓ All dependencies satisfied")
    
    # Check model file
    model_file = Path("Qwen3VL-8B-Instruct-Q8_0.gguf")
    if model_file.exists():
        size_gb = model_file.stat().st_size / (1024**3)
        print(f"✓ Model file found: {size_gb:.2f} GB")
    else:
        print("ℹ Model file not found - will be downloaded on first run")
    
    return True

def main():
    # Run installation check first
    if not check_installation():
        print("❌ Installation check failed. Please run: python install.py")
        sys.exit(1)
    
    config = load_config()
    
    # Get command line arguments
    parser = argparse.ArgumentParser(description="bapX Coder - AI-Powered IDE")
    parser.add_argument("--model", type=str, default=config.get('model', 'model_path', fallback='Qwen3VL-8B-Instruct-Q8_0.gguf'), 
                       help="Path to the GGUF model file")
    parser.add_argument("--host", type=str, default=config.get('server', 'host', fallback='127.0.0.1'), 
                       help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=config.getint('server', 'port', fallback=7860), 
                       help="Port to run the web interface (default: 7860)")
    parser.add_argument("--temperature", type=float, default=config.getfloat('defaults', 'temperature', fallback=0.7),
                       help="Sampling temperature (default: 0.7)")
    parser.add_argument("--max-tokens", type=int, default=config.getint('defaults', 'max_tokens', fallback=512),
                       help="Maximum tokens to generate (default: 512)")
    parser.add_argument("--threads", type=int, default=config.getint('defaults', 'threads', fallback=4),
                       help="Number of CPU threads (default: 4)")
    parser.add_argument("--context-size", type=int, default=config.getint('defaults', 'context_size', fallback=4096),
                       help="Context size in tokens (default: 4096)")
    parser.add_argument("--gpu-layers", type=int, default=config.getint('defaults', 'gpu_layers', fallback=0),
                       help="Number of GPU layers (0 for CPU only, default: 0)")
    
    args = parser.parse_args()
    
    # Check if model exists, download if needed
    if not ensure_model_exists(args.model):
        print("Cannot proceed without the model file.")
        sys.exit(1)
    
    # Initialize the model runner
    global model_runner
    try:
        model_runner = Qwen3VLRunner(
            args.model,
            args.temperature,
            args.threads,
            args.context_size,
            args.gpu_layers
        )
    except Exception as e:
        print(f"Error initializing model: {e}")
        sys.exit(1)
    
    # Initialize project explorer for file management
    try:
        from project_explorer import ProjectExplorer
        global project_explorer
        project_explorer = ProjectExplorer(Path.cwd())
        print("Project explorer initialized for file management")
    except ImportError:
        print("Project explorer not available - install requirements: pip install -e .")
        project_explorer = None

    # Initialize syntax checker for live syntax validation
    try:
        from syntax_checker import initialize_syntax_checker, start_syntax_monitoring
        global syntax_checker
        syntax_checker = initialize_syntax_checker(Path.cwd())
        if syntax_checker:
            start_syntax_monitoring(Path.cwd())
            print("Live syntax checking initialized")
        else:
            print("Syntax checker could not be initialized")
    except ImportError:
        print("Syntax checker not available - install requirements: pip install watchdog")
        syntax_checker = None

    # Start the web-based IDE
    start_ide(args)

def start_ide(args):
    """Start the web-based IDE with Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bapxcoder-secret-key'
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Global reference to model runner and project explorer
    global model_runner, project_explorer

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory('.', path)

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('status', {'msg': 'Connected to bapXcoder IDE'})

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle chat messages from the frontend"""
        message = data.get('message', '')
        has_file = data.get('hasFile', False)
        file_name = data.get('fileName', '')
        file_type = data.get('fileType', '')
        continue_reasoning = data.get('continue_reasoning', False)
        conversation_history = data.get('history', [])

        # If there's a file attachment, include that in the processing
        if has_file:
            if file_type.startswith('image/'):
                message = f"[Image Analysis Request] The user has attached an image: {file_name}. {message}"
            else:
                message = f"[File Analysis Request] The user has attached a file: {file_name}. {message}"

        # If continue_reasoning is enabled, provide context from conversation
        if continue_reasoning and conversation_history:
            context = build_context_from_history(conversation_history)
            full_prompt = f"{context}\n\nUser: {message}\nAssistant:"
            response = model_runner.run_prompt(full_prompt, args.max_tokens)
        else:
            response = model_runner.run_prompt(message, args.max_tokens)

        emit('chat_response', {'response': response})

    def build_context_from_history(history):
        """Build context from conversation history"""
        context_parts = []
        # Use only the last few exchanges to avoid exceeding context limits
        recent_exchanges = history[-5:]  # Use last 5 exchanges

        for exchange in recent_exchanges:
            role = exchange.get('role', '')
            content = exchange.get('content', '')
            if role and content:
                if role == 'user':
                    context_parts.append(f"User: {content}")
                elif role == 'assistant':
                    context_parts.append(f"Assistant: {content}")

        return "\n".join(context_parts)

    @socketio.on('execute_command')
    def handle_execute_command(data):
        """Handle terminal commands from the frontend"""
        command = data.get('command', '')
        # Get the project path for this session
        project_path = get_session_project_path(request.sid) or get_current_project_path()

        # Update session tree with command execution
        update_session_tree(project_path, {
            'last_command': command,
            'last_command_time': time.time()
        })

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=project_path  # Execute in the project directory
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

    @socketio.on('initialize_project')
    def handle_initialize_project(data):
        """Initialize project explorer with file tree"""
        project_path = data.get('project_path', os.getcwd())

        try:
            from project_explorer import ProjectExplorer
            global project_explorer
            project_explorer = ProjectExplorer(project_path)

            project_tree = project_explorer.get_project_tree(max_depth=3)
            recent_files = project_explorer.get_recent_files()
            project_stats = project_explorer.get_project_stats()

            emit('project_initialized', {
                'project_path': project_path,
                'tree': project_tree,
                'recent_files': recent_files,
                'stats': project_stats
            })
        except ImportError:
            emit('status', {
                'msg': 'Project explorer not available - install dependencies: pip install -e .'
            })
        except Exception as e:
            emit('status', {'msg': f'Error initializing project: {str(e)}'})

    @socketio.on('open_file')
    def handle_open_file(data):
        """Open a file in the editor"""
        file_path = data.get('file_path', '')

        if not project_explorer:
            emit('file_error', {'message': 'Project explorer not initialized'})
            return

        try:
            content, error = project_explorer.get_file_content(file_path)
            if content is not None:
                emit('file_opened', {
                    'file_path': file_path,
                    'content': content,
                    'success': True
                })
            else:
                emit('file_error', {'message': error or 'Could not read file'})
        except Exception as e:
            emit('file_error', {'message': f'Error opening file: {str(e)}'})

    @socketio.on('save_file')
    def handle_save_file(data):
        """Save a file from the editor"""
        file_path = data.get('filename', '')
        content = data.get('content', '')

        if not project_explorer:
            emit('file_error', {'message': 'Project explorer not initialized'})
            return

        try:
            success, error = project_explorer.save_file_content(file_path, content)
            if success:
                emit('file_saved', {
                    'file_path': file_path,
                    'success': True
                })
            else:
                emit('file_error', {'message': error})
        except Exception as e:
            emit('file_error', {'message': f'Error saving file: {str(e)}'})

    @socketio.on('create_file')
    def handle_create_file(data):
        """Create a new file in the project"""
        file_path = data.get('file_path', '')
        content = data.get('content', '')

        if not project_explorer:
            emit('file_error', {'message': 'Project explorer not initialized'})
            return

        try:
            success, error = project_explorer.create_file(file_path, content)
            if success:
                emit('file_created', {
                    'file_path': file_path,
                    'success': True
                })
            else:
                emit('file_error', {'message': error})
        except Exception as e:
            emit('file_error', {'message': f'Error creating file: {str(e)}'})

    @socketio.on('create_directory')
    def handle_create_directory(data):
        """Create a new directory in the project"""
        dir_path = data.get('dir_path', '')

        if not project_explorer:
            emit('directory_error', {'message': 'Project explorer not initialized'})
            return

        try:
            success, error = project_explorer.create_directory(dir_path)
            if success:
                emit('directory_created', {
                    'dir_path': dir_path,
                    'success': True
                })
            else:
                emit('directory_error', {'message': error})
        except Exception as e:
            emit('directory_error', {'message': f'Error creating directory: {str(e)}'})

    @socketio.on('search_files')
    def handle_search_files(data):
        """Search for content in project files"""
        query = data.get('query', '')
        extensions = data.get('extensions', None)

        if not project_explorer:
            emit('search_error', {'message': 'Project explorer not initialized'})
            return

        try:
            results = project_explorer.search_in_project(query, extensions)
            emit('search_results', {
                'query': query,
                'results': results
            })
        except Exception as e:
            emit('search_error', {'message': f'Error searching files: {str(e)}'})

    @socketio.on('check_syntax')
    def handle_check_syntax(data):
        """Check syntax of a specific file"""
        file_path = data.get('file_path', '')

        if not project_explorer:
            emit('syntax_error', {'message': 'Project explorer not initialized'})
            return

        try:
            # Create full path relative to project
            full_path = project_explorer.project_path / file_path

            # Check if file exists
            if not full_path.exists():
                emit('syntax_error', {'message': f'File does not exist: {file_path}'})
                return

            # Import syntax checker
            from syntax_checker import LiveSyntaxChecker
            syntax_checker_instance = LiveSyntaxChecker(project_explorer.project_path)

            is_valid, errors = syntax_checker_instance.check_file_syntax(str(full_path))

            emit('syntax_check_result', {
                'file_path': file_path,
                'is_valid': is_valid,
                'errors': errors
            })
        except Exception as e:
            emit('syntax_error', {'message': f'Error checking syntax: {str(e)}'})

    @socketio.on('start_syntax_monitoring')
    def handle_start_syntax_monitoring(data):
        """Start live syntax monitoring for the project"""
        try:
            from syntax_checker import start_syntax_monitoring
            project_path = data.get('project_path', str(project_explorer.project_path if project_explorer else '.'))

            success = start_syntax_monitoring(project_path)
            if success:
                emit('status', {'msg': f'Live syntax monitoring started for: {project_path}'})
            else:
                emit('status', {'msg': 'Failed to start live syntax monitoring'})
        except Exception as e:
            emit('status', {'msg': f'Error starting syntax monitoring: {str(e)}'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    print(f"Starting bapXcoder IDE at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    socketio.run(app, host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
