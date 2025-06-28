#!/usr/bin/env python3
"""
Simple MongoDB Connection Test
Using the exact pattern provided by the user
"""

import os
import urllib.parse
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def main():
    print("Simple MongoDB Connection Test")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    cluster = os.getenv('MONGO_CLUSTER')
    
    print(f"Username: {username}")
    print(f"Cluster: {cluster}")
    print(f"Password: {'*' * len(password) if password else 'Not set'}")
    
    # URL encode the password to handle special characters like @@
    encoded_password = urllib.parse.quote_plus(password)
    print(f"Encoded Password: {'*' * len(encoded_password)}")
    
    # Build URI with encoded password
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"\nConnection URI: {uri[:50]}...")
    
    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        # List all available databases
        print("\nAvailable databases:")
        db_list = client.list_database_names()
        for db in db_list:
            print(f"  - {db}")
        
        # Get default database info
        try:
            default_db = client.get_default_database()
            print(f"\nDefault database: {default_db.name}")
            
            # List collections in default database
            collections = default_db.list_collection_names()
            if collections:
                print(f"Collections in {default_db.name}:")
                for col in collections:
                    print(f"  - {col}")
            else:
                print(f"No collections in {default_db.name} (empty database)")
        except Exception as e:
            print(f"Could not access default database: {e}")
        
        client.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if your MongoDB Atlas cluster is running")
        print("2. Verify username and password are correct")
        print("3. Check if your IP address is whitelisted in MongoDB Atlas")
        print("4. Ensure the database user has proper permissions")

if __name__ == "__main__":
    main()
