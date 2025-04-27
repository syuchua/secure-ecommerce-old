from extensions import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # recipient_name = db.Column(db.String(100))
    # phone = db.Column(db.String(20))

    # 订单地址信息
    shipping_address = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_zip = db.Column(db.String(20))
    shipping_country = db.Column(db.String(100))

    # 付款信息
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')

    # 订单金额
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_fee = db.Column(db.Numeric(10, 2), default=0)
    tax = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # 关系
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.id}>'