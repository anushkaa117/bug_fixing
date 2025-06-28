#!/usr/bin/env python3
"""
Enhanced MongoDB Atlas Connection Test
Tests connection with various SSL/TLS configurations
"""

import os
import urllib.parse
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import ssl

def main():
    print("Enhanced MongoDB Atlas Connection Test")
    print("=" * 45)
    
    # Load environment
    load_dotenv()
    
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    cluster = os.getenv('MONGO_CLUSTER')
    database = os.getenv('MONGO_DATABASE', 'test')
    
    print(f"Username: {username}")
    print(f"Cluster: {cluster}")
    print(f"Database: {database}")
    print(f"Password: {'*' * len(password) if password else 'Not set'}")
    
    # Test different connection configurations
    test_configs = [
        {
            'name': 'Standard Connection (with ServerApi)',
            'uri': f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0",
            'options': {'server_api': ServerApi('1')}
        },
        {
            'name': 'Connection without ServerApi',
            'uri': f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0",
            'options': {}
        },
        {
            'name': 'Connection with SSL disabled (not recommended)',
            'uri': f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority&ssl=false&appName=Cluster0",
            'options': {}
        },
        {
            'name': 'Connection with explicit SSL settings',
            'uri': f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true&appName=Cluster0",
            'options': {}
        }
    ]
    
    successful_config = None
    
    for config in test_configs:
        print(f"\n[TEST] {config['name']}")
        print("-" * 50)
        
        try:
            # Create client with timeout
            client = MongoClient(
                config['uri'], 
                serverSelectionTimeoutMS=10000,  # 10 second timeout
                connectTimeoutMS=10000,
                **config['options']
            )
            
            # Test connection
            client.admin.command('ping')
            print("SUCCESS: Connection successful!")
            
            # Get database info
            db_names = client.list_database_names()
            print(f"Available databases: {db_names}")
            
            # Test specific database
            db = client[database]
            collections = db.list_collection_names()
            print(f"Collections in '{database}': {collections if collections else 'None (empty database)'}")
            
            successful_config = config
            client.close()
            break
            
        except Exception as e:
            print(f"FAILED: Connection failed: {str(e)[:100]}...")
            continue
    
    if successful_config:
        print(f"\n[SUCCESS] Working configuration:")
        print(f"   {successful_config['name']}")
        print(f"\n[INFO] Connection Details:")
        print(f"   URI: {successful_config['uri'][:60]}...")
        print(f"   Options: {successful_config['options']}")
        
        # Test with sample operation
        print(f"\n[TEST] Testing sample operations...")
        try:
            client = MongoClient(
                successful_config['uri'], 
                serverSelectionTimeoutMS=10000,
                **successful_config['options']
            )
            
            db = client[database]
            
            # Insert a test document
            test_collection = db['connection_test']
            test_doc = {'test': 'connection', 'timestamp': '2025-06-28'}
            result = test_collection.insert_one(test_doc)
            print(f"SUCCESS: Test document inserted with ID: {result.inserted_id}")
            
            # Read the document back
            found_doc = test_collection.find_one({'_id': result.inserted_id})
            print(f"SUCCESS: Test document retrieved: {found_doc}")
            
            # Clean up test document
            test_collection.delete_one({'_id': result.inserted_id})
            print(f"SUCCESS: Test document cleaned up")
            
            client.close()
            
        except Exception as e:
            print(f"FAILED: Sample operations failed: {e}")
    
    else:
        print(f"\n[FAILED] All connection attempts failed!")
        print(f"\n[HELP] Troubleshooting suggestions:")
        print(f"   1. Check MongoDB Atlas cluster status")
        print(f"   2. Verify IP whitelist (add 0.0.0.0/0 for testing)")
        print(f"   3. Confirm username/password are correct")
        print(f"   4. Check if database user has proper permissions")
        print(f"   5. Try connecting from MongoDB Compass first")

if __name__ == "__main__":
    main()
