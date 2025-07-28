from .app import app

# Vercel entry point - the app is already created in app.py
# This file serves as the entry point for Vercel deployment

# For local development
if __name__ == "__main__":
    app.run(debug=True)
