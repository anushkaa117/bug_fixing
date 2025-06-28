-- Initialize PostgreSQL database for Bug Tracker
-- This file is used by Docker Compose to set up the initial database

-- Create database if it doesn't exist (handled by Docker environment variables)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create initial admin user (will be handled by Flask app initialization)
-- This file serves as a placeholder for any future database initialization scripts
