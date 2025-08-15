# Real-Time Fraud Detection System

A sophisticated real-time fraud detection system built with Apache Kafka, Flask, and WebSocket technology for instant transaction monitoring and alert generation.

## 🚀 Overview

This system provides real-time fraud detection capabilities by monitoring transaction streams and applying customizable rule-based detection algorithms. The system uses Apache Kafka for high-throughput message processing and provides a web-based dashboard for real-time monitoring and control.

## ✨ Features

- **Real-Time Processing**: Instant transaction analysis using Apache Kafka streams
- **Customizable Rules**: User-defined fraud detection parameters and rules
- **Location-Based Detection**: Geographic anomaly detection (e.g., transactions from unusual locations)
- **Live Dashboard**: Web-based interface with real-time transaction monitoring
- **WebSocket Integration**: Instant alerts and updates without page refresh
- **Rule Management**: REST API for creating and managing fraud detection rules
- **Alert System**: Immediate notifications for suspicious activities
- **Data Simulation**: Built-in transaction generator for testing and demonstration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Transaction   │ -> │   Kafka Topic    │ -> │  Rule Engine    │
│   Producer      │    │  (transactions)  │    │  (Fraud Check)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        v
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Dashboard │ <- │   WebSocket      │ <- │   Alert System  │
│   (Flask App)   │    │   (Socket.IO)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │
        v
┌─────────────────┐
│   SQLite DB     │
│   (Rules)       │
└─────────────────┘
```

### Core Components

- **Flask Web Application**: Web interface and API endpoints
- **Kafka Producer**: Simulates real-time transaction data
- **Kafka Consumer**: Processes transactions in real-time
- **Rule Engine**: Applies fraud detection algorithms
- **WebSocket Server**: Provides real-time updates to the dashboard
- **SQLite Database**: Stores user-defined fraud detection rules

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Apache Kafka 2.8+
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/ARMSTRONGOPONDO/fraud-detection.git
cd fraud-detection
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
cd fraud_detection_system_v1/venv/bin/fraud_detection_system
pip install -r app/requirements.txt
```

### 4. Set Up Kafka

**Download and Start Kafka:**

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/2.13-3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Server (in a new terminal)
bin/kafka-server-start.sh config/server.properties
```

**Create Kafka Topics:**

```bash
# Create transactions topic
bin/kafka-topics.sh --create --topic transactions --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Create alerts topic
bin/kafka-topics.sh --create --topic alerts --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

## 🚀 Usage

### 1. Start the Flask Application

```bash
cd fraud_detection_system_v1/venv/bin/fraud_detection_system
python run.py
```

The web dashboard will be available at: `http://localhost:5000`

![Fraud Detection Dashboard](https://github.com/user-attachments/assets/4669d7fc-2094-421e-b929-3160ab99a341)

### 2. Start the Transaction Producer

In a new terminal:

```bash
cd fraud_detection_system_v1/venv/bin/fraud_detection_system
python kafka/producer.py
```

This will start generating simulated transactions every 2 seconds.

### 3. Access the Web Dashboard

1. Open your browser and navigate to `http://localhost:5000`
2. Click "Start Kafka Consumer" to begin processing transactions
3. Monitor real-time transaction feed and alerts

**Note**: If you encounter WebSocket connection issues, ensure that Socket.IO CDN is accessible, or consider hosting the library locally.

## 📝 API Documentation

### Add Fraud Detection Rule

```http
POST /rules
Content-Type: application/json

{
    "user_id": "12345",
    "rule": "location_anomaly"
}
```

### Get User Rules

```http
GET /rules/{user_id}
```

### Start Kafka Consumer

```http
POST /kafka/start_consumer
```

### Stop Kafka Consumer

```http
POST /kafka/stop_consumer
```

## ⚙️ Configuration

Edit `config.py` to customize system settings:

```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fraud.db'
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
    # Add your Twilio credentials for SMS alerts
    TWILIO_SID = 'your-twilio-sid'
    TWILIO_AUTH_TOKEN = 'your-twilio-token'
    TWILIO_PHONE_NUMBER = 'your-twilio-phone'
```

## 📊 Fraud Detection Rules

The system supports various types of fraud detection:

1. **Location Anomaly**: Flags transactions from unusual geographic locations
2. **Amount Threshold**: Alerts for transactions above specified amounts
3. **Frequency Detection**: Identifies unusual transaction patterns
4. **Time-based Rules**: Detects transactions outside normal hours
5. **Merchant Category**: Flags transactions from suspicious merchant types

## 🐛 Troubleshooting

### Common Issues

**Kafka Connection Issues:**
```bash
# Check if Kafka is running
netstat -an | grep 9092

# Verify topics exist
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Database Issues:**
```bash
# Initialize the database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

**Port Conflicts:**
- Ensure port 5000 (Flask) and 9092 (Kafka) are available
- Modify `run.py` to use a different port if needed

## 🔧 Development

### Project Structure

```
fraud_detection_system_v1/venv/bin/fraud_detection_system/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # API endpoints
│   ├── models.py            # Database models
│   ├── rule_engine.py       # Fraud detection logic
│   ├── templates/           # HTML templates
│   │   └── index.html       # Dashboard UI
│   └── static/              # CSS/JS assets
│       ├── css/style.css    # Styling
│       └── js/main.js       # Frontend logic
├── kafka/
│   ├── producer.py          # Transaction generator
│   └── consumer.py          # Transaction processor
├── config.py                # Configuration settings
└── run.py                   # Application entry point
```

### Adding New Rules

1. Define rule logic in `app/rule_engine.py`
2. Add rule to the `rule_applies()` function
3. Update the database model if needed
4. Test with simulated transactions

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the maintainer: ARMSTRONGOPONDO

---

**Note**: This system uses simulated transaction data for demonstration purposes. In a production environment, you would integrate with real transaction data sources and implement additional security measures.
