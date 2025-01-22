import json
from confluent_kafka import Consumer, Producer

def start_kafka_consumer():
    """Starts the Kafka consumer to listen for transactions."""
    try:
        # Initialize Kafka Consumer with configuration dictionary
        consumer_config = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'fraud_detection_group',
            'auto.offset.reset': 'earliest',  # Start from the earliest message
        }
        
        consumer = Consumer(consumer_config)
        
        # Initialize Kafka Producer with configuration dictionary
        producer_config = {
            'bootstrap.servers': 'localhost:9092',
        }
        
        producer = Producer(producer_config)
        
        print("Kafka Consumer started. Listening for transactions...")
        
        # Subscribe to the transactions topic
        consumer.subscribe(['transactions'])
        
        # Process each transaction
        while True:
            message = consumer.poll(1.0)  # Poll with a timeout of 1 second
            
            if message is None:
                continue  # No new message, continue listening
            
            if message.error():
                print(f"Error: {message.error()}")
                continue
            
            # Deserialize the incoming message
            transaction = json.loads(message.value().decode('utf-8'))
            print(f"Received transaction: {transaction}")
            
            # Process the transaction
            process_transaction(transaction, producer)
    
    except Exception as e:
        print(f"Error starting Kafka consumer: {e}")

# Inside rule_engine.py
def process_transaction(transaction, producer):
    try:
        # Process the transaction (example logic)
        print(f"Processing transaction: {transaction}")
        
        # Get user rules (example logic, replace with your actual rules)
        user_rules = get_rules_for_user(transaction['user_id'])
        
        # Iterate over rules and check if any apply to the transaction
        for rule in user_rules:
            if rule_applies(rule, transaction):
                # If a rule applies, flag the transaction
                producer.produce('alerts', value=json.dumps(transaction).encode('utf-8'))
                print(f"Transaction flagged: {transaction}")
                
        # Optionally send a notification
        send_notification(transaction)
        return True  # Indicate that the transaction was flagged
        
    except Exception as e:
        print(f"Error processing transaction: {e}")
        return False  # Indicate that there was an error


def get_rules_for_user(user_id):
    """Fetches fraud detection rules for a specific user."""
    # TODO: Replace with real database query or external service call
    return [{"type": "online", "action": "block"}]  # Example rule

def rule_applies(rule, transaction):
    """Checks if a rule applies to a transaction."""
    try:
        return "type" in rule and rule["type"] == transaction["type"]
    except Exception as e:
        print(f"Error evaluating rule {rule}: {e}")
        return False

def send_notification(transaction):
    """Sends a notification for a flagged transaction."""
    try:
        print(f"Sending notification for flagged transaction: {transaction}")
        # TODO: Implement Twilio or email API integration here
    except Exception as e:
        print(f"Error sending notification for {transaction}: {e}")

# Entry point of the script
if __name__ == "__main__":
    try:
        start_kafka_consumer()
    except KeyboardInterrupt:
        print("Consumer stopped by user. Exiting...")
    except Exception as e:
        print(f"Critical error: {e}")
