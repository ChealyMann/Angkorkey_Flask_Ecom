from enum import IntEnum

from flask import Blueprint, jsonify, request, redirect, url_for, flash, render_template
from flask_paginate import get_page_parameter, Pagination
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from functions.functions import _cart_payload, _customer_id, generate_secure_invoice, login_required
from models import Order, OrderItem, Cart
from extensions import db
from datetime import datetime, time
from zoneinfo import ZoneInfo


order_bp = Blueprint('order', __name__)

# ── Geopy ────────────────────────────────────────────────────────────────────
_geolocator = Nominatim(user_agent="my_shop_app/1.0")


# ── Status helpers ───────────────────────────────────────────────────────────

class OrderStatus(IntEnum):
    PENDING = 1
    CONFIRMED = 2
    SHIPPED = 3
    DELIVERED = 4
    CANCELED = 5
    RETURNED = 6


VALID_TRANSITIONS = {
    (OrderStatus.PENDING, OrderStatus.CONFIRMED): "Confirmed",
    (OrderStatus.PENDING, OrderStatus.CANCELED): "Canceled",
    (OrderStatus.CONFIRMED, OrderStatus.PENDING): "Pending",
    (OrderStatus.CONFIRMED, OrderStatus.SHIPPED): "Shipped",
    (OrderStatus.CONFIRMED, OrderStatus.CANCELED): "Canceled",
    (OrderStatus.SHIPPED, OrderStatus.DELIVERED): "Delivered",
    (OrderStatus.SHIPPED, OrderStatus.RETURNED): "Returned",
    (OrderStatus.DELIVERED, OrderStatus.RETURNED): "Returned",
}


def _apply_stock_changes(order, current_status, new_status):
    for item in order.items:
        variant = item.variants

        if new_status == OrderStatus.CANCELED and current_status in (
                OrderStatus.PENDING, OrderStatus.CONFIRMED
        ):
            variant.reserved_stock -= item.qty

        elif (current_status, new_status) == (OrderStatus.CONFIRMED, OrderStatus.SHIPPED):
            variant.reserved_stock -= item.qty
            variant.physical_stock -= item.qty

        elif (current_status, new_status) == (OrderStatus.SHIPPED, OrderStatus.CANCELED):
            variant.physical_stock += item.qty


        elif (current_status, new_status) in [

            (OrderStatus.SHIPPED, OrderStatus.RETURNED),

            (OrderStatus.DELIVERED, OrderStatus.RETURNED),

        ]:

            variant.physical_stock += item.qty


# ── Checkout page ─────────────────────────────────────────────────────────────

@order_bp.get('/checkout')
@login_required
def checkout():
    """Render the checkout page with live cart data."""
    customer_id = _customer_id()
    cart = _cart_payload(customer_id)

    if not cart['items']:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('cart_bp.view_cart'))

    return render_template('frontend/pages/checkout.html', cart=cart)


# ── Place order ───────────────────────────────────────────────────────────────

@order_bp.post('/order')
@login_required
def order():
    customer_id = _customer_id()
    items = _cart_payload(customer_id)

    if not items['items']:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('cart_bp.view_cart'))

    phone = request.form.get('phone', '').strip()
    payment_method = request.form.get('payment_method', 'cash_on_delivery').strip()

    try:
        lat = float(request.form.get('latitude', ''))
        lng = float(request.form.get('longitude', ''))
    except (ValueError, TypeError):
        flash('Please drop a pin on the map to set your delivery location.', 'danger')
        return redirect(url_for('order.checkout'))

    if not phone:
        flash('Please enter your phone number.', 'danger')
        return redirect(url_for('order.checkout'))

    address = 'Unknown'
    city = 'Unknown'
    full_address = None

    try:
        location = _geolocator.reverse((lat, lng), language='en', timeout=10)
        if location:
            raw = location.raw.get('address', {})
            parts = [p for p in [
                raw.get('house_number'),
                raw.get('road'),
                raw.get('suburb') or raw.get('quarter'),
            ] if p]
            address = ', '.join(parts) or location.address.split(',')[0]
            city = (
                raw.get('city') or raw.get('town') or
                raw.get('village') or raw.get('county') or
                raw.get('state', 'Unknown')
            )
            full_address = location.address
    except (GeocoderTimedOut, GeocoderServiceError):
        address = f'{lat:.5f}, {lng:.5f}'
        city = 'Unknown'
        full_address = f'Coordinates: {lat:.5f}, {lng:.5f}'

    # All orders start as pending; bakong is confirmed paid via webhook/polling
    payment_status = 'pending'

    new_order = Order(
        customer_id=customer_id,
        phone=phone,
        address=address,
        city=city,
        full_address=full_address,
        latitude=lat,
        longitude=lng,
        sub_total=items['summary']['total'],
        grand_total=items['summary']['total'],
        payment_method=payment_method,
        payment_status=payment_status,   # make sure this column exists
    )
    db.session.add(new_order)
    db.session.flush()

    bill_number = generate_secure_invoice(new_order.id)
    new_order.invoice_no = bill_number

    for item in items['items']:
        order_item = OrderItem()
        order_item.product_id = item['product_id']
        order_item.order_id = new_order.id
        order_item.variant_id = item['variant_id']
        order_item.qty = item['quantity']
        order_item.unit_price = item['price']
        order_item.sub_total = item['quantity'] * item['price']
        db.session.add(order_item)

    cart_items = Cart.query.filter_by(customer_id=customer_id, status=1).all()
    if not cart_items:
        db.session.rollback()
        flash('No cart items found.', 'danger')
        return redirect(url_for('cart_bp.view_cart'))

    for item in cart_items:
        new_reserved_stock = item.variant.reserved_stock + item.quantity

        # check BEFORE saving
        if item.variant.physical_stock < new_reserved_stock:
            flash(f'Sorry, out of stock: {item.product_name} – {item.variant.color}', 'danger')
            db.session.rollback()
            return redirect(url_for('cart_bp.view_cart'))

        item.variant.reserved_stock = new_reserved_stock
        item.status = 0

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Something went wrong placing your order. Please try again.', 'danger')
        raise e

    if payment_method == 'bakong_khqr':
        return redirect(
            url_for('payment.payment', amount=items['summary']['total'], currency='USD', bill_number=bill_number))

    flash(f'Order #{new_order.invoice_no} placed successfully! 🎉', 'success')
    return redirect(url_for('home.home'))


