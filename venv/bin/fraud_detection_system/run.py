import eventlet
eventlet.monkey_patch()  # Apply monkey patching for Eventlet

from app import create_app, socketio  # Import only after monkey patching

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = '769444'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

if __name__ == "__main__":
    app = create_app()  # Use the factory function to create the app
    socketio.run(app, host="127.0.0.1", port=5000, debug=True, allow_unsafe_werkzeug=True, log_output=True)

