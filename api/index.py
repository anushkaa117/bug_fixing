from flask import Flask
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create Flask app for Vercel
app = create_app('production')

# Vercel serverless function handler
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)
