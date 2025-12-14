#!/usr/bin/env python3
"""
Authentication and Payment System for bapXcoder
Handles GitHub/Google OAuth, Stripe payments, and user data management
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session, jsonify, render_template_string
from functools import wraps
import stripe
import requests

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_dev_secret_key')

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key_here')

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', 'your_github_client_id')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', 'your_github_client_secret')

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your_google_client_id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your_google_client_secret')

# Data file for user data and subscriptions
USERS_DATA_FILE = '.IDEbapXcoder/users_data.json'
DOWNLOAD_STATS_FILE = '.IDEbapXcoder/download_stats.json'

def init_data_files():
    """Initialize data files if they don't exist"""
    os.makedirs(os.path.dirname(USERS_DATA_FILE), exist_ok=True)
    
    # Initialize users data file
    if not os.path.exists(USERS_DATA_FILE):
        with open(USERS_DATA_FILE, 'w') as f:
            json.dump({'users': {}, 'subscriptions': {}, 'downloads': {}}, f, indent=2)
    
    # Initialize download stats file
    if not os.path.exists(DOWNLOAD_STATS_FILE):
        with open(DOWNLOAD_STATS_FILE, 'w') as f:
            json.dump({
                'total_downloads': 0,
                'monthly_downloads': {},
                'user_downloads': {}
            }, f, indent=2)

def load_users_data():
    """Load users data from JSON file"""
    try:
        with open(USERS_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'users': {}, 'subscriptions': {}, 'downloads': {}}

