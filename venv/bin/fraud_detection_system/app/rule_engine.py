import sys
import os


# Append the parent directory for imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
from dateutil.parser import parse
from datetime import datetime
from collections import defaultdict
import json
from confluent_kafka import Consumer, Producer
from flask import current_app
from models import Rule
from app import db
from app import create_app
from app.models import FlaggedTransaction

from twilio.rest import Client
from config import Config  # Import your configuration
# Create the Flask app and push the app context
app = create_app()

# In-memory store to track daily totals (consider a database or Redis for production)
daily_transaction_totals = defaultdict(lambda: defaultdict(float))

def start_kafka_consumer():
    """Starts the Kafka consumer to listen for transactions."""
    try:
        with app.app_context():
            # Kafka setup
            consumer_config = {
                'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
                'group.id': 'fraud_detection_group',
                'auto.offset.reset': 'earliest',
            }
            consumer = Consumer(consumer_config)

            producer_config = {
                'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            }
            producer = Producer(producer_config)

            print("Kafka Consumer started. Listening for transactions...")
            consumer.subscribe(['transactions'])

            try:
                while True:
                    message = consumer.poll(5.0)
                    if message is None:
                        continue
                    if message.error():
                        print(f"Error: {message.error()}")
                        continue

                    transaction = json.loads(message.value().decode('utf-8'))
                    print(f"Received transaction: {transaction}")
                    process_transaction(transaction, producer)
            except KeyboardInterrupt:
                print("Consumer stopped by user.")
            finally:
                print("Closing Kafka consumer...")
                consumer.close()

    except Exception as e:
        print(f"Error starting Kafka consumer: {e}")

def get_rules_for_user(user_id):
    """Fetches fraud detection rules for a specific user."""
    try:
        with app.app_context():
            rules = Rule.query.filter_by(user_id=user_id).all()
            return [rule.to_dict() for rule in rules]
    except Exception as e:
        print(f"Error fetching rules for user {user_id}: {e}")
        return []

def rule_applies(rule, transaction):
    """Checks if a specific rule applies to a transaction."""
    try:
        if rule["type"] == "amount":
            return transaction["amount"] > rule["max_transactions"]
        elif rule["type"] == "frequency":
            return transaction.get("transaction_count_today", 0) > rule["threshold"]
        elif rule["type"] == "time_range":
            txn_time = parse(transaction["timestamp"])
            txn_hour = txn_time.hour
            start_hour = int(rule["start"].split(":")[0])
            end_hour = int(rule["end"].split(":")[0])
            return not (start_hour <= txn_hour <= end_hour)
        elif rule["type"] == "location":
            return transaction["location"] not in rule["allowed_locations"]
        elif rule["type"] == "custom_rule":
            # Daily transaction threshold logic
            txn_date = parse(transaction["timestamp"]).date()
            user_id = transaction["user_id"]

            # Update daily total for the user
            daily_total = daily_transaction_totals[user_id][txn_date]
            new_total = daily_total + transaction["amount"]

            if new_total > rule["threshold"]:
                print(f"Daily threshold exceeded: {new_total} > {rule['threshold']}")
                return True

            # Update the in-memory tracker
            daily_transaction_totals[user_id][txn_date] = new_total
        return False
    except Exception as e:
        print(f"Error evaluating rule {rule} for transaction {transaction}: {e}")
        return False


def process_transaction(transaction, producer):
    """Processes the transaction and checks for fraud based on user rules."""
    try:
        print(f"Processing transaction: {transaction}")

        user_rules = get_rules_for_user(transaction['user_id'])
        if not user_rules:
            print(f"No rules found for user {transaction['user_id']}. Skipping fraud check.")
            return False

        print(f"Rules for user {transaction['user_id']}: {user_rules}")

        for rule in user_rules:
            if rule_applies(rule, transaction):
                flagged_transaction = {
                    "transaction": transaction,
                    "rule_triggered": rule
                }
                save_flagged_transaction_to_db(flagged_transaction)  # Save to DB

                producer.produce(
                    'alerts',
                    value=json.dumps(flagged_transaction).encode('utf-8')
                )
                producer.flush()
                print(f"Transaction flagged: {flagged_transaction}")
                send_notification(flagged_transaction)
                return True

    except Exception as e:
        print(f"Error processing transaction: {e}")
    return False

def save_flagged_transaction_to_db(flagged_transaction):
    """Saves flagged transactions to the database."""
    try:
        print("Saving flagged transaction to DB:", flagged_transaction)  # Debug

        with app.app_context():
            new_flag = FlaggedTransaction(
                user_id=flagged_transaction['transaction']['user_id'],
                transaction=json.dumps(flagged_transaction['transaction']),
                rule_triggered=json.dumps(flagged_transaction['rule_triggered']),
                flagged_at=datetime.now(datetime.timezone.utc)
            )
            db.session.add(new_flag)
            db.session.commit()
            print("Flagged transaction saved successfully.")  # Success log
    except Exception as e:
        print(f"Error saving flagged transaction: {e}")  # Error log

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_notification(flagged_transaction):
    """Sends an email notification using Brevo SMTP."""
    try:
        # Extract transaction details
        recipient_email = "opondoarmstrong1@gmail.com"  # Replace with your recipient email for testing
        amount = flagged_transaction["transaction"]["amount"]
        location = flagged_transaction["transaction"]["location"]
        timestamp = flagged_transaction["transaction"]["timestamp"]
        rule_type = flagged_transaction["rule_triggered"]["type"]
        threshold = flagged_transaction["rule_triggered"]["threshold"]

        # Email configuration
        sender_email = "839fe6002@smtp-brevo.com"  # Brevo email login
        smtp_password = "8DjBrFHad5mREZGV"  # Updated Brevo SMTP key
        smtp_server = "smtp-relay.brevo.com"
        smtp_port = 587
        subject = "Flagged Transaction Alert"

        # Email content
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        body = f"""
        Dear User,

        A transaction has been flagged:
        - Amount: ${amount}
        - Location: {location}
        - Timestamp: {timestamp}
        - Rule Triggered: {rule_type} (Threshold: ${threshold})

        Please review this transaction in your account.

        Regards,
        Fraud Detection Team
        """
        message.attach(MIMEText(body, "plain"))

        # Send email via Brevo SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        print(f"Email notification sent to {recipient_email}.")

    except Exception as e:
        print(f"Error sending email notification: {e}")






if __name__ == "__main__":
    try:
        with app.app_context():
            start_kafka_consumer()
    except Exception as e:
        print(f"Critical error: {e}")
