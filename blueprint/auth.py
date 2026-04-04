from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, session,request
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from form.UserForm import LoginForm, RegisterForm
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        username_ = User.query.filter_by(username=username).first()
        if username_ and check_password_hash(username_.password, password):
            session.clear()
            session['user_id'] = username_.id
            session['username'] = username_.username
            session['image'] = username_.image
            flash(category="success", message="Login Successful")
            return redirect(url_for('admin.admin'))
        else:
            flash('Invalid username or password')
        return redirect(url_for('auth.login'))
    return render_template('backend/auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # TODO: Enable registration logic when ready
        # assert False , "Not yet implemented"
        username = form.username.data
        phone = form.phone.data
        password = generate_password_hash(form.password.data)
        user = User(username=username, phone=phone, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('backend/auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(f):
    @wraps(f)
    def login_required(*args, **kwargs):
        if 'customer_id' not in session:
            flash("You need to login first!", "warning")
            return redirect(url_for('home.customer_login',next=request.path))
        return f(*args, **kwargs)
    return login_required
