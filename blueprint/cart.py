from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy.sql.functions import current_user

from blueprint.admin.product.product import product_variants
from extensions import db
from models import Cart, Product, ProductVariant
from functions.functions import login_required
from functions.functions import _cart_payload, _customer_id

cart_bp = Blueprint('cart_bp', __name__)


@cart_bp.get('/cart')
@login_required
def view_cart():
    customer_id = _customer_id()
    items = Cart.query.filter_by(customer_id=customer_id).all()
    total = round(sum(i.price * i.quantity for i in items), 2)
    total_quantity = sum(i.quantity for i in items)

    return render_template(
        'frontend/pages/cart.html',
        items=items,
        total=total,
        total_quantity=total_quantity,
        isinstance=isinstance,
    )


@cart_bp.post('/cart/add')
@login_required
def add_to_cart():
    customer_id = _customer_id()
    product_id = request.form.get('product_id', type=int)
    variant_id = request.form.get('variant_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)

    if not product_id or quantity < 1:
        flash('Invalid request.', 'error')
        return redirect(request.referrer or url_for('cart_bp.view_cart'))

    product = Product.query.get(product_id)
    if not product or product.status != 'true':
        flash('This product is not available.', 'error')
        return redirect(request.referrer or url_for('cart_bp.view_cart'))

    price = float(product.price)
    color = None
    vtype = None
    image = product.image

    if product.images:
        primary = next((i for i in product.images if i.is_primary), None)
        image = (primary or product.images[0]).image

    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if not variant or variant.product_id != product_id:
            flash('Selected option not found.', 'error')
            return redirect(request.referrer or url_for('cart_bp.view_cart'))

        available = (variant.physical_stock or 0) - (variant.reserved_stock or 0)
        if available <= 0:
            flash('Sorry, this option is out of stock.', 'error')
            return redirect(request.referrer or url_for('cart_bp.view_cart'))

        price = float(variant.discount_price or variant.price or product.price)
        color = variant.color
        vtype = variant.type
        if variant.images:
            primary = next((i for i in variant.images if i.is_primary), None)
            image = (primary or variant.images[0]).image

    try:
        existing = Cart.query.filter_by(
            customer_id=customer_id,
            product_id=product_id,
            variant_id=variant_id,
            status = 1
        ).first()

        if existing:
            if variant_id:
                available = variant.available_stock  # ← use the safe property
                remaining = max(0, available - existing.quantity)  # ← clamp to 0
                if existing.quantity + quantity > available:
                    flash(f'Only {remaining} more unit(s) available.', 'warning')
                    return redirect(request.referrer or url_for('cart_bp.view_cart'))
            existing.quantity += quantity
        else:
            db.session.add(Cart(
                customer_id=customer_id, product_id=product_id, variant_id=variant_id,
                product_name=product.name, color=color, variant_type=vtype,
                price=price, image=image, quantity=quantity,
            ))

        db.session.commit()
        flash(f'"{product.name}" added to your cart.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not add item. Please try again.', 'error')

    return redirect(url_for('cart_bp.view_cart'))


@cart_bp.post('/cart/remove')
@login_required
def remove_from_cart():
    customer_id = _customer_id()
    row_id = request.form.get('row_id', type=int)

    if not row_id:
        flash('Invalid request.', 'error')
        return redirect(url_for('cart_bp.view_cart'))

    row = Cart.query.filter_by(id=row_id, customer_id=customer_id).first()
    if not row:
        flash('Item not found.', 'error')
        return redirect(url_for('cart_bp.view_cart'))

    try:
        db.session.delete(row)
        db.session.commit()
        flash('Item removed from cart.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not remove item.', 'error')

    return redirect(url_for('cart_bp.view_cart'))


@cart_bp.post('/cart/update')
@login_required
def update_cart():
    customer_id = _customer_id()
    product_id = request.form.get('product_id', type=int)
    variant_id = request.form.get('variant_id', type=int)

    cart_item = Cart.query.filter_by(
        customer_id=customer_id,
        product_id=product_id,
        variant_id=variant_id,
    ).first()

    if not cart_item:
        flash('Item not found.', 'error')
        return redirect(url_for('cart_bp.view_cart'))

    try:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            db.session.delete(cart_item)

        db.session.commit()
        flash('Item updated successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not update item.', 'error')

    return redirect(url_for('cart_bp.view_cart'))


# ─────────────────────────────────────────────────────────────
#  JSON API ROUTES  (used by Vue frontend)
# ─────────────────────────────────────────────────────────────

@cart_bp.get('/api/cart')
def carts():
    """Return the full cart for the logged-in customer."""
    customer_id = _customer_id()
    return jsonify(_cart_payload(customer_id)), 200


@cart_bp.post('/api/cart/add')
@login_required
def add_to_cart_api():
    """Add one or more units of a product/variant to the cart."""
    customer_id = _customer_id()
    data = request.get_json(silent=True) or {}

    product_id = data.get('product_id')
    variant_id = data.get('variant_id')
    quantity = data.get('quantity', 1)

    if not product_id or quantity < 1:
        return jsonify(success=False, message='Invalid request.'), 400

    product = Product.query.get(product_id)
    if not product or product.status != 'true':
        return jsonify(success=False, message='Product not available.'), 404

    price = float(product.price)
    color = None
    vtype = None
    image = product.image

    if product.images:
        primary = next((i for i in product.images if i.is_primary), None)
        image = (primary or product.images[0]).image

    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if not variant or variant.product_id != product_id:
            return jsonify(success=False, message='Selected option not found.'), 404

        available = (variant.physical_stock or 0) - (variant.reserved_stock or 0)
        if available <= 0:
            return jsonify(success=False, message='Sorry, this option is out of stock.'), 409

        price = float(variant.discount_price or variant.price or product.price)
        color = variant.color
        vtype = variant.type
        if variant.images:
            primary = next((i for i in variant.images if i.is_primary), None)
            image = (primary or variant.images[0]).image

    try:
        existing = Cart.query.filter_by(
            customer_id=customer_id,
            product_id=product_id,
            variant_id=variant_id,
            status = 1
        ).first()

        if existing:
            if variant_id:
                available = variant.available_stock  # ← use the safe property
                remaining = max(0, available - existing.quantity)  # ← clamp to 0
                if existing.quantity + quantity > available:
                    return jsonify(
                        success=False,
                        message=f'Only {remaining} more unit(s) available.',
                        available=remaining,
                    ), 409
            existing.quantity += quantity
        else:
            db.session.add(Cart(
                customer_id=customer_id, product_id=product_id, variant_id=variant_id,
                product_name=product.name, color=color, variant_type=vtype,
                price=price, image=image, quantity=quantity,
            ))

        db.session.commit()
        return jsonify(
            success=True,
            message=f'"{product.name}" added to your cart.',
            cart=_cart_payload(customer_id),
        ), 200

    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Could not add item. Please try again.'), 500


@cart_bp.post('/api/cart/decrease')
@login_required
def decrease_cart_api():
    """Decrease quantity by 1. Removes the row when it reaches 0."""
    customer_id = _customer_id()
    data = request.get_json(silent=True) or {}

    product_id = data.get('product_id')
    variant_id = data.get('variant_id')  # may be None

    if not product_id:
        return jsonify(success=False, message='Invalid request.'), 400

    cart_item = Cart.query.filter_by(
        customer_id=customer_id,
        product_id=product_id,
        variant_id=variant_id,
    ).first()

    if not cart_item:
        return jsonify(success=False, message='Item not found.'), 404

    try:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            db.session.delete(cart_item)

        db.session.commit()
        return jsonify(
            success=True,
            message='Cart updated.',
            cart=_cart_payload(customer_id),
        ), 200

    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Could not update item.'), 500


@cart_bp.post('/api/cart/remove')
@login_required
def remove_from_cart_api():
    """Completely remove a cart row by its id."""
    customer_id = _customer_id()
    data = request.get_json(silent=True) or {}
    row_id = data.get('row_id')

    if not row_id:
        return jsonify(success=False, message='Invalid request.'), 400

    row = Cart.query.filter_by(id=row_id, customer_id=customer_id).first()
    if not row:
        return jsonify(success=False, message='Item not found.'), 404

    try:
        db.session.delete(row)
        db.session.commit()
        return jsonify(
            success=True,
            message='Item removed.',
            cart=_cart_payload(customer_id),
        ), 200

    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Could not remove item.'), 500
