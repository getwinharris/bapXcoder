#!/usr/bin/env python3
"""
bapXcoder: A standalone AI-powered IDE with integrated CLI and offline model
"""
import argparse
import sys
import os
import jwt
import requests
from pathlib import Path
import configparser
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from flask_socketio import SocketIO, emit
import subprocess
import threading
import json
import time
import webbrowser
from datetime import datetime, timedelta

# Load configuration settings and provide centralized management for application settings
# Connects to model, server, and defaults systems during startup
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

# bapXcoder Agent with internal specialized functions for intelligent development assistance
# The bapXcoder Agent uses two specialized internal functions through a shared memory system:
# - Interpreter function for communication, context management, and multimodal processing
# - Developer function for specialized coding tasks, coordinated through shared memory
class BapXcoderAgent:
    def __init__(self, model_path=None, temperature=0.7, threads=4, context_size=4096, gpu_layers=0):
        """
        Initialize the bapXcoder Agent with Interpreter and Developer functions.
        This creates an internal agent with two specialized functions working through shared memory.
        If model_path is None or not found locally, connect directly to Hugging Face Hub.
        Interpreter function (bapXcoder-Interpreter): Handles communication, UI, multimodal processing
        Developer function (bapXcoder-Developer): Specializes in coding tasks and implementation
        """
        self.temperature = temperature
        self.threads = threads
        self.context_size = context_size
        self.gpu_layers = gpu_layers

        # Initialize bapXcoder model for all tasks (single model approach like Trae.ai SOLO)
        try:
            from llama_cpp import Llama
            import os

            # Initialize the bapXcoder model - handles all tasks (coding, planning, analysis)
            print("Initializing bapXcoder IDE Agent with Qwen2.5-Coder model...")

            # Check if the specific model exists, otherwise download it automatically
            model_exists = model_path and os.path.exists(model_path)

            if not model_exists:
                # Automatically download the recommended model
                print("Qwen2.5-Coder model not found. Downloading automatically...")
                from huggingface_hub import hf_hub_download
                try:
                    model_path = hf_hub_download(
                        repo_id="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
                        filename="*Q8_0.gguf",
                        local_files_only=False
                    )
                    print(f"Successfully downloaded model: {model_path}")
                except Exception as download_error:
                    print(f"Download failed: {download_error}")
                    print("Trying alternative download method...")
                    try:
                        self.interpreter_model = Llama.from_pretrained(
                            repo_id="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
                            filename="*Q8_0.gguf",
                            n_ctx=context_size,
                            n_threads=threads,
                            n_gpu_layers=gpu_layers,
                            verbose=False
                        )
                        print("Successfully connected to bapXcoder model via Hugging Face Hub")
                    except Exception as e:
                        print(f"Failed to connect to model: {e}")
                        raise
                    # For single model approach, use same model for all functions
                    self.interpreter_model = self.interpreter_model
                    self.developer_model = self.interpreter_model
                    return

            # Load the model from the specified path
            self.interpreter_model = Llama(
                model_path=model_path,
                n_ctx=context_size,
                n_threads=threads,
                n_gpu_layers=gpu_layers,
                verbose=False
            )

            # For bapXcoder's single model approach (like Trae.ai SOLO), use same model for all functions
            self.developer_model = self.interpreter_model
            print("Successfully connected to bapXcoder unified model")

        except ImportError:
            print("Please install required packages: pip install llama-cpp-python huggingface_hub")
            raise
        except Exception as e:
            print(f"Error initializing bapXcoder Agent: {e}")
            raise

    def run_interpreter_prompt(self, prompt, max_tokens=512, check_session_continuity_on_startup=False):
        """
        Process user prompt through the bapXcoder Agent's Interpreter function.
        The Interpreter function handles all user communication, context management, and multimodal processing.
        For coding tasks, it may coordinate with the Developer function through shared memory.

        If check_session_continuity_on_startup=True, checks for session continuity and reports last tasks/activities.
        """
        try:
            # Check session continuity on startup if requested
            if check_session_continuity_on_startup:
                session_continuity_message = self.check_session_continuity()
                if session_continuity_message:
                    # Prepend session continuity info to the prompt
                    full_prompt = f"{session_continuity_message}\n\nUser request: {prompt}"
                    response = self.interpreter_model(
                        full_prompt,
                        max_tokens=max_tokens,
                        temperature=self.temperature,
                        echo=False
                    )
                else:
                    # No session continuity info, just run the original prompt
                    response = self.interpreter_model(
                        prompt,
                        max_tokens=max_tokens,
                        temperature=self.temperature,
                        echo=False
                    )
            else:
                # All user interaction goes through the Interpreter function of the bapXcoder Agent
                response = self.interpreter_model(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                    echo=False
                )
            return response['choices'][0]['text']
        except Exception as e:
            print(f"Error running prompt through bapXcoder Agent's Interpreter function: {e}")
            return f"Error: {e}"

    def run_developer_task(self, coding_task, max_tokens=512):
        """
        Process specialized coding tasks through the bapXcoder Agent's Developer function.
        The Developer function specializes in code generation, analysis, and implementation.
        """
        try:
            # Coding tasks are processed through the Developer function of the bapXcoder Agent
            response = self.developer_model(
                coding_task,
                max_tokens=max_tokens,
                temperature=self.temperature,
                echo=False
            )
            return response['choices'][0]['text']
        except Exception as e:
            print(f"Error running coding task through bapXcoder Agent's Developer function: {e}")
            return f"Error: {e}"

    def run_coding_task(self, task_description, max_tokens=512):
        """
        Process specialized coding tasks through the appropriate model based on task type.
        For coding tasks, uses the Developer function; for other tasks, uses the Interpreter function.
        """
        try:
            # Determine if this is primarily a coding task that should go to Developer function
            coding_keywords = [
                'code', 'function', 'class', 'implement', 'create', 'generate',
                'write', 'debug', 'fix', 'refactor', 'test', 'program', 'script',
                'algorithm', 'method', 'variable', 'syntax', 'error', 'module',
                'import', 'library', 'dependency', 'build', 'compile', 'deploy',
                'api', 'endpoint', 'database', 'migration', 'configuration'
            ]

            is_coding_related = any(keyword in task_description.lower() for keyword in coding_keywords)

            if is_coding_related:
                # Direct coding tasks to Developer function
                coding_prompt = f"[CODING TASK] {task_description}\nGenerate appropriate code following best practices:"
                return self.run_developer_task(coding_prompt, max_tokens)
            else:
                # Other tasks to Interpreter function
                return self.run_interpreter_prompt(task_description, max_tokens)
        except Exception as e:
            print(f"Error running coding task through bapXcoder Agent: {e}")
            return f"Error: {e}"

    def check_session_continuity(self):
        """
        Check session continuity by reading from .bapXcoder/users/{user_id}/session.json
        This method should be called with a user context.
        Returns a continuation message if session data exists, otherwise None
        """
        # Note: This is a placeholder. In practice, this would need user context to determine which
        # user's session to check. The actual implementation should check for a specific user's session.
        # This is mainly included as a demonstration, but the main checking occurs in other parts of the code.
        return ""

    def run_vision_prompt(self, prompt, image_path, max_tokens=512):
        """
        Run a vision-language prompt through the bapXcoder IDE Agent's Interpreter function.
        The Interpreter function handles multimodal processing including OCR and visual understanding.
        """
        try:
            # For vision models, we need special handling
            # The Interpreter function handles image analysis and multimodal understanding
            full_prompt = f"Analyze the following image and respond to the user's request.\nUser Request: {prompt}\nImage Path: {image_path}"
            response = self.interpreter_model(
                full_prompt,
                max_tokens=max_tokens,
                temperature=self.temperature,
                echo=False
            )
            return response['choices'][0]['text']
        except Exception as e:
            print(f"Error running vision prompt through bapXcoder IDE Agent: {e}")
            return f"Error: {e}"

