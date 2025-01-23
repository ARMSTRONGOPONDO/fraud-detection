import sys
import os


# Append the parent directory for imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import threading
import time
import logging
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_socketio import emit
from confluent_kafka import Consumer
from app.models import Rule
from app import db, socketio

from flask import request, jsonify
from app import db
from app.models import FlaggedTransaction


# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Blueprint and thread variables
bp = Blueprint('main', __name__, template_folder='templates')
kafka_consumer_thread = None
kafka_consumer_running = False
kafka_lock = threading.Lock()  # Thread safety for Kafka consumer state

@bp.route('/')
def home():
    return render_template('test.html')

### User Rule API ###
@bp.route('/rules', methods=['POST'])
def add_rule():
    data = request.json
    try:
        rule = Rule(user_id=data['user_id'], rule=data['rule'])
        db.session.add(rule)
        db.session.commit()
        return jsonify({"message": "Rule added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding rule: {e}")
        return jsonify({"message": "Failed to add rule", "error": str(e)}), 500

@bp.route('/rules/<user_id>', methods=['GET'])
def get_rules(user_id):
    try:
        rules = Rule.query.filter_by(user_id=user_id).all()
        return jsonify([rule.to_dict() for rule in rules]), 200
    except Exception as e:
        logger.error(f"Error fetching rules for user {user_id}: {e}")
        return jsonify({"message": "Failed to fetch rules", "error": str(e)}), 500



@bp.route('/api/set_user_rules', methods=['POST'])
def set_user_rules():
    try:
        data = request.json

        # Validate required fields
        required_fields = ["userId", "customTimeStart", "customTimeEnd", "dailyTransactionLimit", "largeTransactionAmount"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing or invalid field: {field}'}), 400

        if not isinstance(data['userId'], int):
            return jsonify({'success': False, 'message': 'Invalid userId (must be an integer)'}), 400

        if data['customTimeStart'] >= data['customTimeEnd']:
            return jsonify({'success': False, 'message': 'Invalid time range (start must be before end)'}), 400

        # Create a new rule
        rule = Rule(
            user_id=data['userId'],
            type="custom_rule",
            start=data['customTimeStart'],
            end=data['customTimeEnd'],
            threshold=data['largeTransactionAmount'],
            max_transactions=data['dailyTransactionLimit'],
            user_location=data.get('userLocation'),  # Optional
        )

        # Save to database
        db.session.add(rule)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Rules saved successfully!'}), 200

    except Exception as e:
        logger.error(f"Error saving rules: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    """Fetches transactions and flagged transactions for a user."""
    try:
        user_id = request.args.get('user_id')
        transaction = request.args.get('transaction')
        rule_triggered = request.args.get('rule_triggered')

        # Ensure user_id is provided
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Build the query with filters
        query = FlaggedTransaction.query.filter_by(user_id=user_id)

        if transaction:
            query = query.filter_by(transaction=transaction)
        if rule_triggered:
            query = query.filter_by(rule_triggered=rule_triggered)

        flagged = query.all()

        # Convert flagged transactions to dictionaries for JSON response
        return jsonify({
            "flagged_transactions": [flag.to_dict() for flag in flagged]
        })
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return jsonify({"error": "An error occurred while fetching transactions"}), 500


### Kafka Consumer API ###
@bp.route('/kafka/start_consumer', methods=['POST'])
def start_consumer():
    global kafka_consumer_thread, kafka_consumer_running
    with kafka_lock:
        if kafka_consumer_running:
            return jsonify({"message": "Kafka Consumer is already running"}), 200

        kafka_consumer_running = True
        kafka_consumer_thread = threading.Thread(target=consume_kafka_messages, daemon=True)
        kafka_consumer_thread.start()
    return jsonify({"message": "Kafka Consumer started"}), 200

@bp.route('/kafka/stop_consumer', methods=['POST'])
def stop_consumer():
    global kafka_consumer_running
    with kafka_lock:
        if not kafka_consumer_running:
            return jsonify({"message": "Kafka Consumer is not running"}), 200

        kafka_consumer_running = False
    return jsonify({"message": "Kafka Consumer stopped"}), 200

### Kafka Consumer Logic ###
def consume_kafka_messages():
    global kafka_consumer_running
    consumer_config = {
        'bootstrap.servers': os.getenv('KAFKA_BROKER', 'localhost:9092'),
        'group.id': 'fraud_detection_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(['transactions'])

    try:
        while kafka_consumer_running:
            message = consumer.poll(1.0)
            if message is None:
                time.sleep(0.1)
                continue
            if message.error():
                logger.warning(f"Kafka error: {message.error()}")
                continue

            try:
                data = json.loads(message.value().decode('utf-8'))
                logger.info(f"Kafka message received: {data}")
                socketio.emit('transaction_update', data)
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"Error decoding Kafka message: {e}")
    except Exception as e:
        logger.error(f"Error consuming Kafka messages: {e}")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed")
