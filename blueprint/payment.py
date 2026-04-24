import os
from bakong_khqr import KHQR
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from extensions import db
from models.Order import Order

payment_bp = Blueprint('payment', __name__)

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiNGQyN2MwZjE2MzFjNDA2YyJ9LCJpYXQiOjE3NzY3NzAxNDgsImV4cCI6MTc4NDU0NjE0OH0.2im6bNiNJqMpdS04p5At9HOgeKGN-P4w-zTB_cICf4k"


@payment_bp.route('/payment/<float:amount>/<string:currency>/<string:bill_number>')
def payment(amount, currency, bill_number):
    khqr = KHQR(TOKEN)

    qr_string = khqr.create_qr(
        bank_account='mann_chealy@bkrt',
        merchant_name='Angkorkey',
        merchant_city='PhnomPenh',
        bill_number=bill_number,
        currency='KHR',
        store_label='Angkorkey',
        phone_number='0964246058',
        amount=100,
        expiration=2
    )

    image_filename = f'{bill_number}_bakong_qr.png'
    image_path = os.path.join('static', image_filename)

    khqr.qr_image(qr=qr_string, output_path=image_path, format='png')

    return render_template(
        'frontend/pages/payment.html',
        qr_filename=image_filename,
        qr_string=qr_string,
        bill_number=bill_number
    )


@payment_bp.route('/check_payment')
def check_payment():
    qr          = request.args.get('qrcode')
    bill_number = request.args.get('bill_number')

    if not qr:
        return jsonify({"status": "ERROR", "message": "Missing qrcode"}), 400

    try:
        khqr = KHQR(TOKEN)
        md5  = khqr.generate_md5(qr)
        payment_status = khqr.check_payment(md5)

        # ── When PAID: mark the order as paid and confirm it ──────────────
        if payment_status == "PAID" and bill_number:
            order = Order.query.filter_by(invoice_no=bill_number).first()
            if order:
                order.payment_status = 'paid'
                order.status = 2          # e.g. 2 = confirmed / processing
                db.session.commit()

        return jsonify({"status": payment_status})

    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@payment_bp.route('/payment/success')
def payment_success():
    """
    Optional: render a success page.
    bill_number is forwarded from the frontend redirect so you can
    display order details.
    """
    bill_number = request.args.get('bill_number', '')
    order = None
    if bill_number:
        order = Order.query.filter_by(invoice_no=bill_number).first()

    return render_template(
        'frontend/pages/payment_success.html',
        order=order
    )