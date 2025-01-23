from flask import current_app as app
from app import socketio
from flask_socketio import emit
from flask import request, jsonify
from app import app, db
from models import Rule
from flask_socketio import emit, start_background_task
import logging
import traceback

logger = logging.getLogger(__name__)

def send_update(data):
    try:
        # Emit the message to the connected clients
        socketio.emit('transaction_update', {'message': data}, namespace='/')
        logger.info(f"Emit successful: {data}")
    except Exception as e:
        logger.error(f"Error in send_update: {e}\n{traceback.format_exc()}")

def process_transaction(data):
    logger.info(f"Processing transaction: {data}")
    start_background_task(send_update, data)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')



