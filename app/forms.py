from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, BooleanField, SelectMultipleField, \
    TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Required, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class RecipeForm(Form):
    name = StringField('name', validators=[DataRequired()])
    ingredients = TextAreaField('ingredients', validators=[DataRequired()])
    instructions = TextAreaField('instructions', validators=[DataRequired()])
    sources = TextAreaField('sources')
    tags = TextAreaField('tags')
    recipes = TextAreaField('recipes')


class CommentForm(Form):
    comment = TextAreaField('comment', validators=[DataRequired()])

class DeleteCommentForm(Form):
    id = StringField('id', validators=[DataRequired()])

class LogoutForm(Form):
    pass

class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])

class DeleteRecipeForm(Form):
    id = StringField('id', validators=[DataRequired()])

class UpdatePasswordForm(Form):
    password = PasswordField('Password', validators=[
        Length(min=6),
        Required(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat password')
