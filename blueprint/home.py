import re
from flask import Blueprint, render_template, request, flash, url_for, session
from sqlalchemy.orm import subqueryload
from werkzeug.security import check_password_hash, generate_password_hash
from models import Category, Product, Promotion, Customer, OrderItem, Cart

from models import Category, Product, Promotion, Customer, ProductVariant
from extensions import db
from blueprint.auth import login_required
from models.Product import getProductDetail
from functions.functions import generate_secure_invoice
from models import Category, Product, Promotion, Customer, ProductVariant, Order


home_bp = Blueprint("home", __name__)

def add_price_range(products):
    for product in products:
        prices = []

        if getattr(product, "variants", None):
            for variant in product.variants:
                if variant.discount_price and variant.discount_price != 0.0:
                    price = float(variant.discount_price)
                elif variant.price is not None:
                    price = float(variant.price)
                else:
                    continue
                prices.append(price)

        if prices:
            product.min_price = min(prices)
            product.max_price = max(prices)
            product.has_price_range = product.min_price != product.max_price
        else:
            base_price = float(product.price or 0)
            product.min_price = base_price
            product.max_price = base_price
            product.has_price_range = False

    return products


def get_payment_status_meta(payment_status):
    payment_status = (payment_status or "").lower()

    if payment_status == "paid":
        return {
            "label": "Paid",
            "color": "bg-green-500/15 text-green-300 border-green-500/20"
        }

    elif payment_status in ["failed", "cancelled", "canceled"]:
        return {
            "label": payment_status.capitalize(),
            "color": "bg-red-500/15 text-red-300 border-red-500/20"
        }

    return {
        "label": "Pending",
        "color": "bg-yellow-500/15 text-yellow-300 border-yellow-500/20"
    }


def get_order_status_meta(status_code):
    status_map = {
        1: {
            "label": "Pending",
            "step": 1,
            "description": "Your order has been placed and is waiting for confirmation.",
            "color": "bg-yellow-500/15 text-yellow-300 border-yellow-500/20"
        },
        2: {
            "label": "Confirmed",
            "step": 2,
            "description": "Your order has been confirmed and will be prepared for shipment.",
            "color": "bg-blue-500/15 text-blue-300 border-blue-500/20"
        },
        3: {
            "label": "Shipped",
            "step": 3,
            "description": "Your order has been shipped and is on the way.",
            "color": "bg-purple-500/15 text-purple-300 border-purple-500/20"
        },
        4: {
            "label": "Delivered",
            "step": 4,
            "description": "Your order has been delivered successfully.",
            "color": "bg-green-500/15 text-green-300 border-green-500/20"
        },
        5: {
            "label": "Canceled",
            "step": 0,
            "description": "This order was canceled.",
            "color": "bg-red-500/15 text-red-300 border-red-500/20"
        },
        6: {
            "label": "Returned",
            "step": 0,
            "description": "This order was returned.",
            "color": "bg-orange-500/15 text-orange-300 border-orange-500/20"
        }
    }

    return status_map.get(status_code, {
        "label": "Unknown",
        "step": 0,
        "description": "Order status unavailable.",
        "color": "bg-gray-500/15 text-gray-300 border-gray-500/20"
    })


def enrich_order_for_tracking(order):
    order.status_meta = get_order_status_meta(order.status)
    order.payment_meta = get_payment_status_meta(order.payment_status)

    tracking_steps = [
        {"key": 1, "label": "Pending"},
        {"key": 2, "label": "Confirmed"},
        {"key": 3, "label": "Shipped"},
        {"key": 4, "label": "Delivered"},
    ]

    current_step = order.status_meta["step"]

    for step in tracking_steps:
        if order.status in [5, 6]:
            step["done"] = False
            step["active"] = False
        else:
            step["done"] = step["key"] < current_step
            step["active"] = step["key"] == current_step

    order.tracking_steps = tracking_steps
    order.item_count = sum(item.qty for item in order.items) if order.items else 0
    return order

