# Google OAuth Setup Guide

## Environment Variables Required

Add these variables to your `.env` file:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/google/callback

# MongoDB Configuration (you already have these)
MONGO_USERNAME=your_mongo_username
MONGO_PASSWORD=your_mongo_password
MONGO_CLUSTER=your_mongo_cluster
MONGO_DATABASE=your_mongo_database
```

## Google OAuth Setup Steps

1. **Go to Google Cloud Console**
   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google+ API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application" as the application type

4. **Configure OAuth Consent Screen**
   - Add your app name and user support email
   - Add authorized domains (localhost for development)
   - Add scopes: `openid`, `email`, `profile`

5. **Add Authorized Redirect URIs**
   - For development: `http://localhost:5000/api/auth/google/callback`
   - For production: `https://yourdomain.com/api/auth/google/callback`

6. **Copy Credentials**
   - Copy the Client ID and Client Secret
   - Add them to your `.env` file

## Installation

Install the new dependencies:

```bash
pip install -r requirements.txt
```

## Testing

1. Start your backend server
2. Start your frontend development server
3. Go to the login page
4. Click "Continue with Google"
5. Complete the Google OAuth flow

## Features Added

- ✅ Google OAuth authentication
- ✅ User profile picture from Google
- ✅ Automatic user creation for new Google users
- ✅ Support for both local and Google authentication
- ✅ Secure token-based authentication
- ✅ MongoDB integration for user storage

## Security Notes

- Google OAuth tokens are handled securely
- User passwords are hashed for local authentication
- JWT tokens are used for session management
- All sensitive data is stored in environment variables 