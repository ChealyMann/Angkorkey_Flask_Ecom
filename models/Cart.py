from extensions import db
from sqlalchemy.orm import validates


class Cart(db.Model):
    __tablename__ = 'cart'

    id           = db.Column(db.Integer, primary_key=True)
    customer_id  = db.Column(
        db.Integer,
        db.ForeignKey('customer.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    product_id   = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'),
                             nullable=False)
    variant_id   = db.Column(db.Integer, db.ForeignKey('product_variants.id', ondelete='SET NULL'),
                             nullable=True)

    variant = db.relationship('ProductVariant', foreign_keys=[variant_id])

    # Snapshots — captured once at add-time, never updated
    product_name = db.Column(db.String(100), nullable=False)
    color        = db.Column(db.String(50),  nullable=True)
    variant_type = db.Column(db.String(50),  nullable=True)
    price        = db.Column(db.Float,       nullable=False)
    image        = db.Column(db.String(120), nullable=True)

    quantity     = db.Column(db.Integer, default=1, nullable=False)
    added_at     = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.Integer, default=1)  # 1: Pending, 2: Checkout

    @validates('quantity')
    def validate_quantity(self, key, value):
        if value <= 0:
            raise ValueError('Quantity must be greater than zero.')
        return value

    @property
    def line_total(self):
        return round(self.price * self.quantity, 2)

    def __repr__(self):
        return f'<Cart customer={self.customer_id} product={self.product_id}>'