#!/usr/bin/env python3
"""
Direct MongoDB Atlas Connection Test
Tests the exact connection string provided by user
"""

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def main():
    print("Direct MongoDB Atlas Connection Test")
    print("=" * 40)
    
    # Your exact connection string
    connection_string = "mongodb+srv://2024081204:anushka@cluster0.fn8yhfs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"Testing connection string:")
    print(f"mongodb+srv://2024081204:***@cluster0.fn8yhfs.mongodb.net/...")
    print()
    
    # Test configurations
    test_configs = [
        {
            'name': 'Direct connection (no ServerApi)',
            'client_args': {
                'host': connection_string,
                'serverSelectionTimeoutMS': 10000
            }
        },
        {
            'name': 'Direct connection (with ServerApi)',
            'client_args': {
                'host': connection_string,
                'server_api': ServerApi('1'),
                'serverSelectionTimeoutMS': 10000
            }
        },
        {
            'name': 'Connection to specific database (it)',
            'client_args': {
                'host': connection_string.replace('/?', '/it?'),
                'serverSelectionTimeoutMS': 10000
            }
        }
    ]
    
    for config in test_configs:
        print(f"[TEST] {config['name']}")
        print("-" * 50)
        
        try:
            # Create client
            client = MongoClient(**config['client_args'])
            
            # Test connection
            result = client.admin.command('ping')
            print(f"SUCCESS: Ping result: {result}")
            
            # List databases
            databases = client.list_database_names()
            print(f"Available databases: {databases}")
            
            # Test 'it' database specifically
            if 'it' in databases:
                db = client['it']
                collections = db.list_collection_names()
                print(f"Collections in 'it' database: {collections}")
                
                # Try to insert a test document
                test_collection = db['test_connection']
                test_doc = {
                    'message': 'Connection test successful',
                    'timestamp': '2025-06-28T11:05:12+05:30'
                }
                
                result = test_collection.insert_one(test_doc)
                print(f"SUCCESS: Test document inserted with ID: {result.inserted_id}")
                
                # Retrieve the document
                found = test_collection.find_one({'_id': result.inserted_id})
                print(f"SUCCESS: Retrieved document: {found}")
                
                # Clean up
                test_collection.delete_one({'_id': result.inserted_id})
                print(f"SUCCESS: Test document cleaned up")
                
            else:
                print("INFO: 'it' database not found, creating it...")
                db = client['it']
                test_collection = db['test_collection']
                test_doc = {'created': 'first document', 'database': 'it'}
                result = test_collection.insert_one(test_doc)
                print(f"SUCCESS: Created 'it' database with test document: {result.inserted_id}")
            
            client.close()
            print(f"SUCCESS: Connection test completed successfully!")
            return True
            
        except Exception as e:
            print(f"FAILED: {str(e)}")
            print()
            continue
    
    print("[FAILED] All connection attempts failed!")
    print()
    print("[HELP] Please check:")
    print("1. MongoDB Atlas cluster is running")
    print("2. Username '2024081204' exists in the database")
    print("3. Password 'anushka' is correct")
    print("4. IP address is whitelisted (try 0.0.0.0/0 for testing)")
    print("5. User has proper database permissions")
    
    return False

if __name__ == "__main__":
    main()
