from confluent_kafka import Producer
import json
import time
import random

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker
}

# Initialize the producer
producer = Producer(producer_config)

# Callback for delivery reports
def delivery_report(err, msg):
    """ Called once for each message to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Simulated transaction generator
def generate_transaction():
    """ Generate a random transaction for testing. """
    user_id = random.randint(1, 1000)
    amount = round(random.uniform(10.0, 5000.0), 2)
    txn_type = random.choice(["online", "pos", "atm", "transfer"])
    return {"user_id": str(user_id), "amount": amount, "type": txn_type}

# Produce messages infinitely
try:
    print("Starting Kafka producer. Press Ctrl+C to stop.")
    while True:
        transaction = generate_transaction()
        producer.produce(
            'transactions',  # Topic name
            key=str(transaction["user_id"]),  # Key (optional)
            value=json.dumps(transaction),  # Serialized message
            callback=delivery_report  # Callback function
        )
        print(f"Sent: {transaction}")
        producer.poll(0)  # Trigger any available delivery report callbacks
        time.sleep(2)  # Wait for 2 seconds between messages
except KeyboardInterrupt:
    print("\nStopping Kafka producer...")
finally:
    producer.flush()  # Ensure all messages are delivered before exiting
