from flask import current_app as app
from app import socketio
from flask_socketio import emit

# This function sends the update
def send_update(data):
    try:
        # Emit the message to the connected clients
        socketio.emit('transaction_update', {'message': data}, namespace='/')
        print(f"Emit successful: {data}")
    except Exception as e:
        print(f"Error in send_update: {e}")

# Use this function for background processing
def process_transaction(data):
    print(f"Processing transaction: {data}")
    socketio.start_background_task(send_update, data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
