from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from extensions import db
from form.UserForm import UserForm, UserFormEdit
from models import User
from upload_service import save_image
import os
from sqlite3 import DatabaseError

user_bp = Blueprint('user', __name__)

@user_bp.route('/admin/user')
def admin_user():
    users = User.query.all()
    return render_template('backend/admin/pages/user/user.html', users=users)

@user_bp.route('/admin/user/add', methods=['GET', 'POST'])
def admin_user_add():
    form = UserForm()
    filename = ""
    if form.validate_on_submit():
        if form.image.data:
            filename = save_image(form.image.data, current_app.config['UPLOAD_FOLDER'],
                                  current_app.config['ALLOWED_EXTENSIONS'])
        user = User(
            image=str(filename),
            username=form.username.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        db.session.close()
        flash('User has been added successfully!', 'success')
        return redirect(url_for('user.admin_user'))
    return render_template('backend/admin/pages/user/add.html', form=form)

@user_bp.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_user_edit(user_id):
    form = UserFormEdit()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        if form.image.data:
            if user.image and user.image != 'none.jpg':
                old_file_path = os.path.join(current_app.root_path, 'static/images', user.image)
                # Add resized/thumb removal logic if needed, similar to category
                if os.path.exists(old_file_path):
                     try:
                        os.remove(old_file_path)
                     except OSError:
                        pass

            user.image = save_image(form.image.data, current_app.config.get('UPLOAD_FOLDER'),
                                    current_app.config['ALLOWED_EXTENSIONS'])

        if user:
            user.username = form.username.data.strip()
            user.password = generate_password_hash(form.password.data.strip())
            db.session.commit()
            db.session.close()
            flash('User has been updated successfully!', 'success')
            return redirect(url_for('user.admin_user'))
            
    user = User.query.get_or_404(user_id)
    form.username.data = user.username
    # form.password.data = user.password # Typically don't pre-fill password hash
    return render_template('backend/admin/pages/user/edit.html', user=user, form=form, os=os)

@user_bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
def admin_user_delete(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if user.image and user.image != 'none.jpg':
             old_file_path = os.path.join(current_app.root_path, 'static/images', user.image)
             if os.path.exists(old_file_path):
                 try:
                    os.remove(old_file_path)
                 except OSError:
                    pass
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted successfully!', 'success')
        return redirect(url_for('user.admin_user'))
    except(ValueError, TypeError, Exception, DatabaseError):
        db.session.rollback()
        return redirect(url_for('user.admin_user'))
