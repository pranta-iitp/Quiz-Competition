from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import os
import logging
import sys

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    """
    # === Log setup ===
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'app.log')

    # Clear previous log file
    with open(log_file_path, 'w'):
        pass

    # Set up file logging
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Use Python's root logger instead of app.logger to avoid circular logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    # Redirect stdout and stderr safely
    class StreamToFile:
        def __init__(self, stream_name, file_path):
            self.stream_name = stream_name
            self.file = open(file_path, 'a', buffering=1)

        def write(self, message):
            if message.strip():
                self.file.write(message + '\n')

        def flush(self):
            self.file.flush()

    sys.stdout = StreamToFile('stdout', log_file_path)
    sys.stderr = StreamToFile('stderr', log_file_path)
    """

    # PostgreSQL configuration
    app.secret_key = 'supersecret123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/QuizCompete'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Encryption key setup
    encryption_key = os.environ.get('ENCRYPTION_KEY')
    
    # Generate key if not provided (for development only)
    if not encryption_key:
        encryption_key = Fernet.generate_key()
        print("=" * 50)
        print("IMPORTANT: Generated new encryption key for development")
        print(f"Key: {encryption_key}")
        print("For production, set this as ENCRYPTION_KEY environment variable")
        print("=" * 50)
    
    app.config['ENCRYPTION_KEY'] = encryption_key
    
    # Note: You have app.secret_key above, so you might want to use that instead
    # Remove one of these to avoid confusion:
    # Option 1: Use the existing secret_key
    # app.config['SECRET_KEY'] = app.secret_key
    
    # Option 2: Use environment variable (recommended)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'supersecret123'
    
    # Initialize database
    db.init_app(app)
    
     # Register the custom Jinja2 filter for time format purpose
    @app.template_filter('format_duration')
    def format_duration(seconds):
        if seconds is None:
            return "N/A"
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # Import and register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.author import author_bp
    from app.routes.participant import participant_bp
    from app.routes.quiz import quiz_bp
    #from app.routes.superuser import superuser_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(author_bp, url_prefix='/author')
    app.register_blueprint(participant_bp, url_prefix='/participant')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    #app.register_blueprint(superuser_bp, url_prefix='/superuser')
    
    return app

# Optional: Helper function to generate encryption key
def generate_encryption_key():
    """Run this function to generate a new encryption key for production"""
    key = Fernet.generate_key()
    print(f"Generated encryption key: {key}")
    print("Set this as ENCRYPTION_KEY environment variable")
    return key

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)