@home_bp.route("/")
@home_bp.route("/home")
def home():
    products = Product.query.options(subqueryload(Product.variants)).limit(4).all()
    products = add_price_range(products)

    promotions = Promotion.query.filter_by(is_active=True).all()
    categories = Category.query.limit(4).all()

    return render_template(
        "frontend/pages/index.html",
        products=products,
        promotions=promotions,
        categories=categories
    )


@home_bp.route("/product_detail/<int:product_id>")
def product_detail(product_id):
    product = Product.query.options(
        subqueryload(Product.variants)
    ).get_or_404(product_id)

    product_variant = getProductDetail(product_id)

    related_products = Product.query.options(
        subqueryload(Product.variants)
    ).filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()

    if len(related_products) < 4:
        needed = 4 - len(related_products)
        excluded_ids = [p.id for p in related_products] + [product.id]

        more_products = Product.query.options(
            subqueryload(Product.variants)
        ).filter(
            Product.id.notin_(excluded_ids)
        ).limit(needed).all()

        related_products.extend(more_products)

    # IMPORTANT: do this AFTER all related products are added
    related_products = add_price_range(related_products)

    return render_template(
        "frontend/pages/product-detail.html",
        product=product,
        related_products=related_products,
        product_variant=product_variant
    )


# Protect Cart Route


@home_bp.route("/cart")
@login_required
def cart():
    return render_template("frontend/pages/cart.html")


@home_bp.route("/categories")
def all_categories():
    categories = Category.query.all()
    return render_template("frontend/pages/all_categories.html", categories=categories)


@home_bp.route("/products")
@home_bp.route("/category/<int:category_id>")
def products(category_id=None):
    search_query = request.args.get("search", "").strip()

    if category_id is None:
        category_id = request.args.get("category_id", type=int)

    is_ajax = request.args.get("ajax", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = 8

    query = Product.query.options(
        db.load_only(
            Product.id,
            Product.name,
            Product.price,
            Product.old_price,
            Product.image,
            Product.category_id,
            Product.status,
        ),
        subqueryload(Product.variants)
    )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products_list = add_price_range(pagination.items)

    if is_ajax:
        from flask import jsonify
        return jsonify({
            'html': render_template(
                "frontend/layouts/product_grid.html",
                products=products_list
            ),
            'pagination': render_template(
                "frontend/layouts/_pagination.html",
                pagination=pagination
            ),
            'has_next': pagination.has_next
        })

    categories = Category.query.all()
    return render_template(
        "frontend/pages/products.html",
        products=products_list,
        categories=categories,
        current_category=category_id,
        pagination=pagination
    )


@home_bp.route("/promotions")
def promotions():
    search_query = request.args.get("search", "").strip()
    is_ajax = request.args.get("ajax", type=int)

    # Fetch products with valid old_price (active promotion)
    query = Product.query.filter(
        Product.old_price.isnot(None),
        Product.old_price > Product.price
    )

    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))

    products = query.all()

    if is_ajax:
        from flask import jsonify
        return jsonify({
            'html': render_template("frontend/layouts/product_grid.html", products=products)
        })

    return render_template("frontend/pages/promotion_products.html", products=products)

@home_bp.route('/customer/profile', methods=['GET', 'POST'])
def customer_profile():
    from flask import redirect
    customer_id = session.get('customer_id')

    if not customer_id:
        flash("Please log in to access your profile.", "error")
        return redirect(url_for('home.customer_login'))

    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if not name or not email:
            flash("Name and Email are required.", "error")
            return redirect(url_for('home.customer_profile'))

        if phone and not re.match(r"^[0-9+\-\s]{7,15}$", phone):
            flash("Invalid phone number.", "error")
            return redirect(url_for('home.customer_profile'))


        # check email exists for another user
        existing_customer = Customer.query.filter(
            Customer.email == email,
            Customer.id != customer_id
        ).first()

        existing_phone = Customer.query.filter(
            Customer.phone == phone,
            Customer.id != customer_id
        ).first()

        if existing_customer:
            flash("This email is already in use by another account.", "error")
            return redirect(url_for('home.customer_profile'))

        if existing_phone:
            flash("This email is already in use by another account.", "error")
            return redirect(url_for('home.customer_profile'))

        # update data
        customer.name = name
        customer.email = email
        customer.phone = phone
        customer.address = address

        db.session.commit()

        flash("Profile updated successfully!", "success")

        # reload profile page with updated data
        return redirect(url_for('home.customer_profile'))

    # reload latest data
    customer = Customer.query.get(customer_id)

    return render_template(
        'frontend/pages/customer_profile.html',
        customer=customer
    )

