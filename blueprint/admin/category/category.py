import os
from sqlite3 import DatabaseError
from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from extensions import db
from form.CategoryForm import CategoryForm
from models import Category
from upload_service import save_image

category_bp = Blueprint('category', __name__)

@category_bp.route('/admin/category')
def admin_category():
    categories = Category.query.all()
    return render_template('backend/admin/pages/category/category.html', categories=categories)


@category_bp.route('/admin/category/add', methods=['GET', 'POST'])
def admin_category_add():
    form = CategoryForm()
    filename = ""
    if form.validate_on_submit():
        if form.image.data:
            filename = save_image(form.image.data, current_app.config['UPLOAD_FOLDER'],
                                  current_app.config['ALLOWED_EXTENSIONS'])
        category = Category(
            image=str(filename),
            name=form.name.data,
            desc=form.desc.data,
            status=form.status.data
        )
        db.session.add(category)
        db.session.commit()
        db.session.close()
        flash('Category has been added successfully!', 'success')
        return redirect(url_for('category.admin_category'))

    return render_template(
        'backend/admin/pages/category/add.html', form=form)


@category_bp.route('/admin/category/edit/<int:category_id>', methods=['GET', 'POST'])
def admin_category_edit(category_id):
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category.query.get_or_404(category_id)
        if form.image.data:
            if category.image and category.image != 'none.jpg':
                old_file_path = os.path.join(current_app.root_path, 'static/images', category.image)
                old_file_path_resized = os.path.join(current_app.root_path, 'static/images', 'resized_' + category.image)
                old_file_path_thumb = os.path.join(current_app.root_path, 'static/images', 'thumb_' + category.image)
                if os.path.exists(old_file_path or old_file_path_thumb or old_file_path_resized):
                    try:
                        os.remove(old_file_path)
                        os.remove(old_file_path_resized)
                        os.remove(old_file_path_thumb)
                    except OSError:
                        pass # Ignore if file doesn't exist

            category.image = save_image(form.image.data, current_app.config.get('UPLOAD_FOLDER'),
                                        current_app.config['ALLOWED_EXTENSIONS'])

        if category:
            category.name = form.name.data.strip()
            category.desc = form.desc.data.strip()
            category.status = form.status.data.strip()
            db.session.commit()
            flash('Category has been updated successfully!', 'success')
            return redirect(url_for('category.admin_category'))
            
    category = Category.query.get_or_404(category_id)
    form.desc.data = category.desc
    form.name.data = category.name
    form.status.data = category.status
    return render_template('backend/admin/pages/category/edit.html', category=category, form=form, os=os)


@category_bp.route('/admin/category/delete/<int:category_id>', methods=['POST'])
def admin_category_delete(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        flash('Category has been deleted successfully!', 'success')
        return redirect(url_for('category.admin_category'))
    except(ValueError, TypeError, Exception, DatabaseError) as e:
        db.session.rollback()
        print(e)
        flash('Error deleting category', 'danger')
        return redirect(url_for('category.admin_category'))
