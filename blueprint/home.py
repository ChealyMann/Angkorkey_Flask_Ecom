from flask import Blueprint, render_template, request
from models import Category, Product, Promotion
from extensions import db
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


@home_bp.route("/cart")
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
