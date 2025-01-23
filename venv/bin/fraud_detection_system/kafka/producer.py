from collections import defaultdict
from confluent_kafka import Producer
import json
import time
import random
from datetime import datetime, timedelta

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker
}

# Initialize the producer
producer = Producer(producer_config)

# Callback for delivery reports
def delivery_report(err, msg):
    """Called once for each message to indicate delivery result."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Transaction count tracker
user_transaction_counts = defaultdict(list)  # Stores timestamps of transactions for each user

def get_number_of_transactions(user_id):
    """
    Counts the number of transactions for a specific user within the current day.
    :param user_id: User ID for which transactions are being counted.
    :return: Number of transactions for the user today.
    """
    try:
        # Get the current day
        now = datetime.now()
        today = now.date()

        # Filter transactions within today for the user
        transactions_today = [
            txn_time for txn_time in user_transaction_counts[user_id] if txn_time.date() == today
        ]

        # Update the transaction list for the user to only keep today's transactions
        user_transaction_counts[user_id] = transactions_today

        # Return the count of today's transactions
        return len(transactions_today)
    except Exception as e:
        print(f"Error in get_number_of_transactions: {e}")
        return 0

# Simulated transaction generator
def generate_transaction(user_id, location, time_start, time_end, max_amount):
    """
    Generate a random transaction for a given user with configurable rules.
    :param user_id: User ID associated with the transaction.
    :param location: User's location.
    :param time_start: Custom start time (e.g., '10:00').
    :param time_end: Custom end time (e.g., '18:00').
    :param max_amount: Maximum allowed transaction amount.
    :return: Generated transaction dictionary or None if outside the allowed time.
    """
    # Validate the time range
    now = datetime.now()
    start_time = datetime.strptime(time_start, "%H:%M").time()
    end_time = datetime.strptime(time_end, "%H:%M").time()
    current_time = now.time()

    if not (start_time <= current_time <= end_time):
        print(f"Skipping transaction: Outside of custom time range {time_start}-{time_end}")
        return None

    # Random transaction details
    amount = round(random.uniform(10.0, max_amount), 2)
    txn_type = random.choice(["online", "pos", "atm", "transfer"])
    distance_from_user = random.randint(1, 10000)  # Simulated distance from user location
    transaction_count = get_number_of_transactions(user_id) + 1  # Count transactions today

    transaction = {
        "user_id": str(user_id),
        "amount": amount,
        "type": txn_type,
        "timestamp": now.isoformat(),
        "location": location,
        "distance_from_user": distance_from_user,
        "transaction_count_today": transaction_count
    }

    # Track the transaction timestamp
    user_transaction_counts[user_id].append(now)
    return transaction

# Produce messages indefinitely
try:
    print("Starting Kafka producer. Press Ctrl+C to stop.")
    while True:
        # Example parameters (can be replaced with real-time input)
        user_id = random.randint(799, 800)
        location = random.choice(["Nairobi", "Nakuru", "Eldoret", "Kisumu"])
        time_start = "00:00"
        time_end = "23:59"  # Allowed transaction end time
        max_amount = 50000  # Maximum transaction amount

        # Generate a transaction
        transaction = generate_transaction(user_id, location, time_start, time_end, max_amount)

        if transaction:
            producer.produce(
                'transactions',  # Kafka topic
                key=str(transaction["user_id"]),  # Key (optional)
                value=json.dumps(transaction),  # Serialized transaction
                callback=delivery_report  # Callback for delivery report
            )
            print(f"Sent: {transaction}")
            producer.poll(0)  # Trigger any available delivery report callbacks
        time.sleep(10)  # Wait for 10 seconds between transactions
except KeyboardInterrupt:
    print("\nStopping Kafka producer...")
finally:
    producer.flush()  # Ensure all messages are delivered before exiting
