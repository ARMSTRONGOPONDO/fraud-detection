import os
import sys
import json
import threading
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_socketio import emit
from confluent_kafka import Consumer
from app.models import Rule
from app import db, socketio  # Import only what is required

bp = Blueprint('main', __name__, template_folder='templates')

kafka_consumer_thread = None
kafka_consumer_running = False

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/rules', methods=['POST'])
def add_rule():
    data = request.json
    rule = Rule(user_id=data['user_id'], rule=data['rule'])
    db.session.add(rule)
    db.session.commit()
    return jsonify({"message": "Rule added successfully"}), 201

@bp.route('/rules/<user_id>', methods=['GET'])
def get_rules(user_id):
    rules = Rule.query.filter_by(user_id=user_id).all()
    return jsonify([rule.to_dict() for rule in rules])

@bp.route('/kafka/start_consumer', methods=['POST'])
def start_consumer():
    global kafka_consumer_thread, kafka_consumer_running
    if kafka_consumer_running:
        return jsonify({"message": "Kafka Consumer is already running"}), 200

    kafka_consumer_running = True
    kafka_consumer_thread = threading.Thread(target=consume_kafka_messages)
    kafka_consumer_thread.start()
    return jsonify({"message": "Kafka Consumer started"}), 200

@bp.route('/kafka/stop_consumer', methods=['POST'])
def stop_consumer():
    global kafka_consumer_running
    if not kafka_consumer_running:
        return jsonify({"message": "Kafka Consumer is not running"}), 200

    kafka_consumer_running = False
    return jsonify({"message": "Kafka Consumer stopped"}), 200

def consume_kafka_messages():
    global kafka_consumer_running
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'fraud_detection_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(['transactions'])

    try:
        while kafka_consumer_running:
            message = consumer.poll(1.0)
            if message is None or message.error():
                continue

            data = json.loads(message.value().decode('utf-8'))
            print(f"Kafka message received: {data}")
            socketio.emit('transaction_update', data)  # Emit data
    except Exception as e:
        print(f"Error consuming Kafka messages: {e}")
    finally:
        consumer.close()
