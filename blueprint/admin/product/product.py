import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from sqlalchemy import false
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from form.ProductForm import ProductForm, ProductFormEdit, ProductImageAdd
from form.ProductVariantForm import ProductVariantForm
from functions.functions import product_variant_images
from models import Product, ProductImage, ProductVariant
from models.Product import getAllProduct  # <--- Import function ដែលយើងសរសេរពីមុន
from extensions import db
from Webp import save_picture

from upload_service import save_image

product_bp = Blueprint('product', __name__)


@product_bp.route('/admin/product')
def product():
    output = []
    products = getAllProduct()
    _products = Product.query.all()

    for _product in _products:
        output.append({
            'id': _product.id,
            'name': _product.name,
            'desc': _product.desc,
            'price': _product.price,
            'cost': _product.cost,
            'category_id': _product.category_id,
            'image': _product.image,
        })

    return render_template('backend/admin/pages/product/product.html', products=products, product=product,
                           output=output, os=os)


@product_bp.route('/admin/product/add', methods=['GET', 'POST'])
def product_add():
    form = ProductForm()
    if form.validate_on_submit():
        unique_filename = 'none.jpg'  # Default Image
        if form.image.data:
            unique_filename = save_image(form.image.data,
                                         current_app.config.get('UPLOAD_FOLDER'),
                                         current_app.config['ALLOWED_EXTENSIONS'])
        _product = Product(
            name=form.name.data,
            desc=form.desc.data,
            price=form.price.data,
            old_price=form.old_price.data,
            image=str(unique_filename),
            cost=form.cost.data,
            status=form.status.data,
            category_id=form.category.data.id,
        )
        db.session.add(_product)
        db.session.commit()

        flash('Product Added Successfully', 'success')
        return redirect(url_for('product.product'))

    return render_template('backend/admin/pages/product/add.html', form=form)


@product_bp.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def product_edit(product_id):
    _product = Product.query.get_or_404(product_id)
    form = ProductFormEdit()

    # Handle POST Request
    if form.validate_on_submit():
        _product.name = form.name.data
        _product.desc = form.desc.data
        _product.price = form.price.data
        _product.old_price = form.old_price.data
        _product.cost = form.cost.data
        _product.status = form.status.data
        _product.category_id = form.category.data.id

        if form.image.data:

            if _product.image and _product.image != 'none.jpg':
                old_file_path = os.path.join(current_app.root_path, 'static/images', _product.image)
                old_file_path_resized = os.path.join(current_app.root_path, 'static/images',
                                                     'resized_' + _product.image)
                old_file_path_thumb = os.path.join(current_app.root_path, 'static/images', 'thumb_' + _product.image)
                if os.path.exists(old_file_path or old_file_path_thumb or old_file_path_resized):
                    os.remove(old_file_path)
                    os.remove(old_file_path_resized)
                    os.remove(old_file_path_thumb)

            _product.image = save_image(form.image.data, current_app.config.get('UPLOAD_FOLDER'),
                                        current_app.config['ALLOWED_EXTENSIONS'])

        db.session.commit()
        flash('Product Updated Successfully', 'success')  # <--- ដូរ Message
        return redirect(url_for('product.product'))

    # Handle GET Request (Populate Form)
    if request.method == 'GET':
        form.name.data = _product.name
        form.desc.data = _product.desc
        form.price.data = _product.price
        form.old_price.data = _product.old_price
        form.cost.data = _product.cost
        form.status.data = _product.status
        form.category.data = _product.category_id  # Note: ត្រូវប្រាកដថា form field នេះទទួលយក ID

    return render_template('backend/admin/pages/product/edit.html', form=form, product=_product, os=os)


@product_bp.route('/admin/product/delete/<int:product_id>', methods=['POST'])
def product_delete(product_id):
    _product = Product.query.get_or_404(product_id)

    # ⚠️ Safe Delete Image Logic
    if _product.image and _product.image != 'none.jpg':
        file_path = os.path.join(current_app.root_path, 'static/images', _product.image)
        file_path_resized = os.path.join(current_app.root_path, 'static/images', 'resized_' + _product.image)
        file_path_thumb = os.path.join(current_app.root_path, 'static/images', 'thumb_' + _product.image)
        if os.path.exists(file_path or file_path_resized or file_path_thumb):
            try:
                os.remove(file_path)
                os.remove(file_path_resized)
                os.remove(file_path_thumb)
                print(f"Deleted image: {_product.image}")
            except Exception as e:
                print(f"Error deleting image: {e}")

    db.session.delete(_product)
    db.session.commit()
    flash('Product Deleted Successfully', 'success')
    return redirect(url_for('product.product'))


