from extensions import db


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 购买时的价格

    # 关系
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.id}>'

    @property
    def subtotal(self):
        return float(self.price) * self.quantity