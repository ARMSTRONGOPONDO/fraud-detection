import sys
import os


# Append the parent directory for imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask_sqlalchemy import SQLAlchemy
import json
from app import db

class Rule(db.Model):
    __tablename__ = 'rule'
    __table_args__ = {'extend_existing': True}  # Allow redefinition of table

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    start = db.Column(db.String(10), nullable=False)
    end = db.Column(db.String(10), nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    max_transactions = db.Column(db.Integer, nullable=True)
    user_location = db.Column(db.String(255), nullable=True)  # Optional field

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "start": self.start,
            "end": self.end,
            "threshold": self.threshold,
            "max_transactions": self.max_transactions,
            "user_location": self.user_location,
        }
    
class FlaggedTransaction(db.Model):
    __tablename__ = 'flagged_transactions'
    __table_args__ = {'extend_existing': True}  # Allow redefinition of table

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    transaction = db.Column(db.Text, nullable=False)  # JSON as string
    rule_triggered = db.Column(db.Text, nullable=False)  # JSON as string
    flagged_at  = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "transaction": json.loads(self.transaction),
            "rule_triggered": json.loads(self.rule_triggered),
            "flagged_at": self.flagged_at,
        }

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # Allow redefinition of table
    id = db.Column(db.Integer, primary_key=True)  # Unique User ID
    user_id = db.Column(db.String(100), unique=True, nullable=False)  # User ID for login
    password = db.Column(db.String(255), nullable=False)  # Hashed password

    def to_dict(self):
        return{
            "id":self.id,
            "user_id":self.user_id,
            "password":self.password
        }
