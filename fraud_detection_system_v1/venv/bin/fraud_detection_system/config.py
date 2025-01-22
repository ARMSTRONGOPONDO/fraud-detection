import os

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:w!334rd.@localhost/fraud_detection'
SQLALCHEMY_TRACK_MODIFICATIONS = False


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fraud.db'  # Use SQLite for simplicity
    SECRET_KEY = os.getenv('SECRET_KEY', '12345678')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
    TWILIO_SID = 'AC5da8b60b33c771f243da45882fb2f056'
    TWILIO_AUTH_TOKEN = '0c8169f3adc1e53a8c27aee131b56508'
    TWILIO_PHONE_NUMBER = '+12312998918'