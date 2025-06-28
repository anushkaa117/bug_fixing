from app import create_app
import os

# Create application instance
application = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == "__main__":
    application.run()
