from app import db

class Rule(db.Model):
    __tablename__ = 'rules'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    rule = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "rule": self.rule}
