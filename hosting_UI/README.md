# bapXcoder Frontend Hosting

This directory contains the frontend hosting files for the bapXcoder IDE, designed to be deployed on Hostinger or any hosting provider that supports static files and simple backend services.

## Architecture Overview

The bapXcoder project uses a dual-architecture approach:
- **Frontend/Authentication Server** (hosted on Hostinger): Handles authentication, payments, and serves the web interface
- **Local Application** (downloaded by users): Contains the full IDE functionality with local AI processing

This approach allows us to:
1. Manage subscriptions and user authentication through the frontend server
2. Store user metadata in encrypted form in GitHub repositories
3. Distribute the actual IDE application without storing user files on our servers
4. Keep user code completely local and private

## Deployment Instructions

### On Hostinger (Production)

1. Create a new Node.js application on Hostinger
2. Upload all files in this directory
3. Set environment variables (see `.env.example`)
4. Configure domain to point to `coder.bapx.in`

### Required Environment Variables

- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`: For GitHub OAuth
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: For Google OAuth  
- `STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY`: For payment processing
- `SECRET_KEY`: For session management
- `GITHUB_TOKEN`: To access user data repository

### GitHub Repository Setup

The authentication server will store encrypted user subscription data in GitHub repositories, not on our servers. Each user's subscription data is encrypted and stored in a public GitHub repository (because it only contains encrypted data).

## Frontend Structure

- `docs/` - Landing page, documentation, and marketing materials
- `templates/` - Web UI templates for authentication and dashboard
- `bapXcoder_frontend.py` - Authentication and payment processing server
- `static/` - CSS, JavaScript, images, and other static resources
- `config.ini` - Configuration settings

## Security Model

1. User authentication handled via GitHub/Google OAuth
2. Payment processing via Stripe
3. User subscription data stored encrypted in public GitHub repositories
4. Actual IDE application remains completely local after download
5. All user code stays on user's machine, never transmitted to servers

## Subscription Plans

- **Free Trial**: 60 days access to all features
- **Monthly Plan**: $1/month for continued access
- **Lifetime Plan**: $100 one-time for unlimited access

## Admin Panel

The admin panel at `/admin` allows administrators to:
- View user statistics
- Track downloads and subscriptions
- Configure API keys and settings
- Monitor system health

## Development

To run locally for development:
```bash
pip install -r requirements.txt
python bapXcoder_frontend.py
```

Navigate to `http://localhost:5000` to access the frontend.

## Key Features

- GitHub and Google OAuth authentication
- Stripe payment integration
- Encrypted user data storage in GitHub
- Download tracking and analytics
- Admin dashboard for monitoring
- Mobile-responsive design
- PWA capabilities