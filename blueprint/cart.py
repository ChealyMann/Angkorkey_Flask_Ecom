from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy.sql.functions import current_user

from blueprint.admin.product.product import product_variants
from extensions import db
from models import Cart, Product, ProductVariant
from functions.functions import login_required

cart_bp = Blueprint('cart_bp', __name__)


def _customer_id():
    """Return logged-in customer_id or None."""
    return session.get('customer_id')


@cart_bp.get('/cart')
@login_required
def view_cart():
    customer_id = _customer_id()

    # All rows for this customer — one query, no joins needed
    items = Cart.query.filter_by(customer_id=customer_id).all()

    total = round(sum(i.price * i.quantity for i in items), 2)
    total_quantity = sum(i.quantity for i in items)

    return render_template(
        'frontend/pages/cart.html',
        items=items,
        total=total,
        total_quantity=total_quantity,
        isinstance=isinstance
    )


@cart_bp.post('/cart/add')
@login_required
def add_to_cart():
    customer_id = _customer_id()

    product_id = request.form.get('product_id', type=int)
    variant_id = request.form.get('variant_id', type=int)  # None if not sent
    quantity = request.form.get('quantity', 1, type=int)

    # ── Basic validation ──────────────────────────────────────────
    if not product_id or quantity < 1:
        flash('Invalid request.', 'error')
        return redirect(request.referrer or url_for('cart.view_cart'))

    product = Product.query.get(product_id)
    if not product or product.status != 'true':
        flash('This product is not available.', 'error')
        return redirect(request.referrer or url_for('cart.view_cart'))

    # ── Resolve price, image, variant info ────────────────────────
    price = float(product.price)
    color = None
    vtype = None
    image = product.image  # fallback

    if product.images:
        primary = next((i for i in product.images if i.is_primary), None)
        image = (primary or product.images[0]).image

    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if not variant or variant.product_id != product_id:
            flash('Selected option not found.', 'error')
            return redirect(request.referrer or url_for('cart.view_cart'))

        available = (variant.physical_stock or 0) - (variant.reserved_stock or 0)

        if available <= 0:
            flash('Sorry, this option is out of stock.', 'error')
            return redirect(request.referrer or url_for('cart.view_cart'))

        price = float(variant.discount_price or variant.price or product.price)
        color = variant.color
        vtype = variant.type
        if variant.images:
            primary = next((i for i in variant.images if i.is_primary), None)
            image = (primary or variant.images[0]).image

    # ── Check for existing row (same customer + product + variant) ─
    try:
        existing = Cart.query.filter_by(
            customer_id=customer_id,
            product_id=product_id,
            variant_id=variant_id,
        ).first()

        if existing:
            # Guard stock for variants
            if variant_id:
                available = (variant.physical_stock or 0) - (variant.reserved_stock or 0)
                if existing.quantity + quantity > available:
                    flash(f'Only {available - existing.quantity} more unit(s) available.', 'warning')
                    return redirect(request.referrer or url_for('cart.view_cart'))
            existing.quantity += quantity
        else:
            # Insert a brand-new row
            new_row = Cart(
                customer_id=customer_id,
                product_id=product_id,
                variant_id=variant_id,
                product_name=product.name,
                color=color,
                variant_type=vtype,
                price=price,
                image=image,
                quantity=quantity,
            )
            db.session.add(new_row)

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
    # 1. Fix the IDs
    product_id = request.form.get('product_id', type=int)
    variant_id = request.form.get('variant_id', type=int)  # Fixed!
    customer_id = _customer_id()

    # 2. Fetch the item
    cart_item = Cart.query.filter_by(
        customer_id=customer_id,
        product_id=product_id,
        variant_id=variant_id
    ).first()

    # 3. Safety Check FIRST
    if not cart_item:
        flash('Item not found.', 'error')
        return redirect(url_for('cart_bp.view_cart'))

    # 4. Now it's safe to access .quantity
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.session.delete(cart_item)

    try:
        db.session.commit()
        flash('Item updated successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not update item.', 'error')
    return redirect(url_for('cart_bp.view_cart'))