# Route to handle adding multiple images to a specific product and variant
@product_bp.route('/admin/product/add_image/<int:product_id>/<int:variant_id>', methods=['GET', 'POST'])
def product_add_image(product_id, variant_id):
    form = ProductImageAdd()
    # Fetch the product by ID to ensure it exists; otherwise, return a 404 error
    # product_images = Product.query.get_or_404(product_id)
    product_images = product_variant_images(product_id, variant_id)

    # Check if the form was submitted and passed validation
    if form.validate_on_submit():
        # Validation: Ensure the user actually uploaded files
        if not form.images.data:
            flash(message='No images added', category='error')
            return redirect(url_for('product.product_add_image', product_id=product_id, variant_id=variant_id))

        # Process each uploaded file in the list
        for file in form.images.data:
            # Generate a secure, unique filename and save to storage
            unique_filename = save_picture(file)

            # Create a new database record linking the image to the product and variant
            images_db = ProductImage(
                product_id=product_id,
                variant_id=variant_id,
                image=str(unique_filename)
            )
            db.session.add(images_db)

        # Commit all changes to the database at once for better performance
        db.session.commit()
        flash(message='Images uploaded successfully!', category='success')
        return redirect(url_for('product.product'))

    else:
        # Log validation errors to the console for debugging
        if form.errors:
            print(f"Form Errors: {form.errors}")

    return render_template('backend/admin/pages/product/add_images.html', form=form, product=product_images,
                           variant_id=variant_id, product_id=product_id)


@product_bp.route('/admin/product/image/delete/<int:image_id>', methods=['POST'])
def product_image_delete(image_id):
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id

    # Delete physical files
    if image.image and image.image != 'none.jpg':
        file_path = os.path.join(current_app.root_path, 'static/images', image.image)
        file_path_resized = os.path.join(current_app.root_path, 'static/images', 'resized_' + image.image)
        file_path_thumb = os.path.join(current_app.root_path, 'static/images', 'thumb_' + image.image)

        for path in [file_path, file_path_resized, file_path_thumb]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error deleting file {path}: {e}")

    try:
        db.session.delete(image)
        db.session.commit()
        flash('Image Deleted Successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting image record: {e}")
        flash('Error deleting image', 'error')

    return redirect(url_for('product.product_add_image', product_id=product_id, variant_id=image.variant_id))


@product_bp.route('/admin/product/add_variant/<int:product_id>', methods=['GET', 'POST'])
def product_add_variant(product_id):
    # product_id for easy return back to listing page

    form = ProductVariantForm()
    form.product_id.data = Product.query.get_or_404(product_id)

    # happen only when user hit submit via post
    if form.validate_on_submit():
        product_variant = ProductVariant(
            product_id=product_id,
            sku=form.sku.data,
            price=form.price.data,
            discount_price=form.discount_price.data,
            physical_stock=form.physical_stock.data,
            reserved_stock=0,
            color=form.color.data,
            type=form.type.data,
        )

        db.session.add(product_variant)
        db.session.commit()

        flash('Product Added Successfully', 'success')
        return redirect(url_for('product.product'))

    return render_template('backend/admin/pages/product/product_add_variant.html', form=form, product_id=product_id)


@product_bp.route('/admin/product/edit_variant/<int:product_id>/<int:variant_id>', methods=['GET', 'POST'])
def product_edit_variant(product_id, variant_id):
    product_variant = ProductVariant.query.filter_by(product_id=product_id, id=variant_id).first()

    form = ProductVariantForm(obj=product_variant)
    form.product_id.data = product_variant.product

    if form.validate_on_submit():
        form.populate_obj(product_variant)
        product_variant.product_id = product_id
        db.session.commit()

        flash('Product Added Successfully', 'success')
        return redirect(url_for('product.product'))

    return render_template('backend/admin/pages/product/product_edit_variant.html', form=form,
                           product_variant=product_variant, product_id=product_id, variant_id=variant_id)

logger = logging.getLogger(__name__)
@product_bp.route('/admin/product/delete_variant/<int:product_id>/<int:variant_id>', methods=['POST'])
def product_delete_variant(product_id, variant_id):

    # 2. Use first_or_404 — returns proper 404 instead of silent failure
    product_variant = ProductVariant.query.filter_by(
        product_id=product_id, id=variant_id
    ).first_or_404()

    # 3. Collect file paths BEFORE touching the DB
    files_to_delete = []
    if product_variant.images:
        for variant_image in product_variant.images:
            file_path = os.path.join(current_app.root_path, 'static/images', product_variant.image)
            files_to_delete.append(file_path)
            db.session.delete(variant_image)  # stage deletions, don't commit yet

    db.session.delete(product_variant)

    # 4. Single commit wrapping all DB changes atomically
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error("Failed to delete variant %s for product %s: %s", variant_id, product_id, e)
        flash('An error occurred while deleting the variant.', 'danger')
        return redirect(url_for('product.product_variant', product_id=product_id))

    # 5. Only delete files AFTER DB commit succeeds
    for file_path in files_to_delete:
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as e:
                # Log but don't abort — DB is already consistent
                logger.warning("Could not delete file %s: %s", file_path, e)

    flash('Variant deleted successfully.', 'success')
    # 6. Fixed url_for — no .html suffix
    return redirect(url_for('product.product_variant', product_id=product_id))


@product_bp.route('/admin/product/variant/<int:product_id>')
def product_variants(product_id):
    output = []

    _variants = ProductVariant.query.filter_by(product_id=product_id).all()

    if _variants:
        for _variant in _variants:
            output.append({
                'id': _variant.id,
                'sku': _variant.sku,
                'name': _variant.product.name,
                'color': _variant.color,
                'type': _variant.type,
                'price': _variant.price,
                'discount': _variant.discount_price,
                'physical_stock': _variant.physical_stock,
            })

    return render_template('backend/admin/pages/product/product_variant.html',
                           output=output, os=os, product_id=product_id)
