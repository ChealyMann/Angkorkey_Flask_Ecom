from extensions import db
from datetime import datetime
from functions.functions import generate_secure_invoice
from models import OrderItem


class Order(db.Model):
    __tablename__ = 'orders'
    id          = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)

    # Delivery
    phone        = db.Column(db.String(20),  nullable=False)
    address      = db.Column(db.String(255), nullable=False)   # street from geopy
    city         = db.Column(db.String(100), nullable=False)   # city from geopy
    full_address = db.Column(db.Text,        nullable=True)    # full display string from geopy
    latitude     = db.Column(db.Float,       nullable=True)    # pin lat
    longitude    = db.Column(db.Float,       nullable=True)    # pin lng

    # Invoice
    invoice_no   = db.Column(db.String(50),  unique=True)
    sub_total    = db.Column(db.Float,       nullable=False)
    discount     = db.Column(db.Float,       default=0.0)
    shipping_fee = db.Column(db.Float,       default=0.0)
    grand_total  = db.Column(db.Float,       nullable=False)

    # Payment & status
    payment_method  = db.Column(db.String(50), nullable=False)
    payment_status  = db.Column(db.String(50), default='pending')
    status          = db.Column(db.Integer,    default=1)
    # 1 Pending · 2 Confirmed · 3 Shipped · 4 Delivered · 5 Canceled · 6 Returned

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items    = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    customer = db.relationship('Customer',  backref='orders', lazy=True)

    def __init__(self, phone, address, city, sub_total, grand_total, payment_method,
                 customer_id=None, full_address=None, latitude=None, longitude=None,
                 discount=0.0, shipping_fee=0.0, payment_status='pending', status=1):
        self.customer_id    = customer_id
        self.phone          = phone
        self.address        = address
        self.city           = city
        self.full_address   = full_address
        self.latitude       = latitude
        self.longitude      = longitude
        self.sub_total      = sub_total
        self.discount       = discount
        self.shipping_fee   = shipping_fee
        self.grand_total    = grand_total
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.status         = status