def check_subscription_status(user_id):
    """Check if user's subscription is still valid and manage user-specific project memory"""
    try:
        # Check local subscription status - no external API calls
        # For now, we'll just allow access based on existence of user data
        user_data_file = Path('.bapXcoder/users') / f"{user_id}.json"
        if user_data_file.exists():
            with open(user_data_file, 'r') as f:
                user_data = json.load(f)

            # Check if subscription is still active
            sub_end_date_str = user_data.get('subscription_end_date')
            if sub_end_date_str and sub_end_date_str != 'never':
                sub_end_date = datetime.fromisoformat(sub_end_date_str)
                if datetime.now() > sub_end_date:
                    print(f"Subscription expired for user {user_id}. Access denied.")
                    return False  # Subscription expired - user cannot access
            return True
        else:
            # For free trial users, check if trial period has expired
            # New user - assign trial
            trial_end = (datetime.now() + timedelta(days=60)).isoformat()
            user_data = {
                'subscription_type': 'trial',
                'subscription_start': datetime.now().isoformat(),
                'subscription_end_date': trial_end,
                'user_id': user_id
            }

            # Create user-specific directory structure for project memory
            user_dir = Path('.bapXcoder/users') / user_id
            user_dir.mkdir(parents=True, exist_ok=True)

            with open(user_data_file, 'w') as f:
                json.dump(user_data, f, indent=2)

            print(f"New user {user_id} registered with trial access until {trial_end}")
            return True  # Allow access with trial
    except Exception as e:
        print(f"Error checking subscription for user {user_id}: {e}")
        return False  # If any error occurs, deny access by default


def is_user_authenticated():
    """Check if user is authenticated locally"""
    # For local use, assume user is authenticated by default
    # In a real implementation, this would check local authentication
    return True

def store_session_locally(project_path, user_id, session_data):
    """Store session data locally in user-specific project memory"""
    try:
        # Create or access the .bapXcoder directory in the project
        project_dir = Path(project_path)
        bapx_dir = project_dir / '.bapXcoder'
        bapx_dir.mkdir(exist_ok=True)

        # Create user-specific subdirectory within project's .bapXcoder folder
        user_session_dir = bapx_dir / 'users' / user_id
        user_session_dir.mkdir(parents=True, exist_ok=True)

        # Save session data in user-specific location
        session_file = user_session_dir / 'session.json'
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error storing session locally for user {user_id}: {e}")
        return False

def get_current_project_path():
    """Get the current project path for the session"""
    # In a real implementation, this would retrieve the project path from session data
    # For now, returning current working directory
    return str(Path.cwd())

