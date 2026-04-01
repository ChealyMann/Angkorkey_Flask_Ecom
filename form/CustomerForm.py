from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, Optional


# ==============================
# ADD CUSTOMER FORM
# ==============================
class CustomerForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[
            DataRequired(message='Please enter customer name!'),
            Length(1, 50)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Please enter email!'),
            Email(message='Invalid email format!')
        ]
    )

    phone = StringField(
        'Phone',
        validators=[
            DataRequired(message='Please enter phone number!'),
            Length(min=8, max=15),
            Regexp(r'^\d+$', message='Phone must contain only numbers')
        ]
    )

    address = TextAreaField(
        'Address',
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            Length(min=3, message='Password must be at least 8 characters')
        ]
    )

    submit = SubmitField('Submit')


# ==============================
# EDIT CUSTOMER FORM
# ==============================
class CustomerFormEdit(FlaskForm):
    name = StringField(
        'Name',
        validators=[
            DataRequired(message='Please enter customer name!'),
            Length(1, 50)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Please enter email!'),
            Email(message='Invalid email format!')
        ]
    )

    phone = StringField(
        'Phone',
        validators=[
            DataRequired(message='Please enter phone number!'),
            Length(min=8, max=15),
            Regexp(r'^\d+$', message='Phone must contain only numbers')
        ]
    )

    address = TextAreaField(
        'Address',
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            Optional(),
            Length(min=3, message='Password must be at least 8 characters')
        ]
    )

    submit = SubmitField('Update')