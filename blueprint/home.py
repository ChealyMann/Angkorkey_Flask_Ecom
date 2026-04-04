import re
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template, request, flash, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from models import Category, Product, Promotion,Customer,CustomerLocation
from extensions import db
from blueprint.auth import login_required
from models.Product import getProductDetail

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
@home_bp.route("/home")
def home():
    products = Product.query.limit(4).all()
    promotions = Promotion.query.filter_by(is_active=True).all()
    categories = Category.query.limit(4).all()
    return render_template("frontend/pages/index.html", products=products, promotions=promotions, categories=categories)


@home_bp.route("/product_detail/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    product_variant = getProductDetail(product_id)


    # Fetch related products (Same Category, exclude current)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()

    # Fallback: If less than 4 related, fill with random/latest products
    if len(related_products) < 4:
        needed = 4 - len(related_products)
        excluded_ids = [p.id for p in related_products] + [product.id]
        more_products = Product.query.filter(Product.id.notin_(excluded_ids)).limit(needed).all()
        related_products.extend(more_products)

    return render_template("frontend/pages/product-detail.html", product=product, related_products=related_products,product_variant=product_variant)


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
    # 1. Capture Filters
    search_query = request.args.get("search", "").strip()
    # Prioritize path parameter, then query parameter
    if category_id is None:
        category_id = request.args.get("category_id", type=int)
    is_ajax = request.args.get("ajax", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = 8  # Show 8 products per page

    # 2. Build Query
    # Optimize: Select only necessary columns
    query = Product.query.options(
        db.load_only(
            Product.id,
            Product.name,
            Product.price,
            Product.old_price,
            Product.image,
            Product.category_id
        )
    )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))

    # 3. Execute Pagination
    # error_out=False effectively handles out of range pages
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products_list = pagination.items

    # 4. AJAX RESPONSE: Return JSON with grid and pagination HTML
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

    # 5. STANDARD RESPONSE: Return full page
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

    # Load customer WITH locations
    customer = Customer.query.options(
        joinedload(Customer.locations)
    ).get_or_404(customer_id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Validation
        if not name or not email:
            flash("Name and Email are required.", "error")
            return redirect(url_for('home.customer_profile'))

        if phone and not re.match(r"^[0-9+\-\s]{7,15}$", phone):
            flash("Invalid phone number.", "error")
            return redirect(url_for('home.customer_profile'))

        # Check duplicate email
        existing_customer = Customer.query.filter(
            Customer.email == email,
            Customer.id != customer_id
        ).first()

        if existing_customer:
            flash("This email is already in use.", "error")
            return redirect(url_for('home.customer_profile'))

        # Check duplicate phone (only if phone exists)
        if phone:
            existing_phone = Customer.query.filter(
                Customer.phone == phone,
                Customer.id != customer_id
            ).first()

            if existing_phone:
                flash("This phone is already in use.", "error")
                return redirect(url_for('home.customer_profile'))

        #  Update ONLY basic info (DO NOT TOUCH locations)
        customer.name = name
        customer.email = email
        customer.phone = phone

        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('home.customer_profile'))

    #  Render with locations
    return render_template(
        'frontend/pages/customer_profile.html',
        customer=customer
    )

@home_bp.route("/add-location", methods=["POST"])
def add_location():
    from flask import redirect
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Unauthorized", "error")
        return redirect(url_for('home.customer_profile'))

    try:
        data = request.get_json()

        label = data.get("label", "Address")
        address = data.get("address")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not address:
            flash("Address is required", "error")
            return redirect(url_for('home.customer_profile'))

        # check duplicate location
        existing_location = CustomerLocation.query.filter_by(
            customer_id=customer_id,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        ).first()

        if existing_location:
            flash("Location already exists", "error")
            return redirect(url_for('home.customer_profile'))

        # check duplicate label
        existing_label = CustomerLocation.query.filter_by(
            customer_id=customer_id,
            label=label
        ).first()

        if existing_label:
            flash("Label already exists", "error")
            return redirect(url_for('home.customer_profile'))

        # create
        new_location = CustomerLocation(
            customer_id=customer_id,
            label=label,
            address=address,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )

        db.session.add(new_location)
        db.session.commit()

        flash("Location added successfully!", "success")
        return redirect(url_for('home.customer_profile'))

    except Exception as e:
        print("ERROR:", e)
        flash("Server error", "error")
        return redirect(url_for('home.customer_profile'))

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

@home_bp.route('/customer/order', methods=['GET', 'POST'])
def customer_order():
    return render_template('frontend/pages/customer_order.html')

@home_bp.route('/customer/order_detail', methods=['GET', 'POST'])
def customer_order_detail():
    return render_template('frontend/pages/customer_order_detail.html')


