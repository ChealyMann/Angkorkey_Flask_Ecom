import re
from sqlite3 import DatabaseError
from flask import Blueprint, render_template, flash, redirect, url_for, request
from extensions import db
from models import Customer
from form.CustomerForm import CustomerForm,CustomerFormEdit
from werkzeug.security import generate_password_hash

customer_bp = Blueprint('customer', __name__)

# ==============================
# LIST CUSTOMER
# ==============================
@customer_bp.route('/admin/customer')
def admin_customer():
    customers = Customer.query.all()
    return render_template('backend/admin/pages/customer/customer.html', customers=customers)


# ==============================
# ADD CUSTOMER
# ==============================
@customer_bp.route('/admin/customer/add', methods=['GET', 'POST'])
def admin_customer_add():
    form = CustomerForm()

    if form.validate_on_submit():
        email = form.email.data.strip()
        phone = form.phone.data.strip()

        existing_customer = Customer.query.filter_by(email=email).first()
        existing_phone = Customer.query.filter_by(phone=phone).first()

        if existing_customer:
            flash("This email is already in use.", "danger")
            return render_template('backend/admin/pages/customer/add.html', form=form)

        if existing_phone:
            flash("This phone is already in use.", "danger")
            return render_template('backend/admin/pages/customer/add.html', form=form)

        customer = Customer(
            name=form.name.data.strip(),
            email=email,
            phone=phone,
            address=form.address.data.strip(),
            password=generate_password_hash(form.password.data)
        )

        try:
            db.session.add(customer)
            db.session.commit()
            flash('Customer has been added successfully!', 'success')
            return redirect(url_for('customer.admin_customer'))

        except Exception as e:
            db.session.rollback()
            flash('Error adding customer!', 'danger')
            print(e)

    return render_template('backend/admin/pages/customer/add.html', form=form)


# ==============================
# EDIT CUSTOMER
# ==============================
@customer_bp.route('/admin/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
def admin_customer_edit(customer_id):

    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        form = CustomerFormEdit()
    else:
        form = CustomerFormEdit(obj=customer)

    if form.validate_on_submit():
        new_email = (form.email.data or "").strip().lower()
        new_phone = (form.phone.data or "").strip()
        new_address = (form.address.data or "").strip()

        existing_customer = Customer.query.filter(
            Customer.email == new_email,
            Customer.id != customer_id
        ).first()

        existing_phone = Customer.query.filter(
            Customer.phone == new_phone,
            Customer.id != customer_id
        ).first()

        if existing_customer:
            flash("This email is already in use by another account.", "error")
            return render_template('backend/admin/pages/customer/edit.html', form=form, customer=customer)

        if existing_phone:
            flash("This phone is already in use by another account.", "error")
            return render_template('backend/admin/pages/customer/edit.html', form=form, customer=customer)

        if not re.match(r'^[a-zA-Z0-9\s,.-]{5,200}$', new_address):
            flash("Invalid address format", "error")
            return render_template('backend/admin/pages/customer/edit.html', form=form, customer=customer)

        # update
        customer.name = (form.name.data or "").strip()
        customer.email = new_email
        customer.phone = new_phone
        customer.address = new_address

        if form.password.data:
            customer.password = generate_password_hash(form.password.data)

        try:
            db.session.commit()
            flash('Customer has been updated successfully!', 'success')
            return redirect(url_for('customer.admin_customer'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating customer!', 'danger')
            print(e)

    else:
        print(form.errors)

    return render_template(
        'backend/admin/pages/customer/edit.html',
        form=form,
        customer=customer
    )


# ==============================
# DELETE CUSTOMER
# ==============================
@customer_bp.route('/admin/customer/delete/<int:customer_id>', methods=['POST'])
def admin_customer_delete(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('Customer has been deleted successfully!', 'success')

    except (ValueError, TypeError, Exception, DatabaseError) as e:
        db.session.rollback()
        print(e)
        flash('Error deleting customer', 'danger')

    return redirect(url_for('customer.admin_customer'))