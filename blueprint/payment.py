import os

from bakong_khqr import KHQR
from flask import Blueprint, render_template

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/payment/<float:amount>/<string:currency>/<string:bill_number>')
def payment(amount, currency, bill_number):
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkljoiYjc3Y2EyOWY5YzdlNDJhNiJ9LCJpYXQiOjE3NzUyMDQ5OTYslmV4cCI6MTc4Mjk4MDk5Nn0.BBFqs0iDpERORoZTqK91YEGeBOeYfvnibZiwlgpTHzs"
    khqr = KHQR(token)

    qr_string = khqr.create_qr(
        bank_account='choeurn_pinchai@aclb',
        merchant_name='choeurn_pinchai',
        merchant_city='PhnomPenh',
        bill_number=bill_number,
        currency=currency,
        store_label='Angkorkey',
        phone_number='0964246058',
        amount=amount,
        expiration=2
    )

    image_filename = f'{bill_number}bakong_static_qr.png'
    image_path = os.path.join('static', image_filename)

    khqr.qr_image(qr=qr_string, output_path=image_path, format='png')
    khqr.qr_image(qr=qr_string, output_path=image_path, format='png')

    return render_template('frontend/pages/payment.html', qr_filename=image_filename)
