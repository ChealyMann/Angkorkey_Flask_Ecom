from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class PromotionForm(FlaskForm):
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    title = StringField('Title', validators=[Length(min=2, max=100)])
    subtitle = StringField('Subtitle', validators=[Length(min=2, max=255)])
    link = StringField('Link', validators=[Length(min=2, max=255)])
    button_text = StringField('Button Text', validators=[Length(min=2, max=50)])
    is_active = BooleanField('Active', default="checked")
    submit = SubmitField('Add Promotion')

class PromotionFormEdit(FlaskForm):
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')]) # Optional on edit
    title = StringField('Title', validators=[Length(min=2, max=100)])
    subtitle = StringField('Subtitle', validators=[Length(min=2, max=255)])
    link = StringField('Link', validators=[Length(min=2, max=255)])
    button_text = StringField('Button Text', validators=[Length(min=2, max=50)])
    is_active = BooleanField('Active')
    submit = SubmitField('Update Promotion')
