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
        print("\nbapX Coder Interactive Mode")
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

                print("\nbapX Coder: ", end="", flush=True)

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

    @app.route('/manifest.json')
    def manifest():
        return send_from_directory('templates', 'manifest.json', mimetype='application/manifest+json')

    @app.route('/sw.js')
    def sw():
        return send_from_directory('templates', 'sw.js', mimetype='application/javascript')

    @app.route('/favicon.ico')
    def favicon():
        # Return a simple icon for the favicon
        from flask import Response
        import base64
        # This is a simple data URI for a text-based favicon
        svg_data = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">👨‍💻</text></svg>'
        svg_b64 = base64.b64encode(svg_data.encode()).decode()
        data_uri = f"data:image/svg+xml;base64,{svg_b64}"
        # For now, return a simple response - in a full app this would serve actual icon
        from flask import make_response
        response = make_response("Favicon placeholder", 200)
        response.headers['Content-Type'] = 'image/x-icon'
        return response
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        # Initialize project session for this client
        session_id = request.sid
        emit('status', {'msg': 'Connected to bapXcoder IDE'})
        # Send initial project state
        emit('project_state', {
            'current_project': get_current_project_path(),
            'todo_list': get_todo_list(),
            'git_status': get_git_status()
        })

    @socketio.on('set_project')
    def handle_set_project(data):
        """Set the current project path for this session"""
        project_path = data.get('project_path', '')
        if project_path and os.path.isdir(project_path):
            # Create bapXcoder directory structure in the project
            bapxcoder_dir = os.path.join(project_path, '.bapXcoder')
            if not os.path.exists(bapxcoder_dir):
                os.makedirs(bapxcoder_dir)

            # Create default todo.json if it doesn't exist
            todo_file = os.path.join(bapxcoder_dir, 'todo.json')
            if not os.path.exists(todo_file):
                with open(todo_file, 'w') as f:
                    json.dump([], f)

            # Create default sessiontree.json if it doesn't exist
            sessiontree_file = os.path.join(bapxcoder_dir, 'sessiontree.json')
            if not os.path.exists(sessiontree_file):
                # Initialize with basic session structure
                session_tree = {
                    'project_path': project_path,
                    'session_timestamp': time.time(),
                    'session_id': request.sid,
                    'files_opened': [],
                    'current_session': {
                        'start_time': time.time(),
                        'last_activity': time.time(),
                        'active_files': []
                    }
                }
                with open(sessiontree_file, 'w') as f:
                    json.dump(session_tree, f, indent=2)

            # Create project-specific storage
            session_data = {
                'project_path': project_path,
                'session_id': request.sid
            }
            update_session_project(request.sid, session_data)
            emit('project_state', {
                'current_project': project_path,
                'todo_list': get_todo_list(project_path),
                'git_status': get_git_status(project_path)
            })
            emit('status', {'msg': f'Project set to: {project_path}. bapXcoder configuration created.'})
        else:
            emit('status', {'msg': 'Invalid project path'})

    @socketio.on('add_todo')
    def handle_add_todo(data):
        """Add a todo item to the project"""
        project_path = get_session_project_path(request.sid)
        if project_path:
            todo_item = data.get('todo', '')
            add_todo_item(project_path, todo_item)
            emit('todo_update', {'todo_list': get_todo_list(project_path)})
        else:
            emit('status', {'msg': 'No project set'})

    @socketio.on('remove_todo')
    def handle_remove_todo(data):
        """Remove a todo item from the project"""
        project_path = get_session_project_path(request.sid)
        if project_path:
            todo_index = data.get('index', -1)
            remove_todo_item(project_path, todo_index)
            emit('todo_update', {'todo_list': get_todo_list(project_path)})

            # Update session tree with todo removal
            update_session_tree(project_path, {
                'last_todo_removed': time.time(),
                'total_todos': len(get_todo_list(project_path))
            })
        else:
            emit('status', {'msg': 'No project set'})

    @socketio.on('add_todo')
    def handle_add_todo(data):
        """Add a todo item to the project"""
        project_path = get_session_project_path(request.sid)
        if project_path:
            todo_item = data.get('todo', '')
            add_todo_item(project_path, todo_item)

            # Update session tree with todo addition
            update_session_tree(project_path, {
                'last_todo_added': time.time(),
                'total_todos': len(get_todo_list(project_path))
            })

            emit('todo_update', {'todo_list': get_todo_list(project_path)})
        else:
            emit('status', {'msg': 'No project set'})

    def get_session_project_path(session_id):
        """Get the project path for a session"""
        # In a real implementation, this would look up in a session store
        # For now, return a default path
        return get_current_project_path()

    def update_session_project(session_id, project_data):
        """Update session with project data"""
        # In a real implementation, this would store in a session store
        pass

    def get_current_project_path():
        """Get the default project path"""
        return os.getcwd()

    def get_todo_list(project_path=None):
        """Get the todo list for a project"""
        # In a real implementation, this would read from project-specific storage
        if not project_path:
            project_path = get_current_project_path()
        todo_file = os.path.join(project_path, '.bapXcoder', 'todo.json')
        if os.path.exists(todo_file):
            try:
                with open(todo_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []

    def update_session_tree(project_path, update_data):
        """Update the session tree with new activity"""
        if not project_path:
            project_path = get_current_project_path()
        sessiontree_file = os.path.join(project_path, '.bapXcoder', 'sessiontree.json')

        # Load existing session tree
        session_tree = {}
        if os.path.exists(sessiontree_file):
            try:
                with open(sessiontree_file, 'r') as f:
                    session_tree = json.load(f)
            except:
                session_tree = {}

        # Update with new data
        for key, value in update_data.items():
            session_tree[key] = value

        # Update the current session's last activity
        if 'current_session' in session_tree:
            session_tree['current_session']['last_activity'] = time.time()
        else:
            session_tree['current_session'] = {
                'start_time': time.time(),
                'last_activity': time.time(),
                'active_files': []
            }

        # Save back to file
        with open(sessiontree_file, 'w') as f:
            json.dump(session_tree, f, indent=2)

    def add_todo_item(project_path, todo_item):
        """Add a todo item to the project"""
        if not os.path.exists(os.path.join(project_path, '.bapXcoder')):
            os.makedirs(os.path.join(project_path, '.bapXcoder'))

        todo_file = os.path.join(project_path, '.bapXcoder', 'todo.json')
        todo_list = get_todo_list(project_path)
        todo_list.append({
            'id': len(todo_list),
            'text': todo_item,
            'completed': False,
            'timestamp': time.time()
        })

        with open(todo_file, 'w') as f:
            json.dump(todo_list, f)

    def remove_todo_item(project_path, index):
        """Remove a todo item from the project"""
        todo_file = os.path.join(project_path, '.bapXcoder', 'todo.json')
        todo_list = get_todo_list(project_path)

        if 0 <= index < len(todo_list):
            del todo_list[index]
            # Update IDs after removal
            for i, item in enumerate(todo_list):
                item['id'] = i

            with open(todo_file, 'w') as f:
                json.dump(todo_list, f)

    def get_git_status(project_path=None):
        """Get git status for project"""
        if not project_path:
            project_path = get_current_project_path()

        try:
            # Check if it's a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Get git status
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )

                # Get current branch
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )

                return {
                    'is_git_repo': True,
                    'branch': branch_result.stdout.strip() or 'HEAD',
                    'has_changes': bool(status_result.stdout.strip()),
                    'changes': status_result.stdout.strip()
                }
            else:
                return {'is_git_repo': False}
        except Exception:
            return {'is_git_repo': False}
    
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

    @socketio.on('git_oauth')
    def handle_git_oauth(data):
        """Handle Git OAuth requests from the frontend"""
        # For a real implementation, this would start the OAuth flow
        # For now, we'll just open the GitHub OAuth URL in the user's browser
        github_auth_url = "https://github.com/login/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:7860/git/callback&scope=repo"
        emit('chat_response', {'response': f"Opening Git OAuth in your browser. Please complete authentication and return here.\n\nFor security, bapX Coder doesn't store your credentials."})

        # In a real implementation, we would start OAuth flow
        # webbrowser.open(github_auth_url)  # Commented for security reasons

    @socketio.on('git_repo')
    def handle_git_repo(data):
        """Handle Git repository operations"""
        repo_url = data.get('repo_url', '')
        action = data.get('action', 'clone')  # clone, pull, push, etc.

        if repo_url:
            if action == 'clone':
                response = f"Git repository clone requested: {repo_url}. In a complete implementation, this would clone the repository to your local workspace."
            else:
                response = f"Git operation '{action}' requested for: {repo_url}. In a complete implementation, this would perform Git operations."
        else:
            response = "Please provide a Git repository URL. Example: https://github.com/username/repository.git"

        emit('chat_response', {'response': response})
    
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
    
    print(f"Starting bapXcoder IDE at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    socketio.run(app, host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()