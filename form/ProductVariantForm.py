from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SelectField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField

from models import Product


def get_products():
     return Product.query.all()

class ProductVariantForm(FlaskForm):
    # Link to the parent product
    product_id = QuerySelectField('Product ID', query_factory= get_products,
                                  get_label='name',
                                  validators=[DataRequired()])

    sku = StringField('SKU', validators=[Optional()])
    color = StringField('Color', validators=[DataRequired()])
    type = StringField('Type/Size', validators=[DataRequired()])

    price = DecimalField('Price', validators=[DataRequired()])

    purchase_cost = DecimalField(
        'Purchase Cost',
        validators=[Optional(), NumberRange(min=0)],
        default=Decimal('0.00'),
        places=2
    )

    discount_price = DecimalField(
        'Discount Price',
        validators=[Optional(), NumberRange(min=0, message="Price cannot be negative")]
    )
    physical_stock = IntegerField('Physical Stock', validators=[Optional()])

    # For the variant image upload (maps to ProductImage relationship logic in your route)
    image = FileField('Variant Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'webp', 'jpeg'], 'Images only!')
    ])


    submit = SubmitField('Submit')
