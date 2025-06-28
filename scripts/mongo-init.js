// MongoDB Initialization Script for Docker
// This script runs when the MongoDB container starts for the first time

// Switch to the bugtracker database
db = db.getSiblingDB('bugtracker');

// Create a user for the application
db.createUser({
  user: 'bugtracker',
  pwd: 'bugtracker123',
  roles: [
    {
      role: 'readWrite',
      db: 'bugtracker'
    }
  ]
});

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['username', 'email', 'password_hash'],
      properties: {
        username: {
          bsonType: 'string',
          maxLength: 50,
          description: 'Username must be a string and is required'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Email must be a valid email address'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Password hash is required'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        is_active: {
          bsonType: 'bool',
          description: 'User active status'
        }
      }
    }
  }
});

db.createCollection('bugs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['title', 'description', 'created_by_username'],
      properties: {
        title: {
          bsonType: 'string',
          maxLength: 200,
          description: 'Bug title is required'
        },
        description: {
          bsonType: 'string',
          description: 'Bug description is required'
        },
        status: {
          bsonType: 'string',
          enum: ['new', 'in_progress', 'resolved', 'closed'],
          description: 'Bug status must be one of the allowed values'
        },
        priority: {
          bsonType: 'string',
          enum: ['low', 'medium', 'high'],
          description: 'Bug priority must be one of the allowed values'
        },
        category: {
          bsonType: 'string',
          maxLength: 50,
          description: 'Bug category'
        },
        created_by_username: {
          bsonType: 'string',
          description: 'Creator username is required'
        },
        assigned_to_username: {
          bsonType: 'string',
          description: 'Assigned user username'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        },
        comments: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['author_username', 'comment'],
            properties: {
              author_username: {
                bsonType: 'string',
                description: 'Comment author username'
              },
              comment: {
                bsonType: 'string',
                description: 'Comment text'
              },
              created_at: {
                bsonType: 'date',
                description: 'Comment creation timestamp'
              }
            }
          }
        }
      }
    }
  }
});

// Create indexes for better performance
db.users.createIndex({ 'username': 1 }, { unique: true });
db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'created_at': -1 });

db.bugs.createIndex({ 'created_by_username': 1 });
db.bugs.createIndex({ 'assigned_to_username': 1 });
db.bugs.createIndex({ 'status': 1 });
db.bugs.createIndex({ 'priority': 1 });
db.bugs.createIndex({ 'category': 1 });
db.bugs.createIndex({ 'created_at': -1 });
db.bugs.createIndex({ 'updated_at': -1 });

print('MongoDB initialization completed successfully!');
print('Database: bugtracker');
print('Collections created: users, bugs');
print('Indexes created for optimal performance');
