import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS

# Initialize Flask extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

def create_app():
    """
    Application factory to create and configure the Flask app instance.
    This avoids circular imports by initializing the app dynamically.
    """
    app = Flask(__name__)
    app.config.from_object('config')  # Load configuration

    # Enable Cross-Origin Resource Sharing
    CORS(app)

    # Initialize extensions with the app
    db.init_app(app)
    socketio.init_app(app)

    # Import and register blueprints
    from app.routes import bp as main_bp  # Import blueprint
    app.register_blueprint(main_bp)

    return app
