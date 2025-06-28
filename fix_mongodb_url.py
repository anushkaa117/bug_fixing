#!/usr/bin/env python3
"""
MongoDB URL Fixer
Helps fix MongoDB connection strings with special characters in passwords
"""

import urllib.parse
import os
from dotenv import load_dotenv

def fix_mongodb_url():
    """Fix MongoDB URL by properly encoding special characters"""
    
    load_dotenv()
    current_url = os.getenv('DATABASE_URL')
    
    if not current_url:
        print("No DATABASE_URL found in .env file")
        return
    
    print("Current DATABASE_URL:")
    print(current_url)
    print()
    
    # Extract components from the URL
    if 'mongodb+srv://' in current_url:
        # Remove the protocol
        url_without_protocol = current_url.replace('mongodb+srv://', '')
        
        # Split by @ to separate credentials from host
        if '@' in url_without_protocol:
            parts = url_without_protocol.split('@', 1)
            credentials = parts[0]
            host_and_params = parts[1]
            
            if ':' in credentials:
                username, password = credentials.split(':', 1)
                
                print(f"Username: {username}")
                print(f"Original Password: {password}")
                
                # URL encode the password
                encoded_password = urllib.parse.quote_plus(password)
                
                print(f"Encoded Password: {encoded_password}")
                
                # Reconstruct the URL
                fixed_url = f"mongodb+srv://{username}:{encoded_password}@{host_and_params}"
                
                print()
                print("Fixed DATABASE_URL:")
                print(fixed_url)
                print()
                print("Please update your .env file with the fixed URL above.")
                
                return fixed_url
    
    print("Could not parse the MongoDB URL. Please check the format.")
    return None

if __name__ == "__main__":
    print("MongoDB URL Fixer")
    print("=" * 30)
    fix_mongodb_url()
