from sqlalchemy import text

from models import Product, ProductImage
from extensions import db

# for the login required decoration
from functools import wraps
from flask import g, request, redirect, url_for, session, flash


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