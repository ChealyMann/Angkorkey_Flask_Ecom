from flask_wtf.file import FileRequired, FileAllowed, FileField, MultipleFileField
from wtforms import Form, validators, SelectField, FloatField
from wtforms.fields.simple import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf import  FlaskForm

from models import Category


class ProductForm(FlaskForm):
    name = StringField('product_name',validators=[DataRequired(message='Please enter Product Name'),Length(min=1,max=50)] )
    image = FileField('image',validators=([FileAllowed(['jpg','png','jpeg'],'jpg,png,jpeg')]))
    category = QuerySelectField('category',query_factory=lambda: Category.query.all(),get_label='name',default=lambda: Category.query.first())
    desc = TextAreaField('desc')
    price = FloatField('price',validators=[NumberRange(min=0)])
    old_price = FloatField('old_price',validators=[NumberRange(min=0)])
    cost = FloatField('cost',validators=[NumberRange(min=0)])
    status = SelectField('status',choices =
                         [
                             ('true','Active'),
                             ('false','Inactive'),
                         ],default='true')
    submit = SubmitField('Submit')


class ProductFormEdit(FlaskForm):
    name = StringField('product_name',validators=[Length(min=1,max=50)] )
    image = FileField('image',validators=([FileAllowed(['jpg','png','jpeg'],'jpg,png,jpeg')]))
    category = QuerySelectField('category',query_factory=lambda: Category.query.all(),get_label='name',default=lambda: Category.query.first())
    desc = TextAreaField('desc')
    price = FloatField('price',validators=[NumberRange(min=0)])
    old_price = FloatField('old_price',validators=[NumberRange(min=0)])
    cost = FloatField('cost',validators=[NumberRange(min=0)])
    status = SelectField('status',choices =
                         [
                             ('true','Active'),
                             ('false','Inactive'),
                         ],default='true')
    submit = SubmitField('Submit')


class ProductImageAdd(FlaskForm):
    images = MultipleFileField('images',validators=([FileAllowed(['jpg','png','jpeg'],'jpg,png,jpeg')]))
    submit = SubmitField('Submit')