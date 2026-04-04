import datetime
import random
import string

from sqlalchemy import text

from models import Product, ProductImage, Cart
from extensions import db

# for the login required decoration
from functools import wraps
from flask import g, request, redirect, url_for, session, flash
from datetime import datetime


def product_variant_images(product_id, variant_id):
    statement = text('SELECT * FROM product_image WHERE product_id = :product_id AND variant_id = :variant_id')
    query = db.session.execute(statement, {'product_id': product_id, 'variant_id': variant_id}).fetchall()

    product_images = []
    for item in query:
        product_images.append(
            ProductImage(
                id=item.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                image=item.image,
                is_primary=item.is_primary,
            )
        )

    return product_images


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        customer_id = session.get('customer_id')

        if not customer_id or not isinstance(customer_id, int):
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('home.customer_login', next=request.url))

        return f(*args, **kwargs)

    return decorated_function

def _customer_id():
    return session.get('customer_id')

def _cart_payload(customer_id):
    items = Cart.query.filter_by(customer_id=customer_id,status = 1).all()
    cart_items = [
        {
            'id':           i.id,
            'product_id':   i.product_id,
            'variant_id':   i.variant_id,
            'product_name': i.product_name,
            'color':        i.color,
            'variant_type': i.variant_type,
            'price':        float(i.price),
            'image':        i.image,
            'quantity':     i.quantity,
            'added_at':     i.added_at.isoformat() if i.added_at else None,
        }
        for i in items
    ]
    return {
        'items': cart_items,
        'summary': {
            'total':          round(sum(i.price * i.quantity for i in items), 2),
            'total_quantity': sum(i.quantity for i in items),
        },
    }

def generate_secure_invoice(order_id, prefix="AK"):
    date_part = datetime.now().strftime('%y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{prefix}-{date_part}-{order_id}{random_part}"


