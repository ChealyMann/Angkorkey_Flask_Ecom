from flask import Blueprint, render_template, redirect, url_for

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def _admin():
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/dashboard')
def admin():
    return render_template('backend/admin/index.html')
