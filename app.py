import os
from datetime import timedelta

import click
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

import config

from blueprint.admin.admin import admin_bp
from blueprint.cart import cart_bp
from blueprint.home import home_bp
from blueprint.auth import auth_bp
from blueprint.admin.product.product import product_bp
from blueprint.admin.promotion.promotion import promotion_bp
from blueprint.admin.category.category import category_bp
from blueprint.admin.customer.customer import customer_bp
from blueprint.admin.user.user import user_bp
from blueprint.order import order_bp
from blueprint.payment import payment_bp
from extensions import db, cache, limiter
from flask_migrate import Migrate
from models import User, Category
from blueprint.admin.report.report import report_bp


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///app.db'
)

migrate = Migrate(app, db)
db.init_app(app)
cache.init_app(app)
limiter.init_app(app)

app.config.from_object('config')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.register_blueprint(home_bp)
app.register_blueprint(product_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(category_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(user_bp)

app.register_blueprint(promotion_bp)

app.register_blueprint(payment_bp)

app.register_blueprint(cart_bp)
app.register_blueprint(order_bp)
app.register_blueprint(report_bp)

app.config['logo'] = 'static/admin/assets/images/logo-text-1.png'
app.config['title'] = 'Angkorkey'
app.config['icon'] = 'static/admin/assets/images/icon_logo.jpg'

app.config['SECRET_KEY'] = 'oythaiahleay168'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["logo"] = "sql_logo.jpg"


@app.before_request
def before_request():
    url = request.path
    if url.startswith('/admin/'):
        if not session.get('user_id'):
            flash('Please Login', 'danger')
            return redirect(url_for('auth.login'))
    return None

@app.route('/upload')
def index():
    return render_template('upload.html')

# for header categories info
@app.context_processor
def inject_categories():
    categories = Category.query.all()
    return dict(categories=categories)

# Define the command
@app.cli.command("create-admin")
@click.argument("name")
@click.argument("password")
def create_user(name, password):
    """Creates a new user. Usage: flask create-admin <name> <password>"""
    hashed_pw = generate_password_hash(password)

    # Check your User model to see if you need 'email' or 'phone' too!
    user = User(username=name, password=hashed_pw)

    db.session.add(user)
    db.session.commit()
    print(f"Successfully created user: {name}")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('frontend/error/404.html'), 404

@app.errorhandler(429)
def too_many_requests(error):
    return render_template('frontend/error/429.html'), 429


if __name__ == '__main__':
    app.run()