# ── Reverse Geocode API ───────────────────────────────────────────────────────

@order_bp.get('/api/geocode/reverse')
@login_required
def reverse_geocode():
    try:
        lat = float(request.args.get('lat', ''))
        lng = float(request.args.get('lng', ''))
    except (ValueError, TypeError):
        return jsonify(success=False, message='Invalid or missing coordinates.'), 400

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return jsonify(success=False, message='Coordinates out of range.'), 400

    try:
        location = _geolocator.reverse((lat, lng), language='en', timeout=10)
    except GeocoderTimedOut:
        return jsonify(success=False, message='Geocoder timed out, try again.'), 504
    except GeocoderServiceError as exc:
        return jsonify(success=False, message=str(exc)), 502

    if location is None:
        return jsonify(success=False, message='No address found for those coordinates.')

    raw = location.raw.get('address', {})

    # Build readable street from OSM components
    parts = [p for p in [raw.get('house_number'), raw.get('road'), raw.get('suburb') or raw.get('quarter')] if p]
    street = ', '.join(parts) or raw.get('display_name', '').split(',')[0]

    city = (
            raw.get('city')
            or raw.get('town')
            or raw.get('village')
            or raw.get('county')
            or raw.get('state', '')
    )

    return jsonify(
        success=True,
        address=location.address,
        street=street,
        city=city,
        country=raw.get('country', ''),
        postcode=raw.get('postcode', ''),
    )


# ── Admin: Order List ────────────────────────────────────────────────────────

@order_bp.route('/admin/order')
def order_list():
    cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
    today_kh = datetime.now(cambodia_tz).date()

    selected_date = request.args.get('order_date', '').strip()
    sort_order = request.args.get('sort', 'desc').strip().lower()

    page = request.args.get(get_page_parameter(), default=1, type=int)
    per_page = 7

    query = Order.query

    # default = today Cambodia time
    filter_date = today_kh

    if selected_date:
        try:
            filter_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            filter_date = today_kh

    start_dt = datetime.combine(filter_date, time.min).replace(tzinfo=cambodia_tz)
    end_dt = datetime.combine(filter_date, time.max).replace(tzinfo=cambodia_tz)

    query = query.filter(
        Order.created_at >= start_dt,
        Order.created_at <= end_dt
    )

    if sort_order == 'asc':
        query = query.order_by(Order.created_at.asc())
    else:
        query = query.order_by(Order.created_at.desc())

    pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=pagination_obj.total,
        css_framework='bootstrap5'
    )

    return render_template(
        'backend/admin/pages/order/order.html',
        orders={
            'list': pagination_obj.items,
            'pagination': pagination,
        },
        selected_date=filter_date.strftime('%Y-%m-%d'),
        sort_order=sort_order
    )


@order_bp.route('/admin/order/delete/<int:order_id>', methods=['POST'])
def order_delete(order_id):
    order = db.get_or_404(Order, order_id)
    try:
        if order.status == 5:
            db.session.delete(order)
            db.session.commit()
            flash('Order deleted successfully.', 'success')
        else:
            flash('Only canceled orders can be deleted.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete order: {str(e)}', 'danger')

    return redirect(url_for('order.order_list'))


@order_bp.route('/admin/order/detail/<int:order_id>')
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('backend/admin/pages/order/order_detail.html', order=order)


@order_bp.route('/admin/order/update_status', methods=['POST'])
def update_status():
    order_id = int(request.form['order_id'])
    order = db.get_or_404(Order, order_id)

    try:
        new_status = OrderStatus(int(request.form['status']))
    except (ValueError, KeyError):
        flash('Invalid status value.', 'danger')
        return redirect(url_for('order.order_detail', order_id=order.id))

    current_status = OrderStatus(order.status)

    if current_status == new_status:
        return redirect(url_for('order.order_detail', order_id=order.id))

    label = VALID_TRANSITIONS.get((current_status, new_status))
    if label is None:
        flash('Invalid status transition.', 'danger')
        return redirect(url_for('order.order_detail', order_id=order.id))

    try:
        _apply_stock_changes(order, current_status, new_status)
        order.status = new_status

        if order.payment_method == 'cash_on_delivery':
            if new_status == OrderStatus.DELIVERED:
                order.payment_status = 'paid'
            elif new_status == OrderStatus.RETURNED:
                order.payment_status = 'pending'   # or 'refunded' if you track refunds

        db.session.commit()
        flash(f'Order status changed to {label}.', 'success')
    except Exception:
        db.session.rollback()
        flash('Something went wrong updating the order. Please try again.', 'danger')

    return redirect(url_for('order.order_detail', order_id=order.id))