@home_bp.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    from flask import redirect
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        # validation
        if not name or not email or not password:
            flash("Name, Email and Password are required.", "error")
            return render_template(
                'frontend/pages/customer_register.html',
                name=name,
                email=email,
                phone=phone
            )

        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash("Email already registered.", "error")
            return render_template(
                'frontend/pages/customer_register.html',
                name=name,
                email=email,
                phone=phone
            )

        existing_phone = Customer.query.filter_by(phone=phone).first()
        if existing_phone:
            flash("Phone already registered.", "error")
            return render_template(
                'frontend/pages/customer_register.html',
                name=name,
                email=email,
                phone=phone
            )

        hashed_password = generate_password_hash(password)

        new_customer = Customer(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password
        )

        db.session.add(new_customer)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for('home.customer_login'))

    return render_template('frontend/pages/customer_register.html')

@home_bp.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    from app import redirect

    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and Password are required.", "error")
            return redirect(url_for('home.customer_login', next=next_page))

        customer = Customer.query.filter_by(email=email).first()

        if not customer:
            flash("No account found with this email.", "error")
            return redirect(url_for('home.customer_login', next=next_page))

        if not check_password_hash(customer.password, password):
            flash("Incorrect password.", "error")
            return redirect(url_for('home.customer_login', next=next_page))

        # Login success
        session['customer_id'] = customer.id
        flash("Logged in successfully!", "success")

        if next_page:
            return redirect(next_page)

        return redirect(url_for('home.customer_profile'))

    return render_template('frontend/pages/customer_login.html')

@home_bp.route('/customer/logout', methods=['POST'])
def customer_logout():
    from flask import redirect
    session.pop('customer_id', None)
    return redirect(url_for('home.home'))

@home_bp.route('/customer/orders')
def customer_orders():
    from flask import redirect

    customer_id = session.get('customer_id')
    if not customer_id:
        flash("Please log in to view your orders.", "error")
        return redirect(url_for('home.customer_login', next=url_for('home.customer_orders')))

    customer = Customer.query.get_or_404(customer_id)

    orders = (
        Order.query
        .options(
            subqueryload(Order.items)
            .joinedload(OrderItem.product)
            .subqueryload(Product.images),

            subqueryload(Order.items)
            .joinedload(OrderItem.variants)
            .subqueryload(ProductVariant.images)
        )
        .filter_by(customer_id=customer_id)
        .order_by(Order.created_at.desc())
        .all()
    )

    orders = [enrich_order_for_tracking(order) for order in orders]

    # assert False , orders[0].items[0].variants.images[0].image

    return render_template(
        'frontend/pages/customer_orders.html',
        customer=customer,
        orders=orders
    )

@home_bp.route('/customer/orders/<int:order_id>')
def customer_order_detail(order_id):
    from flask import redirect

    customer_id = session.get('customer_id')
    if not customer_id:
        flash("Please log in to view your order.", "error")
        return redirect(url_for('home.customer_login', next=url_for('home.customer_order_detail', order_id=order_id)))

    order = (
        Order.query
        .options(
            subqueryload(Order.items)
            .joinedload(OrderItem.product)
            .subqueryload(Product.images),

            subqueryload(Order.items)
            .joinedload(OrderItem.variants)
            .subqueryload(ProductVariant.images)
        )
        .filter_by(id=order_id, customer_id=customer_id)
        .first_or_404()
    )

    order = enrich_order_for_tracking(order)

    return render_template(
        'frontend/pages/customer_order_detail.html',
        order=order
    )
