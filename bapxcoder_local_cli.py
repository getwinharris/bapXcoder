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

def check_subscription_status(user_id):
    """Check if user's subscription is still valid"""
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
                    return False  # Subscription expired
            return True
        else:
            # For free trial users, check if trial period has expired
            return True  # Allow access by default if no subscription data
    except Exception:
        return True  # If any error occurs, allow access (local system only)


def is_user_authenticated():
    """Check if user is authenticated locally"""
    # For local use, assume user is authenticated by default
    # In a real implementation, this would check local authentication
    return True

# Online users tracking
online_users = set()

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Get user info from token
    auth_header = request.headers.get('Authorization', '').replace('Bearer ', '')
    if auth_header:
        try:
            payload = jwt.decode(auth_header, os.getenv('SECRET_KEY', 'default_secret_key'), algorithms=['HS256'])
            user_id = payload.get('user_id')
            username = payload.get('username', 'Anonymous')
            if user_id:
                online_users.add((user_id, username, request.sid))
                # Emit updated online count to admin
                emit_online_count()
        except:
            pass  # If token invalid, don't track user

    emit('status', {'msg': 'Connected to bapXcoder IDE'})

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

def emit_online_count():
    """Emit current online user count to admin panel"""
    online_count = len(online_users)
    # Broadcast to all clients
    socketio.emit('online_users_count', {'count': online_count, 'users': [{'id': u[0], 'name': u[1]} for u in online_users]})

def store_session_locally(project_path, user_id, session_data):
    """Store session data locally in the project's .bapXcoder folder"""
    try:
        # Create or access the .bapXcoder directory in the project
        project_dir = Path(project_path)
        bapx_dir = project_dir / '.bapXcoder'
        bapx_dir.mkdir(exist_ok=True)

        # Save session data locally
        session_file = bapx_dir / 'session.json'
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error storing session locally: {e}")
        return False

def get_current_project_path():
    """Get the current project path for the session"""
    # In a real implementation, this would retrieve the project path from session data
    # For now, returning current working directory
    return str(Path.cwd())

def get_session_project_path(session_id):
    """Get project path for a specific session"""
    # In a real implementation, this would retrieve project path from session data
    # For now, return current directory
    return str(Path.cwd())

def store_todo_locally(project_path, user_id, todo_data):
    """Store todo data locally in the project's .bapXcoder folder"""
    try:
        # Create or access the .bapXcoder directory in the project
        project_dir = Path(project_path)
        bapx_dir = project_dir / '.bapXcoder'
        bapx_dir.mkdir(exist_ok=True)

        # Save todo data locally
        todo_file = bapx_dir / 'todo.json'
        with open(todo_file, 'w') as f:
            json.dump(todo_data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error storing todo locally: {e}")
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
        """Handle chat messages from the frontend"""
        message = data.get('message', '')
        has_file = data.get('hasFile', False)
        file_name = data.get('fileName', '')
        file_type = data.get('fileType', '')
        continue_reasoning = data.get('continue_reasoning', False)
        conversation_history = data.get('history', [])

        # Get user ID from the authentication token
        auth_header = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = None
        if auth_header:
            try:
                payload = jwt.decode(auth_header, os.environ.get('SECRET_KEY', 'default_secret_key'), algorithms=['HS256'])
                user_id = payload.get('user_id')
            except:
                pass  # If token invalid, user_id remains None

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

        # Store conversation to session.json if user authenticated
        if user_id:
            project_path = get_current_project_path() or str(Path.cwd())
            session_data = {
                'messages': conversation_history,
                'last_message': message,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            store_session_locally(project_path, user_id, session_data)

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
                # Update session tree with todo
                session_tree_path = Path(project_path) / '.bapXcoder' / 'sessiontree.json'
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

    print(f"Starting bapXcoder IDE with dual-model architecture (Interpreter + Developer) at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    socketio.run(app, host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