def store_sessiontree_data(project_path, user_id, session_data):
    """Store session state and memory in the project's .bapXcoder folder in user-specific location"""
    try:
        # Create or access the .bapXcoder directory in the project
        project_dir = Path(project_path)
        bapx_dir = project_dir / '.bapXcoder'
        bapx_dir.mkdir(exist_ok=True)

        # Create user-specific subdirectory within project's .bapXcoder folder
        user_session_dir = bapx_dir / 'users' / user_id
        user_session_dir.mkdir(parents=True, exist_ok=True)

        # Save session state and memory data in user-specific location
        sessiontree_file = user_session_dir / 'sessiontree.json'
        with open(sessiontree_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error storing sessiontree data for user {user_id}: {e}")
        return False

def get_session_project_path(session_id):
    """Get project path for a specific session"""
    # In a real implementation, this would retrieve project path from session data
    # For now, return current directory
    return str(Path.cwd())

def store_todo_locally(project_path, user_id, todo_data):
    """Store todo data locally in user-specific project memory"""
    try:
        # Create or access the .bapXcoder directory in the project
        project_dir = Path(project_path)
        bapx_dir = project_dir / '.bapXcoder'
        bapx_dir.mkdir(exist_ok=True)

        # Create user-specific subdirectory within project's .bapXcoder folder
        user_todo_dir = bapx_dir / 'users' / user_id
        user_todo_dir.mkdir(parents=True, exist_ok=True)

        # Load existing todos if file exists to append the new one
        todo_file = user_todo_dir / 'todo.json'
        existing_todos = []
        if todo_file.exists():
            try:
                with open(todo_file, 'r') as f:
                    existing_data = json.load(f)
                    if isinstance(existing_data, list):
                        existing_todos = existing_data
                    elif isinstance(existing_data, dict) and 'todos' in existing_data:
                        existing_todos = existing_data.get('todos', [])
                    elif isinstance(existing_data, dict):
                        existing_todos = [existing_data]  # Convert single todo to list
            except:
                existing_todos = []  # Start fresh if there's an error reading

        # Add new todo to the list
        if isinstance(todo_data, list):
            existing_todos.extend(todo_data)
        else:
            existing_todos.append(todo_data)

        # Save todos in user-specific location
        todo_file = user_todo_dir / 'todo.json'
        with open(todo_file, 'w') as f:
            json.dump(existing_todos, f, indent=2)

        return True
    except Exception as e:
        print(f"Error storing todo locally for user {user_id}: {e}")
        return False

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


# Admin Panel Routes
@app.route('/admin')
def admin_login():
    """Admin login page"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>bapXcoder Admin Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0f0f13 0%, #1a1a25 100%);
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background: #161622;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #2d2d40;
            width: 350px;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #2d2d40;
            border-radius: 4px;
            background: #252536;
            color: white;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(90deg, #7c5cff 0%, #6a4fd6 100%);
            border: none;
            border-radius: 4px;
            color: white;
            cursor: pointer;
            font-weight: 600;
        }
        h2 {
            color: #7c5cff;
            text-align: center;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Admin Panel Login</h2>
        <form method="POST" action="/admin/authenticate">
            <input type="text" name="username" placeholder="Admin Username" required>
            <input type="password" name="password" placeholder="Admin Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
''')

@app.route('/admin/authenticate', methods=['POST'])
def admin_authenticate():
    """Admin authentication"""
    username = request.form.get('username')
    password = request.form.get('password')

    # Default admin credentials (should be changed in production)
    admin_username = os.environ.get('ADMIN_USERNAME', 'getwinharris@gmail.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'bapX2025#')

    if username == admin_username and password == admin_password:
        session['admin_logged_in'] = True
        session.permanent = True  # Session expires after timeout
        return redirect('/admin/dashboard')
    else:
        return redirect('/admin?error=invalid_credentials')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect('/admin')

    # Load statistics
    stats = get_admin_statistics()
    return render_template_string(ADMIN_PANEL_HTML, admin_data=stats)

def get_admin_statistics():
    """Get admin statistics for dashboard"""
    try:
        # Count total users from the session data
        total_users = 0
        active_subscriptions = 0
        expired_subscriptions = 0

        # Mock data - in a real implementation this would come from a database
        # or from the actual user data storage
        return {
            'total_users': 1245,
            'active_subscriptions': 842,
            'expired_subscriptions': 403,
            'total_downloads': 15432,
            'monthly_downloads': 3876,
            'recent_users': [],
            'payment_revenue': 12345,
            'trial_users': 200,
            'paid_users': 842
        }
    except:
        # Return default mock data
        return {
            'total_users': 0,
            'active_subscriptions': 0,
            'expired_subscriptions': 0,
            'total_downloads': 0,
            'monthly_downloads': 0,
            'recent_users': [],
            'payment_revenue': 0,
            'trial_users': 0,
            'paid_users': 0
        }

# Admin panel HTML template
ADMIN_PANEL_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>bapXcoder Admin Panel</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #0f0f13 0%, #1a1a25 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }

        .admin-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .admin-header {
            background: linear-gradient(90deg, #1a1a25 0%, #14141c 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #2d2d40;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .admin-header h1 {
            color: #7c5cff;
            font-size: 1.8rem;
        }

        .admin-nav {
            display: flex;
            gap: 20px;
            background: linear-gradient(90deg, #1a1a25 0%, #14141c 100%);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #2d2d40;
        }

        .admin-nav a {
            text-decoration: none;
            color: #a0a0c0;
            padding: 10px 20px;
            border-radius: 8px;
            transition: background 0.3s;
        }

        .admin-nav a:hover, .admin-nav a.active {
            background: linear-gradient(90deg, #7c5cff 0%, #6a4fd6 100%);
            color: white;
        }

        .admin-section {
            background: linear-gradient(180deg, #161622 0%, #14141c 100%);
            border: 1px solid #2d2d40;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            display: block; /* Initially show dashboard */
        }

        .admin-section.hidden {
            display: none;
        }

        .admin-section h2 {
            color: #7c5cff;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }

        .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(180deg, #1a1a25 0%, #14141c 100%);
            border: 1px solid #2d2d40;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }

        .stat-card h3 {
            color: #7c5cff;
            margin-bottom: 10px;
            font-size: 1rem;
        }

        .stat-card .number {
            font-size: 2rem;
            font-weight: bold;
            color: #50fa7b;
        }

        .credentials-form input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #2d2d40;
            border-radius: 4px;
            background: #252536;
            color: white;
        }

        .credentials-form button {
            background: linear-gradient(90deg, #7c5cff 0%, #6a4fd6 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 20px;
        }

        .credentials-form button:hover {
            opacity: 0.9;
        }

        .user-table {
            width: 100%;
            border-collapse: collapse;
        }

        .user-table th, .user-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #2d2d40;
        }

        .user-table th {
            color: #7c5cff;
            background: rgba(124, 92, 255, 0.1);
        }

        .logout-btn {
            background: #ff4757;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            float: right;
        }
    </style>
</head>
<body>
    <div class="admin-container">
        <div class="admin-header">
            <h1><i class="fas fa-cog"></i> bapXcoder Admin Panel</h1>
            <button class="logout-btn" onclick="location.href='/admin/logout'">Logout</button>
        </div>

        <div class="admin-nav">
            <a href="#" class="nav-link active" onclick="showSection('dashboard')">Dashboard</a>
            <a href="#" class="nav-link" onclick="showSection('users')">Users</a>
            <a href="#" class="nav-link" onclick="showSection('downloads')">Downloads</a>
            <a href="#" class="nav-link" onclick="showSection('credentials')">Credentials</a>
        </div>

        <!-- Dashboard Section -->
        <div id="dashboard" class="admin-section">
            <h2><i class="fas fa-chart-line"></i> Dashboard Overview</h2>
            <div class="dashboard-stats">
                <div class="stat-card">
                    <h3>Total Users</h3>
                    <div class="number">{{ admin_data.total_users }}</div>
                </div>
                <div class="stat-card">
                    <h3>Active Subscriptions</h3>
                    <div class="number">{{ admin_data.active_subscriptions }}</div>
                </div>
                <div class="stat-card">
                    <h3>Expired Subscriptions</h3>
                    <div class="number">{{ admin_data.expired_subscriptions }}</div>
                </div>
                <div class="stat-card">
                    <h3>Trialing Users</h3>
                    <div class="number">{{ admin_data.trial_users }}</div>
                </div>
            </div>
            <div class="dashboard-stats">
                <div class="stat-card">
                    <h3>Total Downloads</h3>
                    <div class="number">{{ admin_data.total_downloads }}</div>
                </div>
                <div class="stat-card">
                    <h3>Monthly Downloads</h3>
                    <div class="number">{{ admin_data.monthly_downloads }}</div>
                </div>
                <div class="stat-card">
                    <h3>Revenue</h3>
                    <div class="number">${{ admin_data.payment_revenue }}</div>
                </div>
                <div class="stat-card">
                    <h3>Paid Users</h3>
                    <div class="number">{{ admin_data.paid_users }}</div>
                </div>
            </div>
        </div>

        <!-- Users Section -->
        <div id="users" class="admin-section hidden">
            <h2><i class="fas fa-users"></i> User Management</h2>
            <table class="user-table">
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Email</th>
                        <th>Provider</th>
                        <th>Subscription</th>
                        <th>Registration Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>user@example.com</td>
                        <td>GitHub</td>
                        <td>Monthly</td>
                        <td>2025-01-01</td>
                        <td><span style="color: #50fa7b;">Active</span></td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>another@example.com</td>
                        <td>Google</td>
                        <td>Annual</td>
                        <td>2025-01-02</td>
                        <td><span style="color: #50fa7b;">Active</span></td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>trial@example.com</td>
                        <td>GitHub</td>
                        <td>Trial</td>
                        <td>2025-01-03</td>
                        <td><span style="color: #f1fa8c;">Trial</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Downloads Section -->
        <div id="downloads" class="admin-section hidden">
            <h2><i class="fas fa-download"></i> Download Statistics</h2>
            <div class="dashboard-stats">
                <div class="stat-card">
                    <h3>Today</h3>
                    <div class="number">42</div>
                </div>
                <div class="stat-card">
                    <h3>This Week</h3>
                    <div class="number">287</div>
                </div>
                <div class="stat-card">
                    <h3>This Month</h3>
                    <div class="number">{{ admin_data.monthly_downloads }}</div>
                </div>
                <div class="stat-card">
                    <h3>All Time</h3>
                    <div class="number">{{ admin_data.total_downloads }}</div>
                </div>
            </div>
        </div>

        <!-- Credentials Section -->
        <div id="credentials" class="admin-section hidden">
            <h2><i class="fas fa-cog"></i> Configuration Settings</h2>
            <div class="config-section">
                <h3>Runtime Configuration</h3>
                <p>Model runtime settings configured via local config file</p>

                <h3>Local Settings</h3>
                <p>Project-specific configurations stored locally</p>

                <h3>Licensing</h3>
                <p>License validation handled locally</p>
            </div>
        </div>
    </div>

    <script>
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.admin-section').forEach(section => {
                section.classList.add('hidden');
            });

            // Show selected section
            document.getElementById(sectionId).classList.remove('hidden');

            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });

            // Find the link that triggered this section and make it active
            document.querySelectorAll('.nav-link').forEach(link => {
                if (link.onclick.toString().includes(sectionId)) {
                    link.classList.add('active');
                }
            });
        }

        // Set dashboard as active by default
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.admin-section').forEach(section => {
                if (section.id !== 'dashboard') {
                    section.classList.add('hidden');
                }
            });
        });
    </script>
</body>
</html>
'''

@app.route('/admin/update-config', methods=['POST'])
def admin_update_config():
    """Update local configuration settings"""
    if not session.get('admin_logged_in'):
        return redirect('/admin')

    # In a real implementation, this would update local configuration
    # For now, just return to dashboard
    return redirect('/admin/dashboard')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect('/admin')
    
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

# Initializes the dual-model AI development environment with CLI and web interface
# Orchestrates all subsystems (models, UI, project management, validation)
def main():
    """Main entry point for bapXcoder application"""
    # Run installation check first
    if not check_installation():
        print("❌ Installation check failed. Please run: python install.py")
        sys.exit(1)

    config = load_config()
    
    # Get command line arguments
    parser = argparse.ArgumentParser(description="bapXcoder - Dual-Model AI Development Environment (Interpreter + Developer)")
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

    # Check if model exists for local usage, skip check if using Hugging Face connection
    # For Hugging Face connection, the Qwen3VLRunner will handle downloading/caching automatically
    model_exists = Path(args.model).exists()
    if not model_exists:
        print(f"Local model not found: {args.model}")
        print("Will connect to Hugging Face Hub for model access (first access may take longer)")
    else:
        print(f"Using local model: {args.model}")

    # Initialize the bapXcoder Agent
    global model_runner
    try:
        model_runner = BapXcoderAgent(
            args.model,
            args.temperature,
            args.threads,
            args.context_size,
            args.gpu_layers
        )

        # Check session continuity on startup
        print("Checking session continuity...")
        session_continuity_message = model_runner.check_session_continuity()
        if session_continuity_message:
            print(f"Session restored: {session_continuity_message}")
        else:
            print("No previous session data found - starting fresh session")

    except Exception as e:
        print(f"Error initializing bapXcoder Agent: {e}")
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

    def check_user_subscription_status(user_id):
        """Check user's subscription status with expiry validation"""
        try:
            # In a real implementation, this would fetch from GitHub metadata
            # For now, simulate the check for trial expiration

            # Check if user has a subscription file in their GitHub repo
            bapxcoder_dir = Path('.bapXcoder')
            bapxcoder_dir.mkdir(exist_ok=True)

            user_data_file = bapxcoder_dir / f"users_{user_id}.json"
            if user_data_file.exists():
                with open(user_data_file, 'r') as f:
                    user_data = json.load(f)

                # Check subscription expiration
                sub_end_str = user_data.get('subscription_end_date', 'never')
                if sub_end_str == 'never':
                    return { 'type': 'lifetime', 'expires': 'never', 'days_left': float('inf') }
                else:
                    sub_end = datetime.fromisoformat(sub_end_str)
                    if datetime.now() > sub_end:
                        return { 'type': 'expired', 'expires': sub_end_str, 'days_left': 0 }
                    else:
                        days_left = (sub_end - datetime.now()).days
                        return { 'type': 'active', 'expires': sub_end_str, 'days_left': days_left }
            else:
                # New user - assign trial
                trial_end = (datetime.now() + timedelta(days=60)).isoformat()
                user_data = {
                    'subscription_type': 'trial',
                    'subscription_start': datetime.now().isoformat(),
                    'subscription_end_date': trial_end,
                    'user_id': user_id
                }

                with open(user_data_file, 'w') as f:
                    json.dump(user_data, f, indent=2)

                days_left = (datetime.fromisoformat(trial_end) - datetime.now()).days
                return { 'type': 'trial', 'expires': trial_end, 'days_left': days_left }
        except Exception as e:
            # Default to trial if anything fails
            trial_end = (datetime.now() + timedelta(days=60)).isoformat()
            return { 'type': 'trial', 'expires': trial_end, 'days_left': 60 }

def check_user_session_continuity(user_id):
    """Check session continuity for a specific user and return continuity message"""
    try:
        from pathlib import Path
        import json
        from datetime import datetime

        # Check session state and memory from sessiontree.json
        sessiontree_file = Path('.bapXcoder/users') / user_id / 'sessiontree.json'
        # Also check intent from todo.json
        todo_file = Path('.bapXcoder/users') / user_id / 'todo.json'

        last_task = 'no specific task'
        last_action = 'no action recorded'
        pending_tasks = []

        # Read session state from sessiontree.json
        if sessiontree_file.exists():
            with open(sessiontree_file, 'r') as f:
                sessiontree_data = json.load(f)

            # Extract session information from sessiontree
            last_task = sessiontree_data.get('last_task', 'no specific task')
            last_action = sessiontree_data.get('last_action', 'no action recorded')

        # Read intent from todo.json
        if todo_file.exists():
            with open(todo_file, 'r') as f:
                todo_data = json.load(f)

            # Extract pending tasks from todo list
            if isinstance(todo_data, list):
                pending_tasks = [todo.get('item', '') for todo in todo_data if not todo.get('completed', False)]
            elif isinstance(todo_data, dict) and 'todos' in todo_data:
                pending_tasks = [todo.get('item', '') for todo in todo_data.get('todos', []) if not todo.get('completed', False)]

        # Create continuation message
        if pending_tasks:
            pending_tasks_str = ", ".join(pending_tasks[:3])  # Limit to first 3 tasks
            if len(pending_tasks) > 3:
                pending_tasks_str += f", and {len(pending_tasks) - 3} more"
            else:
                pending_tasks_str = pending_tasks_str or 'none'

            message = (f"System resumed. You were working on {last_task}. "
                       f"Last action was {last_action}. Pending tasks: {pending_tasks_str}.")
        else:
            message = (f"System resumed. You were working on {last_task}. "
                       f"Last action was {last_action}. No pending tasks.")

        return message

    except Exception as e:
        print(f"Error checking session continuity for user {user_id}: {e}")
        return None

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        # Check if user has proper authentication
        auth_required = os.getenv('AUTH_REQUIRED', 'false').lower() == 'true'
        if auth_required and not is_user_authenticated():
            emit('auth_required', {'msg': 'Authentication required to access IDE features'})
        else:
            emit('status', {'msg': 'Connected to bapXcoder IDE'})

            # Check subscription status and emit to client
            auth_header = request.headers.get('Authorization', '').replace('Bearer ', '')
            if auth_header:
                try:
                    payload = jwt.decode(auth_header, os.environ.get('SECRET_KEY', 'default_secret_key'), algorithms=['HS256'])
                    user_id = payload.get('user_id', 'anonymous')
                    user_subscription = check_user_subscription_status(user_id)

                    emit('subscription_info', {
                        'type': user_subscription['type'],
                        'expires': user_subscription['expires'],
                        'days_left': user_subscription['days_left']
                    })

                    # Check session continuity for returning users
                    session_continuity_message = check_user_session_continuity(user_id)
                    if session_continuity_message:
                        emit('session_continuity', {'message': session_continuity_message})

                    # If it's a trial user, emit daily validation reminder
                    if user_subscription['type'] == 'trial':
                        emit('trial_reminder', {
                            'days_left': user_subscription['days_left'],
                            'expires': user_subscription['expires'],
                            'message': f"Trial expires in {user_subscription['days_left']} days. Renew subscription to continue using all features."
                        })
                except:
                    pass  # If token invalid, just continue without subscription info

    # Initialize multi-agent system
    multi_agent_system = None

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        global multi_agent_system
        if multi_agent_system is None:
            from multi_agent import MultiAgentSystem
            multi_agent_system = MultiAgentSystem(model_runner)

        # Check if user has proper authentication
        auth_required = os.getenv('AUTH_REQUIRED', 'false').lower() == 'true'
        if auth_required and not is_user_authenticated():
            emit('auth_required', {'msg': 'Authentication required to access IDE features'})
        else:
            emit('status', {'msg': 'Connected to bapXcoder IDE'})

            # Check subscription status and emit to client
            auth_header = request.headers.get('Authorization', '').replace('Bearer ', '')
            if auth_header:
                try:
                    payload = jwt.decode(auth_header, os.environ.get('SECRET_KEY', 'default_secret_key'), algorithms=['HS256'])
                    user_id = payload.get('user_id', 'anonymous')
                    user_subscription = check_user_subscription_status(user_id)

                    emit('subscription_info', {
                        'type': user_subscription['type'],
                        'expires': user_subscription['expires'],
                        'days_left': user_subscription['days_left']
                    })

                    # Check session continuity for returning users
                    session_continuity_message = check_user_session_continuity(user_id)
                    if session_continuity_message:
                        emit('session_continuity', {'message': session_continuity_message})

                    # If it's a trial user, emit daily validation reminder
                    if user_subscription['type'] == 'trial':
                        emit('trial_reminder', {
                            'days_left': user_subscription['days_left'],
                            'expires': user_subscription['expires'],
                            'message': f"Trial expires in {user_subscription['days_left']} days. Renew subscription to continue using all features."
                        })
                except:
                    pass  # If token invalid, just continue without subscription info

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle chat messages from the frontend with multi-agent architecture"""
        message = data.get('message', '')
        has_file = data.get('hasFile', False)
        file_name = data.get('fileName', '')
        file_type = data.get('fileType', '')
        continue_reasoning = data.get('continue_reasoning', False)
        conversation_history = data.get('history', [])
        use_multi_agent = data.get('use_multi_agent', False)  # New flag to enable multi-agent processing

        # Get user ID from the authentication token
        auth_header = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = None
        if auth_header:
            try:
                payload = jwt.decode(auth_header, os.environ.get('SECRET_KEY', 'default_secret_key'), algorithms=['HS256'])
                user_id = payload.get('user_id')
            except:
                pass  # If token invalid, user_id remains None

        # If there's a file attachment, handle appropriately
        if has_file and file_type.startswith('image/'):
            # Handle image analysis request with vision capabilities
            message = f"[Image Analysis Request] The user has attached an image: {file_name}. {message}"
            if continue_reasoning and conversation_history:
                context = build_context_from_history(conversation_history)
                full_prompt = f"{context}\n\nUser: {message}\nAssistant:"
                response = model_runner.run_interpreter_prompt(full_prompt, args.max_tokens)
            else:
                response = model_runner.run_interpreter_prompt(message, args.max_tokens)
        elif has_file:
            # Handle other file types
            message = f"[File Analysis Request] The user has attached a file: {file_name}. {message}"

            # Detect if this is a coding-related request for proper routing
            is_coding_task = any(keyword in message.lower() for keyword in [
                'code', 'function', 'class', 'implement', 'create', 'generate',
                'write', 'debug', 'fix', 'refactor', 'test', 'program', 'script',
                'algorithm', 'method', 'variable', 'syntax', 'error'
            ])

            if is_coding_task:
                if continue_reasoning and conversation_history:
                    context = build_context_from_history(conversation_history)
                    full_prompt = f"{context}\n\nUser: {message}\nAssistant:"
                    response = model_runner.run_coding_task(full_prompt, args.max_tokens)
                else:
                    response = model_runner.run_coding_task(message, args.max_tokens)
            else:
                if continue_reasoning and conversation_history:
                    context = build_context_from_history(conversation_history)
                    full_prompt = f"{context}\n\nUser: {message}\nAssistant:"
                    response = model_runner.run_interpreter_prompt(full_prompt, args.max_tokens)
                else:
                    response = model_runner.run_interpreter_prompt(message, args.max_tokens)
        else:
            # No file attachment - handle text-only request
            if use_multi_agent and multi_agent_system:
                # Use multi-agent system for complex tasks (like Trae.ai SOLO)
                emit('status', {'msg': 'bapXcoder is coordinating multiple specialized agents...'})

                # Run coordinated task using multiple simulated agents
                project_path = get_current_project_path() or str(Path.cwd())
                project_context = f"Current project: {project_path}"

                coordinated_result = multi_agent_system.run_coordinated_task(message, project_context)

                response = f"## Multi-Agent Analysis\n\n"
                response += f"**Task**: {coordinated_result['task']}\n\n"

                for step in coordinated_result['steps']:
                    response += f"### {step['step'].title()} Agent Result:\n"
                    response += f"{step['result']}\n\n"

                response += f"**Final Result**: {coordinated_result['final_result'][:500]}..."
            else:
                # Detect if this is a coding-related request for proper routing
                is_coding_task = any(keyword in message.lower() for keyword in [
                    'code', 'function', 'class', 'implement', 'create', 'generate',
                    'write', 'debug', 'fix', 'refactor', 'test', 'program', 'script',
                    'algorithm', 'method', 'variable', 'syntax', 'error'
                ])

                if is_coding_task:
                    if continue_reasoning and conversation_history:
                        context = build_context_from_history(conversation_history)
                        full_prompt = f"{context}\n\nUser: {message}\nAssistant:"
                        response = model_runner.run_coding_task(full_prompt, args.max_tokens)
                    else:
                        response = model_runner.run_coding_task(message, args.max_tokens)
                else:
                    if continue_reasoning and conversation_history:
                        context = build_context_from_history(conversation_history)
                        full_prompt = f"{context}\n\nUser: {message}\nAssistant:"
                        response = model_runner.run_interpreter_prompt(full_prompt, args.max_tokens)
                    else:
                        response = model_runner.run_interpreter_prompt(message, args.max_tokens)

        # Store conversation and update session continuity data if user authenticated
        if user_id:
            project_path = get_current_project_path() or str(Path.cwd())

            # Update session state and memory in sessiontree.json
            sessiontree_data = {
                'last_task': message[:100] + '...' if len(message) > 100 else message,  # Truncate long tasks
                'last_action': 'chat_message_processed',
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }

            # Also store the full conversation data
            conversation_data = {
                'messages': conversation_history,
                'last_message': message,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }

            # Store both session state/memory and conversation data
            store_sessiontree_data(project_path, user_id, sessiontree_data)
            store_session_locally(project_path, user_id, conversation_data)

        emit('chat_response', {'response': response})

    @socketio.on('multi_agent_request')
    def handle_multi_agent_request(data):
        """Handle explicit multi-agent requests (like Trae.ai SOLO)"""
        try:
            task_description = data.get('task', '')
            agent_type = data.get('agent_type', 'coordinated')  # 'coordinated', 'planner', 'coder', etc.

            if not task_description:
                emit('chat_response', {'response': 'Please provide a task description for the multi-agent system.'})
                return

            if not multi_agent_system:
                emit('chat_response', {'response': 'Multi-agent system not initialized.'})
                return

            if agent_type == 'coordinated':
                # Run coordinated task using multiple simulated agents
                project_path = get_current_project_path() or str(Path.cwd())
                project_context = f"Current project: {project_path}"

                coordinated_result = multi_agent_system.run_coordinated_task(task_description, project_context)

                response = f"Multi-Agent Analysis by bapXcoder\n\n"
                response += f"**Task**: {coordinated_result['task']}\n\n"

                for step in coordinated_result['steps']:
                    response += f"### {step['step'].title()} Agent Result:\n"
                    response += f"{step['result']}\n\n"

                response += f"**Final Result Summary**: {coordinated_result['final_result'][:500]}..."

            else:
                # Create a specific type of agent
                from multi_agent import AgentType
                agent_type_enum = AgentType.CODER  # default

                if agent_type == 'planner':
                    agent_type_enum = AgentType.PLANNER
                elif agent_type == 'coder':
                    agent_type_enum = AgentType.CODER
                elif agent_type == 'researcher':
                    agent_type_enum = AgentType.RESEARCHER
                elif agent_type == 'tester':
                    agent_type_enum = AgentType.TESTER
                elif agent_type == 'debugger':
                    agent_type_enum = AgentType.DEBUGGER
                elif agent_type == 'analyzer':
                    agent_type_enum = AgentType.ANALYZER
                else:
                    emit('chat_response', {'response': f'Invalid agent type: {agent_type}. Use one of: coordinated, planner, coder, researcher, tester, debugger, analyzer'})
                    return

                project_path = get_current_project_path() or str(Path.cwd())
                project_context = f"Current project: {project_path}"

                agent_id = multi_agent_system.create_agent(agent_type_enum, task_description, project_context)
                result = multi_agent_system.execute_agent_task(agent_id, task_description)

                response = f"{agent_type_enum.value.title()} Agent Result\n\n"
                response += f"**Task**: {task_description}\n\n"
                response += f"**Result**:\n{result}"

                # Add agent status info
                status = multi_agent_system.get_agent_status(agent_id)
                if 'error' not in status:
                    response += f"\n\n*Agent Status: {status['status']}*"

            emit('chat_response', {'response': response})

        except Exception as e:
            error_msg = f"Error in multi-agent processing: {str(e)}"
            print(f"Multi-Agent System Error: {error_msg}")
            emit('chat_response', {'response': error_msg})

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

    @socketio.on('validate_file')
    def handle_validate_file(data):
        """Validate a file with AI-driven testing"""
        file_path = data.get('file_path', '')
        run_tests = data.get('run_tests', False)

        if not project_explorer:
            emit('validation_error', {'message': 'Project explorer not initialized'})
            return

        try:
            # Create full path relative to project
            full_path = project_explorer.project_path / file_path

            # Check if file exists
            if not full_path.exists():
                emit('validation_error', {'message': f'File does not exist: {file_path}'})
                return

            # Import validation system
            from validation_system import AITestRunner

            # Initialize the AI test runner if not already done
            global ai_test_runner
            if 'ai_test_runner' not in globals():
                ai_test_runner = AITestRunner(project_explorer.project_path)

            # Run individual file validation
            result = ai_test_runner.run_individual_file_tests(str(full_path))

            emit('validation_result', {
                'file_path': file_path,
                'validation_result': result['validation_result'],
                'ai_analysis': result['ai_analysis'],
                'test_summary': result['test_summary'],
                'timestamp': result['timestamp'],
                'success': True
            })
        except Exception as e:
            emit('validation_error', {'message': f'Error validating file: {str(e)}'})

    @socketio.on('validate_project')
    def handle_validate_project(data):
        """Validate the entire project with AI-driven testing"""
        if not project_explorer:
            emit('validation_error', {'message': 'Project explorer not initialized'})
            return

        try:
            # Import validation system
            from validation_system import AITestRunner

            # Initialize the AI test runner if not already done
            global ai_test_runner
            if 'ai_test_runner' not in globals():
                ai_test_runner = AITestRunner(project_explorer.project_path)

            # Run project-wide validation
            result = ai_test_runner.run_project_wide_tests()

            emit('project_validation_result', {
                'results': result,
                'success': True
            })
        except Exception as e:
            emit('validation_error', {'message': f'Error validating project: {str(e)}'})

    @socketio.on('add_todo')
    def handle_add_todo(data):
        """Handle adding a todo item with GitHub sync"""
        todo_item = data.get('todo', '')

        # Get user ID from the authentication token
        auth_header = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = None
        if auth_header:
            try:
                payload = jwt.decode(auth_header, os.environ.get('SECRET_KEY', 'default_secret_key'), algorithms=['HS256'])
                user_id = payload.get('user_id')
            except:
                pass  # If token invalid, user_id remains None

        if user_id:
            project_path = get_current_project_path() or str(Path.cwd())
            todo_data = {
                'item': todo_item,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'completed': False
            }
            success = store_todo_locally(project_path, user_id, todo_data)

            if success:
                # Update user-specific session tree with todo
                user_session_dir = Path(project_path) / '.bapXcoder' / 'users' / user_id
                user_session_dir.mkdir(parents=True, exist_ok=True)

                session_tree_path = user_session_dir / 'sessiontree.json'
                if session_tree_path.exists():
                    with open(session_tree_path, 'r') as f:
                        session_data = json.load(f)
                else:
                    session_data = {}

                if 'todos' not in session_data:
                    session_data['todos'] = []

                session_data['todos'].append(todo_data)

                with open(session_tree_path, 'w') as f:
                    json.dump(session_data, f, indent=2)

        emit('todo_added', {'success': True, 'todo': todo_item})

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

    @socketio.on('web_search')
    def handle_web_search(data):
        """Handle web search requests with Antigravity-inspired research capabilities"""
        query = data.get('query', '')
        if not query:
            emit('chat_response', {'response': 'Please provide a search query.'})
            return

        try:
            from web_search import AntigravityWebResearch
            research_agent = AntigravityWebResearch()

            # Conduct research using the Antigravity-inspired system
            results = research_agent.conduct_research(query)

            # Format results for the chat interface
            response = f"Web Research Results for: '{query}'\n\n"

            if results and results.get('findings'):
                for finding in results['findings']:
                    response += f"{finding['results']}\n"
            else:
                response += "No results found. The search may have failed due to missing API keys.\n"
                response += "To enable web search, set your TAVILY_API_KEY environment variable.\n"

            if results and results.get('conclusion'):
                response += f"\nConclusion: {results['conclusion']}"

            emit('chat_response', {'response': response})
        except ImportError as e:
            # Fallback if web_search module is not available
            response = f"Web Search for: '{query}'\n\n"
            response += "Web search functionality requires the web_search module.\n"
            response += "To enable full web search capabilities:\n"
            response += "1. pip install requests\n"
            response += "2. Set TAVILY_API_KEY environment variable (free API key available at tavily.com)\n"
            response += f"\nFor now, I can't perform this search without the required dependencies. Error: {str(e)}"
            emit('chat_response', {'response': response})
        except Exception as e:
            response = f"Web Search for: '{query}'\n\n"
            response += f"Error performing web search: {str(e)}\n"
            response += "\nMake sure you have a valid API key set in your environment variables."
            emit('chat_response', {'response': response})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
        # Remove from online users if present
        disconnected_user = None
        for user in online_users:
            if user[2] == request.sid:  # Check if session ID matches
                disconnected_user = user
                break
        if disconnected_user:
            online_users.remove(disconnected_user)
            emit_online_count()

    print(f"Starting bapXcoder AI Development Environment with dual-model architecture (Interpreter + Developer) at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    socketio.run(app, host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
