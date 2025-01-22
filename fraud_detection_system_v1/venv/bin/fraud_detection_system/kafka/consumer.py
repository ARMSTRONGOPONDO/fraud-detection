import sys
import os
# Append the parent directory for imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import json
from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
from producer import producer
from app.rule_engine import process_transaction  # Ensure this import is correct
from app.sockets import send_update  # Assuming send_update is in socket.py

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TRANSACTIONS_TOPIC = 'transactions'
KAFKA_ALERTS_TOPIC = 'alerts'
GROUP_ID = 'fraud_detection_group'

# Initialize Kafka Consumer
consumer_config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest',  # Start consuming from the earliest message
}
consumer = Consumer(consumer_config)

# Subscribe to the transactions topic
consumer.subscribe([KAFKA_TRANSACTIONS_TOPIC])

# Initialize Kafka Producer
producer_config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
}
producer = Producer(producer_config)

# Callback for producer delivery reports
def delivery_report(err, msg):
    if err:
        print(f"Error delivering message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

print("Consumer is listening for transactions...")

# Consume messages from Kafka
try:
    while True:
        msg = consumer.poll(1.0)  # Poll with a timeout of 1 second

        if msg is None:
            continue  # No new message, continue listening

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print("End of partition reached")
            elif msg.error():
                raise KafkaException(msg.error())
            continue

        # Deserialize the incoming message
        transaction = json.loads(msg.value().decode('utf-8'))
        print(f"Received transaction: {transaction}")  # Debug log for received transactions

        # Process the transaction using the rule engine
        try:
            flagged = process_transaction(transaction, producer)  # Assuming process_transaction requires producer
        except Exception as e:
            print(f"Error processing transaction: {e}")
            continue

        # If flagged, send the transaction to the alerts topic
        if flagged:
            producer.produce(
                KAFKA_ALERTS_TOPIC,
                value=json.dumps(transaction).encode('utf-8'),
                callback=delivery_report
            )
            print(f"Flagged transaction sent to alerts: {transaction}")

        # Emit the transaction to WebSocket clients
        try:
            if send_update is not None:
                send_update(transaction)  # Send updates to the frontend via WebSocket
            else:
                print("WebSocket client is not initialized.")
        except Exception as e:
            print(f"Error emitting transaction update: {e}")

        # Trigger delivery reports
        producer.flush()

except KeyboardInterrupt:
    print("Consumer interrupted by user")

finally:
    consumer.close()
    print("Consumer closed")
