from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import IntegerField
from wtforms.fields.simple import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class UserForm(FlaskForm):
    username = StringField('Name',
                           validators=[DataRequired(message='Please enter the category name !'), Length(1, 25), ])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    password = PasswordField('Password', validators=[DataRequired(message='Please enter the password !'), Length(8)])
    submit = SubmitField('Submit')


class UserFormEdit(FlaskForm):
    username = StringField('Name',
                           validators=[DataRequired(message='Please enter the category name !'), Length(1, 25), ])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Please enter your username'),
        Length(min=1, max=25)
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter your password'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    submit = SubmitField('Sign In')


# Registration Form (Standard extras added)
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=1, max=25)
    ])
    phone = StringField('Phone Number',
                        validators=[DataRequired(message='Please enter your phone number'),
                                    Length(min=8, max=12),
                                    Regexp(r'^\d+$', message="Must contain only numbers")])

    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=8)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')