def save_users_data(data):
    """Save users data to JSON file"""
    with open(USERS_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_download_stats():
    """Load download statistics"""
    try:
        with open(DOWNLOAD_STATS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            'total_downloads': 0,
            'monthly_downloads': {},
            'user_downloads': {}
        }

def save_download_stats(stats):
    """Save download statistics"""
    with open(DOWNLOAD_STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'provider' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/auth/login')
def login():
    """Login endpoint"""
    provider = request.args.get('provider', 'github')
    if provider == 'github':
        # Redirect to GitHub OAuth
        github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri=http://localhost:7860/callback/github&scope=user:email"
        return redirect(github_auth_url)
    elif provider == 'google':
        # Redirect to Google OAuth
        google_auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:7860/callback/google&response_type=code&scope=profile email"
        return redirect(google_auth_url)
    else:
        return jsonify({'error': 'Invalid provider'}), 400

@app.route('/callback/<provider>')
def oauth_callback(provider):
    """OAuth callback handler"""
    code = request.args.get('code')
    
    if provider == 'github' and code:
        # Exchange code for access token
        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': 'http://localhost:7860/callback/github'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if access_token:
            # Get user info from GitHub
            user_response = requests.get('https://api.github.com/user', 
                                       headers={'Authorization': f'token {access_token}'})
            user_data = user_response.json()
            
            user_id = user_data.get('id')
            email = user_data.get('email') or user_data.get('login') + '@github.com'
            name = user_data.get('name') or user_data.get('login')
            
            # Store user session
            session['user_id'] = user_id
            session['provider'] = 'github'
            session['email'] = email
            
            # Update user data
            users_data = load_users_data()
            if str(user_id) not in users_data['users']:
                users_data['users'][str(user_id)] = {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'provider': 'github',
                    'created_at': datetime.now().isoformat(),
                    'subscription_plan': 'free_trial',
                    'trial_start': datetime.now().isoformat(),
                    'trial_end': (datetime.now() + timedelta(days=60)).isoformat(),  # 60 day trial
                    'download_count': 0
                }
                save_users_data(users_data)
            
            return redirect('/dashboard')
    
    elif provider == 'google' and code:
        # Exchange code for access token with Google
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:7860/callback/google'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if access_token:
            # Get user info from Google
            user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                                       headers={'Authorization': f'Bearer {access_token}'})
            user_data = user_response.json()
            
            user_id = user_data.get('id')
            email = user_data.get('email')
            name = user_data.get('name')
            
            # Store user session
            session['user_id'] = user_id
            session['provider'] = 'google'
            session['email'] = email
            
            # Update user data
            users_data = load_users_data()
            if str(user_id) not in users_data['users']:
                users_data['users'][str(user_id)] = {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'provider': 'google',
                    'created_at': datetime.now().isoformat(),
                    'subscription_plan': 'free_trial',
                    'trial_start': datetime.now().isoformat(),
                    'trial_end': (datetime.now() + timedelta(days=60)).isoformat(),  # 60 day trial
                    'download_count': 0
                }
                save_users_data(users_data)
            
            return redirect('/dashboard')
    
    return jsonify({'error': 'OAuth failed'}), 400

@app.route('/dashboard')
@require_auth
def dashboard():
    """User dashboard"""
    users_data = load_users_data()
    user_id = session['user_id']
    
    if str(user_id) in users_data['users']:
        user_info = users_data['users'][str(user_id)]
        return jsonify({
            'user': user_info,
            'subscription_status': check_subscription_status(user_info)
        })
    else:
        return jsonify({'error': 'User not found'}), 404

def check_subscription_status(user_info):
    """Check user's subscription status"""
    plan = user_info.get('subscription_plan', 'free_trial')
    
    if plan == 'free_trial':
        trial_end = datetime.fromisoformat(user_info.get('trial_end', datetime.now().isoformat()))
        if datetime.now() > trial_end:
            # Trial expired, downgrade to free
            return {'status': 'expired', 'plan': 'expired_trial', 'expires_at': trial_end.isoformat()}
        else:
            # Trial still active
            return {
                'status': 'active',
                'plan': 'free_trial',
                'expires_in_days': (trial_end - datetime.now()).days,
                'expires_at': trial_end.isoformat()
            }
    else:
        # Paid subscription
        sub_end_date = user_info.get('subscription_end_date')
        if sub_end_date:
            end_date = datetime.fromisoformat(sub_end_date)
            if datetime.now() > end_date:
                # Subscription expired
                return {'status': 'expired', 'plan': plan, 'expires_at': end_date.isoformat()}
            else:
                # Subscription active
                return {
                    'status': 'active',
                    'plan': plan,
                    'expires_in_days': (end_date - datetime.now()).days,
                    'expires_at': end_date.isoformat()
                }
        else:
            # Lifetime or no expiration date
            return {'status': 'active', 'plan': plan, 'expires_at': 'never'}

@app.route('/payment/create-checkout-session', methods=['POST'])
@require_auth
def create_checkout_session():
    """Create a Stripe checkout session"""
    data = request.json
    plan_type = data.get('plan_type', 'monthly')  # monthly, annual, lifetime
    
    # Define prices based on plan
    prices = {
        'monthly': {'amount': 100, 'currency': 'usd', 'interval': 'month'},
        'annual': {'amount': 1000, 'currency': 'usd', 'interval': 'year'},
        'lifetime': {'amount': 10000, 'currency': 'usd', 'interval': None}
    }
    
    price_info = prices.get(plan_type)
    if not price_info:
        return jsonify({'error': 'Invalid plan type'}), 400
    
    # Create Stripe checkout session
    try:
        if plan_type == 'lifetime':
            # One-time payment for lifetime
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': price_info['currency'],
                        'product_data': {
                            'name': 'bapXcoder Lifetime Plan',
                            'description': 'Lifetime access to bapXcoder IDE with all features',
                        },
                        'unit_amount': price_info['amount'],
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.url_root + 'payment/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.url_root + 'payment/cancel',
                metadata={
                    'user_id': session['user_id'],
                    'provider': session['provider'],
                    'plan_type': plan_type
                }
            )
        else:
            # Subscription payment
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': price_info['currency'],
                        'product_data': {
                            'name': f'bapXcoder {plan_type.capitalize()} Plan',
                            'description': f'Monthly access to bapXcoder IDE with all features',
                        },
                        'unit_amount': price_info['amount'],
                        'recurring': {
                            'interval': price_info['interval']
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.url_root + 'payment/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.url_root + 'payment/cancel',
                metadata={
                    'user_id': session['user_id'],
                    'provider': session['provider'],
                    'plan_type': plan_type
                }
            )
        
        return jsonify({'id': checkout_session.id, 'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment/success')
def payment_success():
    """Handle successful payment"""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve the session to get metadata
            session_info = stripe.checkout.Session.retrieve(session_id)
            user_id = session_info.metadata.get('user_id')
            plan_type = session_info.metadata.get('plan_type')
            
            # Update user subscription
            users_data = load_users_data()
            if str(user_id) in users_data['users']:
                user_info = users_data['users'][str(user_id)]
                
                if plan_type == 'monthly':
                    user_info['subscription_plan'] = 'monthly'
                    user_info['subscription_end_date'] = (datetime.now() + timedelta(days=30)).isoformat()
                elif plan_type == 'annual':
                    user_info['subscription_plan'] = 'annual'
                    user_info['subscription_end_date'] = (datetime.now() + timedelta(days=365)).isoformat()
                elif plan_type == 'lifetime':
                    user_info['subscription_plan'] = 'lifetime'
                    user_info['subscription_end_date'] = 'never'
                
                save_users_data(users_data)
            
            return jsonify({
                'status': 'success',
                'message': f'Payment successful! Your {plan_type} subscription is now active.',
                'session_id': session_id
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid session ID'}), 400

@app.route('/download')
@require_auth
def download():
    """Handle download requests"""
    users_data = load_users_data()
    download_stats = load_download_stats()
    
    user_id = session['user_id']
    
    # Check subscription status
    if str(user_id) in users_data['users']:
        user_info = users_data['users'][str(user_id)]
        sub_status = check_subscription_status(user_info)
        
        if sub_status['status'] == 'active' or sub_status['plan'] == 'free_trial':
            # Increment download count
            user_info['download_count'] = user_info.get('download_count', 0) + 1
            save_users_data(users_data)
            
            # Update download stats
            download_stats['total_downloads'] += 1
            current_month = datetime.now().strftime('%Y-%m')
            download_stats['monthly_downloads'][current_month] = download_stats['monthly_downloads'].get(current_month, 0) + 1
            download_stats['user_downloads'][str(user_id)] = download_stats['user_downloads'].get(str(user_id), 0) + 1
            save_download_stats(download_stats)
            
            # Return the download URL
            return redirect('https://github.com/getwinharris/bapXcoder/releases/latest/download/install.sh')
        else:
            return jsonify({'error': 'Subscription expired. Please renew your subscription to download.', 'status': 'expired'}), 403
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/admin')
def admin_login():
    """Admin login page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>bapXcoder Admin</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0f0f13;
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
                border-radius: 10px;
                border: 1px solid #2d2d40;
                width: 300px;
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
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Admin Login</h2>
            <form method="POST" action="/admin/authenticate">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/authenticate', methods=['POST'])
def admin_authenticate():
    """Authenticate admin user"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Default admin credentials
    admin_username = os.environ.get('ADMIN_USERNAME', 'getwinharris@gmail.com')
    admin_password_hash = hashlib.sha256(os.environ.get('ADMIN_PASSWORD', 'bapX2025#').encode()).hexdigest()
    
    input_password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if username == admin_username and input_password_hash == admin_password_hash:
        session['admin_logged_in'] = True
        return redirect('/admin/dashboard')
    else:
        return redirect('/admin?error=invalid_credentials')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    users_data = load_users_data()
    download_stats = load_download_stats()
    
    total_users = len(users_data['users'])
    active_subscriptions = 0
    expired_subscriptions = 0
    
    for user_id, user_info in users_data['users'].items():
        sub_status = check_subscription_status(user_info)
        if sub_status['status'] == 'active':
            active_subscriptions += 1
        else:
            expired_subscriptions += 1
    
    return jsonify({
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'total_downloads': download_stats['total_downloads'],
        'monthly_downloads': download_stats['monthly_downloads'],
        'recent_users': list(users_data['users'].values())[:10]  # Last 10 users
    })

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    """Admin settings page for managing credentials"""
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    if request.method == 'POST':
        # Update OAuth and Stripe credentials
        github_client_id = request.form.get('github_client_id')
        github_client_secret = request.form.get('github_client_secret')
        google_client_id = request.form.get('google_client_id')
        google_client_secret = request.form.get('google_client_secret')
        stripe_secret_key = request.form.get('stripe_secret_key')
        
        # In a real implementation, you'd update environment variables or config files
        # For now, we'll just acknowledge in the response
        return jsonify({'status': 'credentials_updated'})
    
    # Return settings form
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Settings</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0f0f13;
                color: #e0e0e0;
                padding: 20px;
            }
            .settings-container {
                max-width: 800px;
                margin: 0 auto;
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
                padding: 12px 24px;
                background: linear-gradient(90deg, #7c5cff 0%, #6a4fd6 100%);
                border: none;
                border-radius: 4px;
                color: white;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="settings-container">
            <h2>Admin Settings</h2>
            <form method="POST">
                <h3>GitHub OAuth Credentials</h3>
                <label>GitHub Client ID:</label>
                <input type="text" name="github_client_id" placeholder="GitHub Client ID">
                <label>GitHub Client Secret:</label>
                <input type="password" name="github_client_secret" placeholder="GitHub Client Secret">
                
                <h3>Google OAuth Credentials</h3>
                <label>Google Client ID:</label>
                <input type="text" name="google_client_id" placeholder="Google Client ID">
                <label>Google Client Secret:</label>
                <input type="password" name="google_client_secret" placeholder="Google Client Secret">
                
                <h3>Stripe API Credentials</h3>
                <label>Stripe Secret Key:</label>
                <input type="password" name="stripe_secret_key" placeholder="Stripe Secret Key">
                
                <button type="submit">Update Credentials</button>
            </form>
        </div>
    </body>
    </html>
    '''

# Initialize data files on startup
init_data_files()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)