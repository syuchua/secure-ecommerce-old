from extensions import db
from datetime import datetime


class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    postal_code = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)