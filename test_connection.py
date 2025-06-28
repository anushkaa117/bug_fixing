#!/usr/bin/env python3
"""
Quick MongoDB Connection Test Script
Tests the DATABASE_URL connection before running the full initialization
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection():
    """Test MongoDB connection using DATABASE_URL"""
    
    # Load environment variables
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL not found in .env file")
        print("Please add your MongoDB connection string to .env file:")
        print("DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/database")
        return False
    
    print("Testing MongoDB Connection...")
    print(f"URL: {database_url[:50]}...")
    
    try:
        # Create MongoDB client with timeout
        client = MongoClient(
            database_url, 
            serverSelectionTimeoutMS=10000,  # 10 second timeout
            connectTimeoutMS=10000
        )
        
        # Test the connection
        print("Attempting to connect...")
        client.admin.command('ping')
        
        # Get database info
        db_name = client.get_default_database().name
        server_info = client.server_info()
        
        print("MongoDB Connection Successful!")
        print(f"Database: {db_name}")
        print(f"MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        # List collections (if any)
        collections = client.get_default_database().list_collection_names()
        if collections:
            print(f"Existing Collections: {', '.join(collections)}")
        else:
            print("No existing collections found (fresh database)")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"Connection Failed: {e}")
        print("Check your internet connection and MongoDB credentials")
        return False
        
    except ServerSelectionTimeoutError as e:
        print(f"Server Selection Timeout: {e}")
        print("The MongoDB server might be unreachable or credentials are incorrect")
        return False
        
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False

def main():
    """Main function"""
    print("MongoDB Connection Test")
    print("=" * 40)
    
    if test_mongodb_connection():
        print("\nConnection test passed!")
        print("You can now run: python init_database.py")
    else:
        print("\nConnection test failed!")
        print("Please check your DATABASE_URL in .env file")
        sys.exit(1)

if __name__ == "__main__":
    main()
